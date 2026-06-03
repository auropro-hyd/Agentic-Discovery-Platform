import os, sys, tempfile
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from generators.o2c_pdfs import (
    generate_order_management_sop,
    generate_credit_management_policy,
    generate_o2c_raci,
    generate_edi_integration_register,
    generate_retail_onboarding_guide,
    generate_sanofi_o2c_sop_2023,
)


def _pdf_exists_and_nonempty(path: str) -> bool:
    return os.path.exists(path) and os.path.getsize(path) > 2000


def test_order_management_sop_generated(tmp_path):
    path = str(tmp_path / "sop.pdf")
    generate_order_management_sop(path)
    assert _pdf_exists_and_nonempty(path)


def test_credit_management_policy_generated(tmp_path):
    path = str(tmp_path / "credit.pdf")
    generate_credit_management_policy(path)
    assert _pdf_exists_and_nonempty(path)


def test_o2c_raci_generated(tmp_path):
    path = str(tmp_path / "raci.pdf")
    generate_o2c_raci(path)
    assert _pdf_exists_and_nonempty(path)


def test_edi_register_generated(tmp_path):
    path = str(tmp_path / "edi.pdf")
    generate_edi_integration_register(path)
    assert _pdf_exists_and_nonempty(path)


def test_onboarding_guide_generated(tmp_path):
    path = str(tmp_path / "onboard.pdf")
    generate_retail_onboarding_guide(path)
    assert _pdf_exists_and_nonempty(path)


def test_sanofi_sop_generated(tmp_path):
    path = str(tmp_path / "sanofi.pdf")
    generate_sanofi_o2c_sop_2023(path)
    assert _pdf_exists_and_nonempty(path)
