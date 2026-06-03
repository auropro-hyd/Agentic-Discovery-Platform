"""Offline test: the report suite renders clickable source pages and links citations to them."""
from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from discovery import registry  # noqa: E402
from discovery.reportsuite import build, render  # noqa: E402


def test_clickable_provenance(tmp_path):
    import os
    from discovery import docnames
    registry.setup_domain(ROOT / "inputs" / "o2c", freeze=True)
    content = build.fixture_o2c()
    build._apply_derived_links(content)
    # build the source index from the domain's documents (as run.py does)
    doc_ids = [docnames.stem(f) for f in os.listdir(ROOT / "inputs" / "o2c")
               if f.endswith((".csv", ".pdf", ".txt")) and not f.startswith(("_", "."))]
    content.source_index = build.build_source_index({"findings": []}, doc_ids)

    out = tmp_path / "o2c"
    render.render_suite(content, {"client": "", "domain_label": "Order-to-Cash"}, out,
                        suppress_names=["Opella"])

    # 1) a source page exists per indexed doc
    sdir = out / "sources"
    assert sdir.is_dir() and any(sdir.glob("*.html"))

    # 2) Report 06 links each document to its source page
    r06 = (out / "06-supporting-artefacts.html").read_text()
    assert "href='sources/" in r06

    # 3) pain-point citations are clickable links to source pages
    r02 = (out / "02-pain-points.html").read_text()
    assert "href='sources/" in r02

    # 4) source pages don't leak the suppressed client name
    blob = "\n".join(p.read_text() for p in sdir.glob("*.html"))
    assert "opella" not in blob.lower()
