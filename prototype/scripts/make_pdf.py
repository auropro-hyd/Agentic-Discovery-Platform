#!/usr/bin/env python3
"""Render a generated report suite (out/<domain>/) to a single, print-quality PDF.

Why a separate step: the suite is HTML-first (screen), and a reliable running header/footer with
page numbers across a multi-page PDF needs the browser's NATIVE margin boxes — CSS position:fixed
repeats unreliably in print and collides with headings. So we drive headless Chrome with
--header-template / --footer-template here, where it is supported, and concatenate the sections in
suite order (cover + TOC come from the index page; then 01..06).

Usage:
    uv run python scripts/make_pdf.py --domain o2c
    uv run python scripts/make_pdf.py --domain o2c --out /tmp/o2c-report.pdf

No new dependencies: uses headless Chrome (found at the usual macOS path or $CHROME) and the stdlib
to stitch the per-page PDFs. If a PDF-merge lib (pypdf) is present it produces one file; otherwise
it writes the per-section PDFs into a folder and tells you.
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

# native running header/footer templates (Chrome injects page numbers via the classes below)
_HEADER = ("<div style='font-size:8px;color:#5b6776;width:100%;padding:0 14mm;"
           "display:flex;justify-content:space-between;'>"
           "<span>{title}</span><span>AuroPro · Autonomous Discovery Platform</span></div>")
_FOOTER = ("<div style='font-size:8px;color:#5b6776;width:100%;padding:0 14mm;"
           "display:flex;justify-content:space-between;'>"
           "<span>Confidential</span>"
           "<span>Page <span class='pageNumber'></span> of <span class='totalPages'></span></span>"
           "</div>")


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
    title = f"{domain.upper()} Discovery Report"
    chrome = _chrome()
    tmp = Path(tempfile.mkdtemp())
    parts = []
    # the cover page (index) gets no running header/footer; the rest do
    for i, name in enumerate(SECTIONS):
        src = suite / f"{name}.html"
        if not src.exists():
            continue
        dst = tmp / f"{i:02d}-{name}.pdf"
        cmd = [chrome, "--headless=new", "--disable-gpu", "--no-sandbox",
               f"--print-to-pdf={dst}", src.as_uri()]
        if name == "index":
            cmd.insert(-1, "--no-pdf-header-footer")     # cover/TOC: clean, no running chrome
        else:
            cmd[-1:-1] = [f"--print-to-pdf-header-template={_HEADER.format(title=title)}",
                          f"--print-to-pdf-footer-template={_FOOTER}"]
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
