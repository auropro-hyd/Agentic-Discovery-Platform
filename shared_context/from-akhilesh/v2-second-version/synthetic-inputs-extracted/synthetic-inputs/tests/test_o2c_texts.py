import os, sys, tempfile
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from generators.o2c_texts import generate_ar_review_notes, generate_edi_working_notes


def test_ar_review_notes_created(tmp_path):
    path = str(tmp_path / "ar.txt")
    generate_ar_review_notes(path)
    assert os.path.exists(path)


def test_ar_review_notes_contains_carrefour_discrepancy():
    """Must contain the exact quoted discrepancy that seeds F1."""
    with tempfile.TemporaryDirectory() as d:
        path = os.path.join(d, "ar.txt")
        generate_ar_review_notes(path)
        content = open(path).read()
    assert "CRM has" in content and "ERP has" in content
    assert "Carrefour France" in content
    assert "2.4M" in content or "2,400,000" in content
    assert "1.8M" in content or "1,800,000" in content


def test_ar_review_notes_contains_boots_discrepancy():
    with tempfile.TemporaryDirectory() as d:
        path = os.path.join(d, "ar.txt")
        generate_ar_review_notes(path)
        content = open(path).read()
    assert "Boots UK" in content
    assert "NET30" in content and "NET45" in content


def test_ar_review_notes_word_count():
    with tempfile.TemporaryDirectory() as d:
        path = os.path.join(d, "ar.txt")
        generate_ar_review_notes(path)
        words = len(open(path).read().split())
    assert 500 <= words <= 700


def test_edi_working_notes_contains_sanofi_helpdesk_instruction():
    """Must contain the verbatim passage that seeds F3 (Sanofi IT helpdesk dependency)."""
    with tempfile.TemporaryDirectory() as d:
        path = os.path.join(d, "edi.txt")
        generate_edi_working_notes(path)
        content = open(path).read()
    assert "Sanofi IT helpdesk" in content
    assert "Opella Digital" in content and "doesn't manage" in content.lower() or "does not manage" in content.lower()


def test_edi_working_notes_names_six_connections():
    """Must name all 6 Sanofi-managed connections."""
    with tempfile.TemporaryDirectory() as d:
        path = os.path.join(d, "edi.txt")
        generate_edi_working_notes(path)
        content = open(path).read()
    for customer in ["Carrefour", "Boots UK", "dm", "Leclerc", "Lidl", "Coop"]:
        assert customer in content, f"Missing '{customer}' in EDI working notes"


def test_edi_working_notes_word_count():
    with tempfile.TemporaryDirectory() as d:
        path = os.path.join(d, "edi.txt")
        generate_edi_working_notes(path)
        words = len(open(path).read().split())
    assert 900 <= words <= 1300
