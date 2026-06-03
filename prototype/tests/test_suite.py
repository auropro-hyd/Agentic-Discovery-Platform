"""PR-B: the 6-report suite — grounding, factual Report 01, dependency invariant, no leaks,
no TSA count, renders to 6 files.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from discovery import docnames, registry, synthesis  # noqa: E402
from discovery.agent_loop import GroundingError  # noqa: E402
from discovery.reportsuite import build  # noqa: E402
from discovery.reportsuite.render import REPORTS, render_suite, _strip_tags, r01  # noqa: E402

DOMAIN = ROOT / "inputs" / "o2c"


@pytest.fixture(scope="module")
def raw_payload():
    p = ROOT / "out" / "discovery-o2c.json"
    if not p.exists():
        pytest.skip("run `python run.py --domain o2c --golden` first to produce findings")
    return json.load(open(p))["internal_trace"]


@pytest.fixture(scope="module", autouse=True)
def _setup():
    registry.setup_domain(DOMAIN, freeze=True)
    yield


def test_fixture_is_grounded(raw_payload):
    allow = synthesis.allowed_numbers(raw_payload)
    content = build.fixture_o2c()
    synthesis.validate_synthesis(content.to_dict(), allow, set(docnames.DOC_META))  # must not raise


def test_dependency_invariant(raw_payload):
    content = build.build_synthesis(raw_payload, live=False)
    deps = {o.id: set(o.dependencies) for o in content.opportunities}
    assert not deps["OPP1"]
    assert not (deps["OPP2"] & {"OPP1", "OPP3"})
    assert deps["OPP3"] == {"OPP1"}
    # derived inverse link
    opp1 = next(o for o in content.opportunities if o.id == "OPP1")
    assert "OPP3" in opp1.prerequisite_for


def test_pp_opp_links(raw_payload):
    content = build.build_synthesis(raw_payload, live=False)
    pp = {p.id: p.opportunity_signal for p in content.pain_points}
    assert pp == {"PP1": "OPP1", "PP2": "OPP3", "PP3": "OPP2"}


def test_report01_is_factual():
    content = build.fixture_o2c()
    text = _strip_tags(r01(content, {"client": "the organisation", "domain_label": "Order-to-Cash"}))
    synthesis.assert_factual(text)  # must not raise — no diagnostic words in Report 01


def test_suite_renders_six_files_no_leaks(raw_payload, tmp_path):
    content = build.build_synthesis(raw_payload, live=False)
    out = tmp_path / "o2c"
    render_suite(content, {"client": "the organisation", "domain_label": "Order-to-Cash"}, out)
    for slug, _ in REPORTS:
        assert (out / f"{slug}.html").exists()
    assert (out / "index.html").exists()
    # no TSA count fabrication anywhere (D2)
    blob = "\n".join((out / f"{slug}.html").read_text() for slug, _ in REPORTS)
    assert "6 of 14" not in blob and "14 connections" not in blob


def test_no_new_numbers_in_fixture(raw_payload):
    """Every NumberRef in the fixture must trace to the findings allow-list."""
    allow = synthesis.allowed_numbers(raw_payload)
    content = build.fixture_o2c()

    def walk(o):
        if isinstance(o, dict):
            if {"value", "unit", "text"} <= set(o):
                assert synthesis._num_ok(o["value"], allow), f"untraceable {o['value']}"
            for v in o.values():
                walk(v)
        elif isinstance(o, list):
            for x in o:
                walk(x)
    walk(content.to_dict())


def test_fixture_has_consultant_depth():
    """Lock in the consultant-grade depth: per-system narrative profiles, a format taxonomy, the
    three readiness ratings + operating-model fields per opportunity, and a metrics framework.
    A regression that strips any of these (back to the thin original) fails here."""
    c = build.fixture_o2c()
    assert len(c.current_state.system_profiles) >= 3
    assert all(p.name and p.how_used and p.limitations for p in c.current_state.system_profiles)
    assert len(c.current_state.format_taxonomy) >= 2
    assert len(c.metrics_framework) >= 4
    assert all(m.name and m.definition and m.target for m in c.metrics_framework)
    for o in c.opportunities:
        assert o.personas, f"{o.id} has no personas"
        assert o.expected_behaviour and o.escalation, f"{o.id} missing operating model"
        for dim in (o.data_readiness, o.technical_complexity, o.operational_readiness):
            assert dim.split("—")[0].strip().lower() in ("high", "medium", "low"), \
                f"{o.id} readiness must start high|medium|low: {dim!r}"


def test_depth_renders_into_html(raw_payload, tmp_path):
    """The depth fields must actually surface in the rendered HTML (not silently dropped)."""
    content = build.build_synthesis(raw_payload, live=False)
    out = tmp_path / "o2c"
    render_suite(content, {"client": "the organisation", "domain_label": "Order-to-Cash"}, out)
    r01h = (out / "01-current-state.html").read_text()
    r03h = (out / "03-recommendation.html").read_text()
    r04h = (out / "04-opportunity-portfolio.html").read_text()
    r06h = (out / "06-supporting-artefacts.html").read_text()
    assert "Systems &amp; sources" in r01h and "Information format" in r01h
    assert "Prioritization rationale" in r03h and "rate-high" in r03h
    assert "Who uses it" in r04h and "Escalation" in r04h
    assert "Success metrics framework" in r06h
