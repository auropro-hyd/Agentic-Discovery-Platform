import os, sys, subprocess

OUTPUT_DIR = os.path.join(os.path.dirname(__file__), "..", "output", "o2c")
EXPECTED_FILES = [
    "order-management-sop-opella-europe.pdf",
    "credit-management-policy-opella-europe.pdf",
    "o2c-process-raci-opella-europe.pdf",
    "edi-integration-register-opella-europe.pdf",
    "retail-customer-onboarding-guide-opella-europe.pdf",
    "customer-service-escalation-log-2025.csv",
    "accounts-receivable-review-notes-q4-2025.txt",
    "sap-s4-customer-master-export.csv",
    "sap-crm-customer-export.csv",
    "order-flow-analysis-export-2025.csv",
    "edi-dispute-resolution-cs-working-notes.txt",
    "sanofi-consumer-healthcare-o2c-sop-2023.pdf",
]


def test_all_12_files_generated():
    """Run the generator and verify all 12 output files exist and are non-empty."""
    result = subprocess.run(
        [sys.executable, "generate_o2c.py"],
        cwd=os.path.join(os.path.dirname(__file__), ".."),
        capture_output=True,
        text=True,
    )
    assert result.returncode == 0, f"Generator failed:\n{result.stderr}"

    for filename in EXPECTED_FILES:
        full_path = os.path.join(OUTPUT_DIR, filename)
        assert os.path.exists(full_path), f"Missing: {filename}"
        assert os.path.getsize(full_path) > 500, f"Too small: {filename}"
