"""Shared test payloads: a depth-complete, fully-grounded emit_synthesis payload built from the
hand-grounded O2C fixture, plus the verified-number allow-list for it.

Building the live-shaped payload from the dataclasses keeps the test in lockstep with the fixture:
if the fixture deepens, this payload deepens with it, so the live-path test exercises the same
depth the renderer expects.
"""
from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from discovery.reportsuite.build import fixture_o2c  # noqa: E402


def _src(refs):
    return [{"doc_key": r.doc_id} for r in refs]


def _nums(refs):
    return [{"value": n.value, "unit": n.unit, "text": n.text, "label": n.label} for n in refs]


def _steps(steps):
    out = []
    for st in steps:
        d = {"seq": st.seq, "name": st.name, "actor": st.actor, "description": st.description}
        if st.system:
            d["system"] = st.system
        if st.failure_points:
            d["failure_points"] = list(st.failure_points)
        out.append(d)
    return out


def depth_synthesis_payload() -> dict:
    """A complete emit_synthesis payload (all depth fields populated), shaped exactly as the live
    model would emit it, derived from fixture_o2c() so every number is grounded."""
    s = fixture_o2c()
    cs = s.current_state
    return {
        "current_state": {
            "domain_overview": cs.domain_overview,
            "process_summary": cs.process_summary,
            "process_flow": _steps(cs.process_flow),
            "process_inventory": [{"name": i.name, "purpose": i.purpose}
                                  for i in cs.process_inventory],
            "ownership_map": [{"activity": r.activity, "responsible": r.responsible,
                               "accountable": r.accountable} for r in cs.ownership_map],
            "system_inventory": [{"name": i.name, "role": i.purpose,
                                  "system_of_record_for": i.system_of_record_for}
                                 for i in cs.system_inventory],
            "handoff_catalogue": [{"from_step": h.from_step, "to_step": h.to_step,
                                   "mechanism": h.mechanism} for h in cs.handoff_catalogue],
            "system_profiles": [p.to_dict() for p in cs.system_profiles],
            "format_taxonomy": [f.to_dict() for f in cs.format_taxonomy],
        },
        "pain_points": [{
            "id": p.id, "title": p.title, "impact_rank": p.impact_rank,
            "from_finding": p.from_finding, "description": p.description,
            "root_cause": p.root_cause, "failure_pattern": p.failure_pattern,
            "quantified": _nums(p.quantified), "sources": _src(p.sources),
        } for p in s.pain_points],
        "cross_process_patterns": s.cross_process_patterns,
        "opportunities": [{
            "id": o.id, "title": o.title, "pattern": o.pattern.value, "overview": o.overview,
            "before_process": _steps(o.before_process), "after_process": _steps(o.after_process),
            "business_impact": {"narrative": o.business_impact.narrative,
                                "quantified": _nums(o.business_impact.quantified),
                                "derivation": o.business_impact.derivation},
            "implementation_approach": o.implementation_approach,
            "required_integrations": list(o.required_integrations),
            "success_metrics": list(o.success_metrics), "dependencies": list(o.dependencies),
            "risks": list(o.risks), "value_rating": o.value_rating,
            "feasibility_rating": o.feasibility_rating, "value_score": o.value_score,
            "feasibility_score": o.feasibility_score, "matrix_quadrant": o.matrix_quadrant.value,
            "personas": list(o.personas), "expected_behaviour": o.expected_behaviour,
            "escalation": o.escalation, "data_readiness": o.data_readiness,
            "technical_complexity": o.technical_complexity,
            "operational_readiness": o.operational_readiness, "sources": _src(o.sources),
        } for o in s.opportunities],
        "transformation": {"sequencing_rationale": s.sequencing_rationale,
                           "strategic_readiness": s.strategic_readiness,
                           "dependency_notes": s.dependency_notes},
        "roadmap": [{"horizon": h.horizon, "window": h.window, "theme": h.theme,
                     "items": [{"title": it.title, "rationale": it.rationale,
                                **({"opportunity_id": it.opportunity_id} if it.opportunity_id
                                   else {})} for it in h.items]} for h in s.roadmap],
        "strategy_profile": s.strategy_profile,
        "metrics_framework": [m.to_dict() for m in s.metrics_framework],
    }


# Document keys the payload cites (the synthesis allow-list of doc_keys).
def depth_doc_keys() -> set[str]:
    keys: set[str] = set()

    def collect(o):
        if isinstance(o, dict):
            if "doc_key" in o:
                keys.add(o["doc_key"])
            for v in o.values():
                collect(v)
        elif isinstance(o, list):
            for x in o:
                collect(x)
    collect(depth_synthesis_payload())
    return keys


# The verified-number allow-list for the O2C fixture (the figures the findings actually computed,
# plus the factual current-state figures restated from the source documents — account populations,
# connection counts and per-account credit limits, all grounded in the CSVs/register).
O2C_VERIFIED = {267.0, 600000.0, 67.0, 5667.0, 8420.0, 1196.0, 12362493.74, 12.4,
                34.0, 2.4, 1.8, 2400000.0, 1800000.0,
                340.0, 318.0, 22.0, 14.0, 320.0, 111.0, 40.0,
                1100000.0, 1200000.0, 1000000.0, 950000.0, 850000.0, 800000.0, 750000.0,
                1400000.0, 1550000.0, 1350000.0, 1150000.0}


def o2c_allow() -> set[float]:
    allow = set(O2C_VERIFIED)
    allow |= {round(a / b * 100, 1) for a in list(allow) for b in list(allow) if b and a < b}
    return allow
