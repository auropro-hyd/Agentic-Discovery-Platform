import os, sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from generators.pdf_utils import OpellaDoc
import pytest

def test_create_document_produces_file(tmp_path):
    doc = OpellaDoc(title="Test Document", subtitle="Opella Europe", classification="INTERNAL")
    doc.add_section("1. Overview", "This is the overview section body text.")
    out = tmp_path / "test.pdf"
    doc.save(str(out))
    assert out.exists()
    assert out.stat().st_size > 1000

def test_document_without_content_still_saves(tmp_path):
    doc = OpellaDoc(title="Empty Doc", subtitle="", classification="CONFIDENTIAL")
    out = tmp_path / "empty.pdf"
    doc.save(str(out))
    assert out.exists()
