import os
import sys

sys.path.insert(0, os.path.dirname(__file__))
from generators.o2c_csvs import (
    generate_cs_escalation_log,
    generate_s4_customer_master,
    generate_crm_customer_export,
    generate_order_flow_analysis,
)
from generators.o2c_texts import generate_ar_review_notes, generate_edi_working_notes
from generators.o2c_pdfs import (
    generate_order_management_sop,
    generate_credit_management_policy,
    generate_o2c_raci,
    generate_edi_integration_register,
    generate_retail_onboarding_guide,
    generate_sanofi_o2c_sop_2023,
)

OUT = os.path.join(os.path.dirname(__file__), "output", "o2c")
os.makedirs(OUT, exist_ok=True)


def p(name: str) -> str:
    return os.path.join(OUT, name)


if __name__ == "__main__":
    print("Generating O2C synthetic input files...")

    print("  01/12 Order Management SOP")
    generate_order_management_sop(p("order-management-sop-opella-europe.pdf"))

    print("  02/12 Credit Management Policy")
    generate_credit_management_policy(p("credit-management-policy-opella-europe.pdf"))

    print("  03/12 O2C Process RACI")
    generate_o2c_raci(p("o2c-process-raci-opella-europe.pdf"))

    print("  04/12 EDI Integration Register")
    generate_edi_integration_register(p("edi-integration-register-opella-europe.pdf"))

    print("  05/12 Retail Customer Onboarding Guide")
    generate_retail_onboarding_guide(p("retail-customer-onboarding-guide-opella-europe.pdf"))

    print("  06/12 Customer Service Escalation Log")
    generate_cs_escalation_log(p("customer-service-escalation-log-2025.csv"))

    print("  07/12 Accounts Receivable Review Notes")
    generate_ar_review_notes(p("accounts-receivable-review-notes-q4-2025.txt"))

    print("  08/12 SAP S4 Customer Master Export")
    generate_s4_customer_master(p("sap-s4-customer-master-export.csv"))

    print("  09/12 SAP CRM Customer Export")
    generate_crm_customer_export(p("sap-crm-customer-export.csv"))

    print("  10/12 Order Flow Analysis Export")
    generate_order_flow_analysis(p("order-flow-analysis-export-2025.csv"))

    print("  11/12 EDI Working Notes")
    generate_edi_working_notes(p("edi-dispute-resolution-cs-working-notes.txt"))

    print("  12/12 Sanofi O2C SOP 2023")
    generate_sanofi_o2c_sop_2023(p("sanofi-consumer-healthcare-o2c-sop-2023.pdf"))

    print(f"\nDone. 12 files written to {OUT}")
