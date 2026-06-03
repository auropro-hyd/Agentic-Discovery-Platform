"""Load input documents from a domain folder into Document objects.

Keeps things dependency-light: md/txt/json/csv read natively; PDF text extracted with
pypdf if available, otherwise the file is skipped with a clear warning. CSVs are rendered
to a compact preview (header + first N rows + row count) so they fit in a prompt without
dumping thousands of rows.
"""
from __future__ import annotations

import csv as csv_mod
import io
import json
from pathlib import Path

from .models import Document, DocCategory

SUPPORTED = {".md", ".txt", ".json", ".csv", ".pdf"}
CSV_PREVIEW_ROWS = 25


def load_domain(domain_dir: Path) -> list[Document]:
    docs: list[Document] = []
    for path in sorted(domain_dir.iterdir()):
        if path.name.startswith(("_", ".")) or path.suffix.lower() not in SUPPORTED:
            continue
        text = _read_text(path)
        if text is None:
            print(f"  ! skipped (could not read): {path.name}")
            continue
        docs.append(Document(doc_id=path.name, path=str(path), text=text))
    return docs


def load_manifest(domain_dir: Path) -> dict | None:
    p = domain_dir / "_manifest.json"
    return json.loads(p.read_text()) if p.exists() else None


def load_resolutions(domain_dir: Path) -> dict:
    p = domain_dir / "_resolutions.json"
    return json.loads(p.read_text()) if p.exists() else {}


def _read_text(path: Path) -> str | None:
    suffix = path.suffix.lower()
    try:
        if suffix == ".csv":
            return _render_csv(path)
        if suffix == ".pdf":
            return _read_pdf(path)
        return path.read_text(encoding="utf-8", errors="replace")
    except Exception as e:  # pragma: no cover - defensive
        print(f"  ! error reading {path.name}: {e}")
        return None


def _render_csv(path: Path) -> str:
    raw = path.read_text(encoding="utf-8", errors="replace")
    reader = csv_mod.reader(io.StringIO(raw))
    rows = list(reader)
    if not rows:
        return "(empty csv)"
    header, body = rows[0], rows[1:]
    preview = body[:CSV_PREVIEW_ROWS]
    out = [f"CSV columns: {', '.join(header)}", f"Total data rows: {len(body)}", "",
           "Preview rows:"]
    out.append(", ".join(header))
    out.extend(", ".join(r) for r in preview)
    if len(body) > CSV_PREVIEW_ROWS:
        out.append(f"... ({len(body) - CSV_PREVIEW_ROWS} more rows)")
    return "\n".join(out)


def _read_pdf(path: Path) -> str | None:
    try:
        from pypdf import PdfReader
    except ImportError:
        print(f"  ! pypdf not installed; cannot read {path.name} (pip install pypdf)")
        return None
    reader = PdfReader(str(path))
    return "\n".join((page.extract_text() or "") for page in reader.pages)
