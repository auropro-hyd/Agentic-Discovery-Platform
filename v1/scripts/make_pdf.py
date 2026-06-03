#!/usr/bin/env python3
"""Render a generated report suite (out/<domain>/) to print-quality PDFs.

Each report is a STANDALONE deliverable — its own cover, its own table of contents, numbered
sections. The print chrome (full-bleed cover, running brand line, page numbers, Confidential footer)
is all in the report's print stylesheet via CSS @page margin boxes — which render reliably in
headless Chrome. So this prints each report to PDF with Chrome's own default header/footer
SUPPRESSED (--no-pdf-header-footer).

By default it also stitches the seven reports, in suite order, into one combined PDF (each report
paginating from its own cover). `--per-report` instead writes one PDF per report into a folder.

Usage:
    uv run python scripts/make_pdf.py --domain o2c                 # combined out/o2c-report.pdf
    uv run python scripts/make_pdf.py --domain o2c --per-report    # one PDF per report -> out/o2c-pdf/
    uv run python scripts/make_pdf.py --domain o2c --out /tmp/x.pdf

Uses headless Chrome (the usual macOS path or $CHROME) + pypdf to stitch. Without pypdf it writes
the per-report PDFs into a folder and tells you.
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
SECTIONS = ["00-executive-summary", "01-current-state", "02-pain-points", "03-recommendation",
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


def _print_each(domain: str, dest_dir: Path) -> list[Path]:
    """Print every report in the suite to its own PDF (each standalone, own cover→TOC→body)."""
    suite = ROOT / "out" / domain
    if not (suite / "00-executive-summary.html").exists():
        sys.exit(f"error: no suite at {suite} — run `python run.py --domain {domain}` first.")
    chrome = _chrome()
    dest_dir.mkdir(parents=True, exist_ok=True)
    parts = []
    # all chrome (cover, running brand line, page numbers, Confidential) is in the print CSS;
    # suppress Chrome's OWN default header/footer so only our @page margin boxes show.
    for i, name in enumerate(SECTIONS):
        src = suite / f"{name}.html"
        if not src.exists():
            continue
        dst = dest_dir / f"{i:02d}-{name}.pdf"
        cmd = [chrome, "--headless=new", "--disable-gpu", "--no-sandbox",
               "--no-pdf-header-footer", f"--print-to-pdf={dst}", src.as_uri()]
        subprocess.run(cmd, check=True, capture_output=True)
        parts.append(dst)
    return parts


def render(domain: str, out_path: Path, per_report: bool) -> int:
    if per_report:
        dest_dir = ROOT / "out" / f"{domain}-pdf"
        parts = _print_each(domain, dest_dir)
        print(f"wrote {len(parts)} standalone report PDFs to {dest_dir}")
        return 0
    tmp = Path(tempfile.mkdtemp())
    parts = _print_each(domain, tmp)
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
            print(f"per-report PDFs written to {dest_dir} (install 'pypdf' to merge into one file)")
            return 0
    w = PdfWriter()
    for p in parts:
        w.append(str(p))
    out_path.parent.mkdir(parents=True, exist_ok=True)
    with out_path.open("wb") as fh:
        w.write(fh)
    print(f"wrote {out_path} ({out_path.stat().st_size // 1024} KB, {len(parts)} reports)")
    return 0


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description="Render a report suite to print-quality PDF(s)")
    ap.add_argument("--domain", required=True)
    ap.add_argument("--per-report", action="store_true",
                    help="write one standalone PDF per report (default: one combined PDF)")
    ap.add_argument("--out", default=None, help="output PDF path (default: out/<domain>-report.pdf)")
    args = ap.parse_args(argv)
    out = Path(args.out) if args.out else ROOT / "out" / f"{args.domain}-report.pdf"
    return render(args.domain, out, args.per_report)


if __name__ == "__main__":
    raise SystemExit(main())
