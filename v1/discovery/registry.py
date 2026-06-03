"""Populate the tool FILE_REGISTRY (CSVs) and DOC_TEXT (frozen narrative text).

CSV files are exposed to the CSV tools by logical id (filename stem). PDF/TXT narrative docs
are extracted ONCE to committed `inputs/<domain>/pdftext/<id>.txt` sidecars; find_mentions and
the agent's system prompt read those sidecars, never the live PDF — so text is byte-stable and
auditable. Re-extraction is asserted identical to the frozen sidecar (Gate B).
"""
from __future__ import annotations

from pathlib import Path

from . import tools

CSV_SUFFIX = ".csv"
NARRATIVE_SUFFIXES = {".pdf", ".txt", ".md"}

# Business-friendly names live in docnames.py (single source of truth). DOC_META kept as an
# alias for any code that imported it from here.
from .docnames import DOC_META  # noqa: E402,F401


def setup_domain(domain_dir: Path, *, freeze: bool = True) -> dict:
    """Wire FILE_REGISTRY + DOC_TEXT for a domain folder. Returns a small manifest."""
    tools.FILE_REGISTRY.clear()
    tools.DOC_TEXT.clear()
    sidecar_dir = domain_dir / "pdftext"
    sidecar_dir.mkdir(exist_ok=True)

    csv_ids, doc_ids = [], []
    for path in sorted(domain_dir.iterdir()):
        if path.name.startswith(("_", ".")) or path.is_dir():
            continue
        stem = path.stem
        if path.suffix.lower() == CSV_SUFFIX:
            tools.FILE_REGISTRY[stem] = path
            csv_ids.append(stem)
        elif path.suffix.lower() in NARRATIVE_SUFFIXES:
            text = _frozen_text(path, sidecar_dir, freeze=freeze)
            tools.DOC_TEXT[stem] = text
            doc_ids.append(stem)
    return {"csv_ids": sorted(csv_ids), "doc_ids": sorted(doc_ids),
            "sidecar_dir": str(sidecar_dir)}


def _frozen_text(path: Path, sidecar_dir: Path, *, freeze: bool) -> str:
    sidecar = sidecar_dir / f"{path.stem}.txt"
    if path.suffix.lower() in (".txt", ".md"):
        text = path.read_text(encoding="utf-8", errors="replace")
    else:  # pdf
        text = _extract_pdf(path)
        if freeze:
            # assert double-extraction is identical (determinism guard)
            if _extract_pdf(path) != text:
                raise RuntimeError(f"PDF extraction not stable for {path.name}")
    if freeze:
        sidecar.write_text(text, encoding="utf-8")
    elif sidecar.exists():
        text = sidecar.read_text(encoding="utf-8")
    return text


def _extract_pdf(path: Path) -> str:
    from pypdf import PdfReader
    reader = PdfReader(str(path))
    return "\n".join((page.extract_text() or "") for page in reader.pages)
