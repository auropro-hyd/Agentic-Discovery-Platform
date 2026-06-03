#!/usr/bin/env python3
"""Render a generated report suite (out/<domain>/) to a single, print-quality PDF.

The suite is HTML-first; the print chrome (full-bleed cover, running brand line, page numbers,
Confidential footer) is all in the report's print stylesheet via CSS @page margin boxes — which
render reliably in headless Chrome. So this just prints each section to PDF with Chrome's own
default header/footer SUPPRESSED (--no-pdf-header-footer), then concatenates them in suite order
(the index carries the cover + TOC; then 01..06).

Usage:
    uv run python scripts/make_pdf.py --domain o2c
    uv run python scripts/make_pdf.py --domain o2c --out /tmp/o2c-report.pdf

Uses headless Chrome (the usual macOS path or $CHROME) + pypdf to stitch. Without pypdf it writes
the per-section PDFs into a folder and tells you.
"""
from __future__ import annotations

import argparse
import os
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SECTIONS = ["index", "01-current-state", "02-pain-points", "03-recommendation",
            "04-opportunity-portfolio", "05-roadmap", "06-supporting-artefacts"]


def _chrome() -> str:
    env = os.environ.get("CHROME")
    if env and Path(env).exists():
        return env
    for c in ("/Applications/Google Chrome.app/Contents/MacOS/Google Chrome",
              shutil.which("google-chrome"), shutil.which("chromium"),
              shutil.which("chromium-browser")):
        if c and Path(c).exists():
            return c
    sys.exit("error: Chrome/Chromium not found. Set $CHROME to the browser binary.")


def render(domain: str, out_path: Path) -> int:
    suite = ROOT / "out" / domain
    if not (suite / "index.html").exists():
        sys.exit(f"error: no suite at {suite} — run `python run.py --domain {domain}` first.")
    chrome = _chrome()
    tmp = Path(tempfile.mkdtemp())
    parts = []
    # all chrome (cover, running brand line, page numbers, Confidential) is in the print CSS;
    # suppress Chrome's OWN default header/footer so only our @page margin boxes show.
    for i, name in enumerate(SECTIONS):
        src = suite / f"{name}.html"
        if not src.exists():
            continue
        dst = tmp / f"{i:02d}-{name}.pdf"
        cmd = [chrome, "--headless=new", "--disable-gpu", "--no-sandbox",
               "--no-pdf-header-footer", f"--print-to-pdf={dst}", src.as_uri()]
        subprocess.run(cmd, check=True, capture_output=True)
        parts.append(dst)
    # stitch
    try:
        from pypdf import PdfWriter
    except ImportError:
        try:
            from PyPDF2 import PdfWriter  # type: ignore
        except ImportError:
            dest_dir = out_path.with_suffix("")
            dest_dir.mkdir(parents=True, exist_ok=True)
            for p in parts:
                shutil.copy(p, dest_dir / p.name)
            print(f"per-section PDFs written to {dest_dir} (install 'pypdf' to merge into one file)")
            return 0
    w = PdfWriter()
    for p in parts:
        w.append(str(p))
    out_path.parent.mkdir(parents=True, exist_ok=True)
    with out_path.open("wb") as fh:
        w.write(fh)
    print(f"wrote {out_path} ({out_path.stat().st_size // 1024} KB, {len(parts)} sections)")
    return 0


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description="Render a report suite to a print-quality PDF")
    ap.add_argument("--domain", required=True)
    ap.add_argument("--out", default=None, help="output PDF path (default: out/<domain>-report.pdf)")
    args = ap.parse_args(argv)
    out = Path(args.out) if args.out else ROOT / "out" / f"{args.domain}-report.pdf"
    return render(args.domain, out)


if __name__ == "__main__":
    raise SystemExit(main())
