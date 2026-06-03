import os
import sys
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
from generators.sop_utils import (
    FONT, C_NAVY, C_BLUE, C_LGRAY, C_GRAY, C_NOTE, C_WHITE, C_BLACK, C_SANOFI,
    _s, _SopPdf, _render_toc,
)

# Re-export the professional Order Management SOP so generate_o2c.py keeps working.
from generators.sop_order_management import generate_order_management_sop  # noqa: F401


# =============================================================================
# Doc 02 — Credit Management Policy
# F1 signal: SAP S/4HANA ERP is the sole authoritative credit limit source.
#            CRM figures must NOT be used. Post-carve-out discrepancies exist.
# =============================================================================

def generate_credit_management_policy(path: str) -> None:
    """Doc 02 — ~13pp professional Credit Management Policy.
    F1: explicit warning that CRM credit figures may diverge from ERP post-carve-out."""

    pdf = _SopPdf(
        ref="OPS-EU-FIN-POL-002",
        title="Credit Management Policy",
        subtitle="Policy Document  |  Opella Europe  |  Finance",
        version="1.3",
        eff_date="01 April 2025",
        review_date="01 April 2026",
        classification="CONFIDENTIAL",
        doc_owner="Finance Director, Europe",
        proc_owner="Credit Controller, UK & Europe",
    )

    # ── Cover ─────────────────────────────────────────────────────────────────
    pdf.cover()

    # ── Document Control ──────────────────────────────────────────────────────
    pdf.add_page()
    pdf.h1("Document Control")

    pdf.h2("Document Information")
    pdf.table(
        ["Field", "Details"],
        [
            ["Document Title",     "Credit Management Policy - Opella Europe"],
            ["Document Reference", "OPS-EU-FIN-POL-002"],
            ["Process Area",       "Finance / Credit & Accounts Receivable"],
            ["Business Unit",      "Opella Europe"],
            ["Document Owner",     "Finance Director, Europe"],
            ["Process Owner",      "Credit Controller, UK & Europe"],
            ["Version",            "1.3"],
            ["Effective Date",     "01 April 2025"],
            ["Review Date",        "01 April 2026"],
            ["Classification",     "CONFIDENTIAL"],
        ],
        widths=[62, 106],
    )

    pdf.h2("Approval and Authorisation")
    pdf.table(
        ["Role", "Name", "Decision", "Date"],
        [
            ["Finance Director, Europe",              "Marc Dupont",      "Approved", "27 Mar 2025"],
            ["VP Commercial Operations, Europe",      "Sophie Marchetti", "Approved", "25 Mar 2025"],
            ["Credit Controller, UK & Europe",        "Raj Patel",        "Reviewed", "20 Mar 2025"],
            ["Legal & Compliance, Europe",            "Isabelle Fontaine","Noted",    "18 Mar 2025"],
        ],
        widths=[68, 42, 28, 30],
    )

    pdf.h2("Version History")
    pdf.table(
        ["Version", "Date", "Author", "Summary of Changes"],
        [
            ["1.3", "01 Apr 2025", "R. Patel",
             "Updated effective at Opella operational independence. Section 4 revised to "
             "clarify authoritative data source for credit limits (ERP only). "
             "Approval authority thresholds updated. Sanofi references removed."],
            ["1.2", "01 Nov 2024", "R. Patel",
             "Interim update during carve-out preparation. Credit limit governance "
             "aligned to Opella operating model. Section 6 (TSA period procedures) added."],
            ["1.1 (Sanofi)", "01 Jan 2023", "Sanofi Credit Ops",
             "Inherited Sanofi Consumer Healthcare Credit Management Policy. "
             "Not authoritative for Opella operations from April 2025."],
        ],
        widths=[17, 23, 28, 100],
    )

    pdf.h2("Related Documents")
    pdf.table(
        ["Reference", "Title", "Ver"],
        [
            ["OPS-EU-CS-SOP-001",  "Order Management SOP - Opella Europe",               "2.1"],
            ["OPS-EU-CS-RACI-001", "Order-to-Cash Process RACI Matrix - Opella Europe",   "1.0"],
            ["OPS-EU-CS-SOP-002",  "Returns and Credits SOP - Opella Europe",             "1.1"],
            ["OPS-EU-FIN-POL-003", "Accounts Receivable Collections Policy",              "1.0"],
        ],
        widths=[50, 98, 20],
    )

    # ── TOC ───────────────────────────────────────────────────────────────────
    pdf.add_page()
    pdf.insert_toc_placeholder(_render_toc, pages=1)
    pdf.h1("1.   Purpose and Scope")

    pdf.h2("1.1   Purpose")
    pdf.para(
        "This policy defines the framework for managing customer credit across Opella "
        "Europe. It establishes the principles, processes, and governance requirements "
        "for setting and maintaining customer credit limits, managing credit holds, "
        "controlling payment terms, and managing overdue accounts.\n\n"
        "This policy is mandatory for all Finance, Credit Control, Customer Service, "
        "and Account Management personnel involved in any aspect of customer credit "
        "management. It is effective from 1 April 2025, the date of Opella's full "
        "operational independence from Sanofi."
    )

    pdf.h2("1.2   Scope")
    pdf.para("This policy applies to:")
    pdf.bullets([
        "All customer accounts within the Opella Europe commercial region (France, United "
        "Kingdom, Germany, Spain, Italy, Benelux, Austria, Switzerland, and wider EMEA).",
        "All credit limit setting, review, and override decisions for accounts in scope.",
        "All credit hold decisions, escalations, and releases.",
        "All payment term negotiations and deviations from standard terms.",
        "Customer accounts migrated from Sanofi at carve-out, which remain subject to "
        "this policy regardless of their historical treatment under Sanofi governance.",
    ])

    pdf.h2("1.3   Exclusions")
    pdf.bullets([
        "Intercompany accounts between Opella entities.",
        "Export accounts in markets outside the Opella Europe commercial region, governed "
        "by separate export credit procedures.",
        "Sanofi accounts under TSA supply arrangements, which are governed by the TSA "
        "rather than this policy.",
    ])

    # ── Section 2: Policy Principles ──────────────────────────────────────────
    pdf.h1("2.   Policy Principles")

    pdf.para(
        "Opella Europe's credit management approach is governed by the following core "
        "principles, which must inform all credit decisions:"
    )
    pdf.numbered([
        "Commercial sustainability: Credit terms exist to enable commercial relationships. "
        "Credit decisions must balance the risk of financial loss against the commercial "
        "value of the customer relationship. Neither principle overrides the other without "
        "escalation to the appropriate approval level.",
        "Single system of record: SAP S/4HANA is the sole authoritative source for all "
        "customer credit limits and outstanding balance data. No credit decision may be "
        "based on data from any other system, document, or verbal communication without "
        "Credit Controller validation against the ERP record.",
        "Documented governance: All credit decisions - approvals, rejections, holds, "
        "releases, and limit changes - must be documented in writing before taking effect. "
        "Verbal authorisations are not acceptable.",
        "Separation of duties: Credit limit decisions and credit hold releases are the "
        "exclusive responsibility of the Credit Controller. Account Managers and CS "
        "Representatives do not have authority to approve credit decisions.",
        "Proportionality: The rigour of the credit assessment process must be proportionate "
        "to the credit exposure involved. Accounts with limits above EUR 500,000 require "
        "enhanced due diligence.",
    ])

    # ── Section 3: Credit Assessment — New Accounts ───────────────────────────
    pdf.add_page()
    pdf.h1("3.   Credit Assessment - New Accounts")

    pdf.h2("3.1   Eligibility for Credit Terms")
    pdf.para(
        "Standard credit terms (as defined in Section 6) are available to all new "
        "accounts that pass the credit assessment in this section. Accounts that do not "
        "pass the assessment are offered cash-with-order terms only, pending a successful "
        "reassessment or the provision of a bank guarantee or surety bond."
    )

    pdf.h2("3.2   Assessment Requirements")
    pdf.para(
        "The Account Manager must submit the following information to the Credit "
        "Controller before a new account credit limit is set:"
    )
    pdf.table(
        ["Required Item", "Description", "Minimum Threshold for Credit"],
        [
            ["Completed Credit Application Form",
             "Signed by an authorised signatory of the customer.",
             "Mandatory for all accounts."],
            ["Trade References",
             "Two supplier references from the customer's existing suppliers.",
             "Mandatory for limits above EUR 100,000."],
            ["Company Accounts (most recent filed)",
             "Audited financial statements or, for private companies, management accounts.",
             "Mandatory for limits above EUR 250,000."],
            ["D&B or Creditsafe Report",
             "Current credit rating report from an approved bureau.",
             "Mandatory for limits above EUR 500,000."],
            ["Bank Guarantee / Surety Bond",
             "Required where the requested limit exceeds the bureau recommended limit.",
             "Discretionary - Credit Controller decision."],
        ],
        widths=[48, 72, 48],
    )

    pdf.h2("3.3   Initial Credit Limit Setting")
    pdf.para(
        "Based on the assessment, the Credit Controller sets an initial credit limit "
        "within the approval tiers in Appendix A. The initial limit is documented in "
        "writing to the Account Manager within five business days of receiving all "
        "required documentation.\n\n"
        "For accounts previously served by Sanofi that are establishing direct trading "
        "with Opella, the Credit Controller may reference the Sanofi historical trading "
        "record as supporting evidence. However, the Opella credit limit is set "
        "independently under Opella governance and does not automatically carry over "
        "the Sanofi limit."
    )

    # ── Section 4: Credit Limit Management ────────────────────────────────────
    pdf.add_page()
    pdf.h1("4.   Credit Limit Management")

    pdf.h2("4.1   Authoritative System of Record")
    pdf.para(
        "SAP S/4HANA (ERP) is the single authoritative system of record for customer "
        "credit limits across Opella Europe. The credit limit maintained in SAP S/4HANA "
        "is the binding figure for all order release decisions, credit hold assessments, "
        "and credit utilisation monitoring."
    )
    pdf.note(
        "IMPORTANT - CRM System Data",
        "The SAP CRM system also contains customer account records, including fields that\n"
        "reference credit limits. These CRM credit figures are NOT authoritative and must\n"
        "NOT be used for credit decisions.\n\n"
        "Following the legal and operational separation from Sanofi in April 2025, certain\n"
        "customer accounts may show inconsistent credit limit data between the SAP ERP\n"
        "and CRM systems as a result of incomplete data synchronisation during the carve-out\n"
        "migration. In all cases, the ERP (S/4HANA) figure governs.\n\n"
        "If a discrepancy between the ERP and CRM credit limit is identified, the Credit\n"
        "Controller must be notified immediately. The CRM record must be updated to reflect\n"
        "the authoritative ERP figure. Personnel must not make credit decisions based on\n"
        "the CRM figure without written Credit Controller confirmation that the CRM figure\n"
        "has been validated against the current ERP record."
    )

    pdf.h2("4.2   Credit Limit Maintenance")
    pdf.para(
        "Only the Credit Controller has authority to create or modify customer credit "
        "limits in SAP S/4HANA. All limit changes require a written approval record "
        "before the SAP update is made. The Credit Controller maintains an audit trail "
        "of all limit changes in the credit management log."
    )
    pdf.bullets([
        "Limit increases require a formal request with supporting trading data and "
        "approval within the tiers defined in Appendix A.",
        "Limit decreases take effect on the next business day after Credit Controller "
        "decision. The Account Manager must be notified before the limit is reduced.",
        "Temporary limit increases (for seasonal peaks or large one-off orders) may be "
        "approved for a defined period not exceeding 90 days. All temporary increases "
        "must include an expiry date in the SAP record.",
        "Limit changes arising from annual review take effect from 1 January each year.",
    ])

    pdf.h2("4.3   Annual Credit Review Cycle")
    pdf.para(
        "The Credit Controller initiates the annual credit review in October for all "
        "active accounts. The review is completed by 30 November for limit changes to "
        "take effect from 1 January."
    )
    pdf.table(
        ["Review Trigger", "Action Required", "Approval Authority"],
        [
            ["Annual cycle (all accounts)",
             "Credit Controller reviews payment performance and adjusts limits if "
             "criteria in Section 4.4 are met.",
             "Credit Controller (within tier A), Finance Director (tiers B/C)."],
            ["Account Manager request (limit increase)",
             "AM submits formal request with last 12 months trading data. "
             "Credit Controller completes assessment within 5 business days.",
             "Per Appendix A approval tiers."],
            ["Customer financial deterioration",
             "Credit Controller initiates immediate review. Account placed on "
             "Credit Review status pending outcome.",
             "Finance Director for reductions above EUR 200,000."],
            ["Post-carve-out migration account",
             "All migrated Sanofi accounts are subject to a full Opella credit "
             "assessment within 12 months of the April 2025 carve-out date.",
             "Per Appendix A approval tiers."],
        ],
        widths=[48, 80, 40],
    )

    pdf.h2("4.4   Credit Review Criteria")
    pdf.para(
        "The following criteria trigger an automatic credit limit review when identified "
        "during the annual cycle or intra-year monitoring:"
    )
    pdf.bullets([
        "More than two late payments (> 30 days overdue) in the 12-month review period.",
        "Outstanding balance exceeding 80% of the approved credit limit for more than "
        "three consecutive months.",
        "Material deterioration in publicly available financial information.",
        "Change of ownership or group structure affecting the customer entity.",
        "Any invoice under formal dispute for more than 60 days.",
    ])

    # ── Section 5: Credit Hold Procedures ─────────────────────────────────────
    pdf.add_page()
    pdf.h1("5.   Credit Hold Procedures")

    pdf.h2("5.1   Automatic Credit Holds")
    pdf.para(
        "SAP S/4HANA automatically places an order on credit hold when processing the "
        "order would cause the customer's outstanding balance to exceed their approved "
        "credit limit. An automatic hold may also be triggered by a delinquency flag "
        "where the customer has an invoice more than 60 days overdue."
    )

    pdf.h2("5.2   Manual Credit Holds")
    pdf.para(
        "The Credit Controller may manually apply a credit hold to an account at any "
        "time without an automatic trigger. Manual holds are applied when the Credit "
        "Controller has information indicating a material credit risk that warrants "
        "suspending order processing pending investigation. The reason for a manual "
        "hold must be documented in the SAP account record."
    )

    pdf.h2("5.3   Credit Hold Response Procedure")
    pdf.numbered([
        "The CS Representative receives a SAP notification when a credit hold is triggered "
        "and must notify the Credit Controller within four business hours of the "
        "notification, providing: customer name and SAP account number, order reference "
        "and total order value, current outstanding balance, and approved credit limit.",
        "The Credit Controller reviews the hold and communicates their decision within "
        "four business hours of CS notification. If the Credit Controller is unavailable, "
        "the CS Representative escalates to the Finance Director.",
        "Credit Controller decision options: (a) Release with documented justification; "
        "(b) Approve a temporary limit increase with defined expiry date; "
        "(c) Request partial payment before release; (d) Reject order and notify customer.",
        "The Credit Controller's decision must be recorded in writing (email is "
        "sufficient) and attached to the SAP order record before the hold is released.",
        "The CS Representative may not release a credit hold under any circumstances "
        "without the Credit Controller's written authorisation. This applies regardless "
        "of instructions received from Account Managers or commercial colleagues.",
        "If the Credit Controller does not respond within four business hours, the CS "
        "Representative escalates to the CS Team Lead, who escalates to the Finance "
        "Director.",
    ])
    pdf.note(
        "POLICY REQUIREMENT - No Informal Credit Releases",
        "Releasing a credit hold based on verbal instruction, without written Credit\n"
        "Controller authorisation documented in the SAP order record, constitutes a\n"
        "material policy breach. Breaches will be escalated to the Finance Director\n"
        "and the relevant line manager and may result in formal disciplinary action."
    )

    # ── Section 6: Payment Terms ───────────────────────────────────────────────
    pdf.h1("6.   Payment Terms")

    pdf.h2("6.1   Standard Payment Terms by Account Tier")
    pdf.table(
        ["Account Tier", "Account Type", "Standard Terms", "Early Payment Discount"],
        [
            ["Tier 1 - Major Retail",
             "National supermarket chains and pharmacy multiples with annual "
             "Opella purchases above EUR 2M.",
             "NET 45 days from invoice date.",
             "1% for payment within 15 days."],
            ["Tier 2 - Pharmacy & Wholesale",
             "Regional pharmacy chains, buying groups, and pharmaceutical "
             "wholesalers.",
             "NET 30 days from invoice date.",
             "Not offered as standard."],
            ["Tier 3 - Independent",
             "Independent pharmacies, specialist retailers, and other accounts "
             "not meeting Tier 1 or 2 criteria.",
             "NET 30 days from invoice date.",
             "Not offered as standard."],
            ["New Account (first 6 months)",
             "Any account in its first 6 months of trading with Opella where "
             "full credit assessment has not been completed.",
             "NET 14 days or cash-with-order per Credit Controller instruction.",
             "N/A."],
        ],
        widths=[28, 60, 42, 38],
    )

    pdf.h2("6.2   Deviations from Standard Terms")
    pdf.para(
        "Deviations from the standard payment terms applicable to an account tier "
        "require prior written approval from the Finance Director. Deviations agreed "
        "with customers by Account Managers without Finance Director approval are not "
        "binding and will not be reflected in the SAP customer master.\n\n"
        "All approved deviations must be documented in the SAP customer record with "
        "the approval reference, the agreed terms, and the period for which the "
        "deviation applies. Permanent deviations from standard terms must be included "
        "in the customer's commercial agreement."
    )

    # ── Section 7: Overdue Account Management ─────────────────────────────────
    pdf.add_page()
    pdf.h1("7.   Overdue Account Management")

    pdf.h2("7.1   Overdue Escalation Ladder")
    pdf.table(
        ["Overdue Period", "Collections Action", "Responsibility", "Escalation"],
        [
            ["1 - 30 days",
             "Automated payment reminder issued by SAP on day 5 post due date.",
             "System automated.",
             "None required."],
            ["31 - 60 days",
             "Credit Controller issues formal payment demand by email and telephone. "
             "Account flagged for enhanced monitoring.",
             "Credit Controller.",
             "Account Manager notified."],
            ["61 - 90 days",
             "Second formal demand. Credit Controller proposes account credit hold "
             "to Finance Director.",
             "Credit Controller.",
             "Finance Director and Account Manager."],
            ["91+ days",
             "Account placed on credit hold. New orders suspended. Finance Director "
             "and Account Manager agree collections strategy. External collections "
             "agency referral considered.",
             "Finance Director.",
             "VP Commercial Operations."],
        ],
        widths=[26, 70, 34, 38],
    )

    pdf.h2("7.2   Collections Reporting")
    pdf.para(
        "The Credit Controller produces a monthly aged debtors report, distributed to "
        "the Finance Director and VP Commercial Operations by the 5th working day of "
        "each month. The report shows all accounts with outstanding balances, days "
        "outstanding, and credit hold status. Accounts more than 60 days overdue are "
        "individually reviewed in the monthly Finance and Commercial review meeting."
    )

    # ── Section 8: Compliance ──────────────────────────────────────────────────
    pdf.h1("8.   Compliance and Governance")

    pdf.h2("8.1   Policy Compliance")
    pdf.para(
        "Compliance with this policy is mandatory for all personnel in scope. "
        "Non-compliance identified through self-reporting, audit, customer complaint, "
        "or management review will be escalated to the Finance Director and the "
        "relevant line manager. Serious or repeated non-compliance may result in formal "
        "corrective action under Opella's HR performance management process."
    )

    pdf.h2("8.2   Audit Scope")
    pdf.bullets([
        "Annual audit by Opella Internal Audit: sample review of credit limit changes, "
        "credit hold decisions and releases, payment term deviations, and overdue "
        "collections actions.",
        "Quarterly self-assessment by the Credit Controller: review of credit limit "
        "data accuracy in SAP S/4HANA against approved credit files, identification "
        "of any ERP/CRM data discrepancies, and review of holds pending resolution.",
        "Post-carve-out data integrity check: a targeted review of all accounts "
        "migrated from Sanofi to confirm credit limits in SAP S/4HANA are consistent "
        "with the latest approved Opella credit files. Target completion: Q3 2025.",
    ])

    # ── Appendix A ─────────────────────────────────────────────────────────────
    pdf.add_page()
    pdf.h1("Appendix A:   Credit Limit Approval Authority")

    pdf.table(
        ["Credit Limit Band", "New Account", "Limit Increase", "Temporary Increase"],
        [
            ["Up to EUR 50,000",
             "Credit Controller",
             "Credit Controller",
             "Credit Controller"],
            ["EUR 50,001 - EUR 250,000",
             "Credit Controller",
             "Credit Controller",
             "Credit Controller"],
            ["EUR 250,001 - EUR 500,000",
             "Finance Director",
             "Finance Director",
             "Credit Controller (max 30 days)"],
            ["EUR 500,001 - EUR 1,000,000",
             "Finance Director + VP Comm Ops",
             "Finance Director",
             "Finance Director (max 30 days)"],
            ["Above EUR 1,000,000",
             "Finance Director + VP Comm Ops + CEO",
             "Finance Director + VP Comm Ops",
             "Finance Director + VP Comm Ops"],
        ],
        widths=[44, 44, 44, 36],
    )

    # ── Appendix B ─────────────────────────────────────────────────────────────
    pdf.h1("Appendix B:   Credit Application Requirements Checklist")

    pdf.table(
        ["#", "Requirement", "Mandatory For", "Submitted By"],
        [
            ["1", "Completed Opella Credit Application Form (signed)",
             "All new accounts",
             "Account Manager"],
            ["2", "Two trade references from existing suppliers",
             "Limits > EUR 100,000",
             "Account Manager / Customer"],
            ["3", "Most recent filed company accounts or management accounts",
             "Limits > EUR 250,000",
             "Account Manager / Customer"],
            ["4", "D&B or Creditsafe current credit report",
             "Limits > EUR 500,000",
             "Credit Controller"],
            ["5", "Bank guarantee or surety bond",
             "Where requested limit exceeds bureau recommendation",
             "Customer"],
            ["6", "Completed KYC/AML screening confirmation",
             "All new accounts",
             "Finance / Compliance"],
        ],
        widths=[8, 70, 54, 36],
    )

    pdf.output(path)


# =============================================================================
# Doc 03 — O2C Process RACI
# F2 signal: NO EDI row anywhere in the RACI matrix.
# =============================================================================

def generate_o2c_raci(path: str) -> None:
    """Doc 03 — ~8pp professional O2C RACI matrix.
    F2: zero EDI process steps in the accountability matrix."""

    pdf = _SopPdf(
        ref="OPS-EU-CS-RACI-001",
        title="Order-to-Cash Process RACI Matrix",
        subtitle="Process Reference  |  Opella Europe  |  Commercial Operations",
        version="1.0",
        eff_date="01 April 2025",
        review_date="01 April 2026",
        classification="INTERNAL",
        doc_owner="VP Commercial Operations, Europe",
        proc_owner="Customer Service Team Lead, Europe",
    )

    pdf.cover()

    # ── Document Control ──────────────────────────────────────────────────────
    pdf.add_page()
    pdf.h1("Document Control")

    pdf.h2("Document Information")
    pdf.table(
        ["Field", "Details"],
        [
            ["Document Title",     "Order-to-Cash Process RACI Matrix - Opella Europe"],
            ["Document Reference", "OPS-EU-CS-RACI-001"],
            ["Process Area",       "Order-to-Cash / Commercial Operations"],
            ["Scope",              "All O2C process steps for Opella Europe accounts"],
            ["Document Owner",     "VP Commercial Operations, Europe"],
            ["Process Owner",      "Customer Service Team Lead, Europe"],
            ["Version",            "1.0"],
            ["Effective Date",     "01 April 2025"],
            ["Review Date",        "01 April 2026"],
            ["Classification",     "INTERNAL"],
        ],
        widths=[62, 106],
    )

    pdf.h2("Approval")
    pdf.table(
        ["Role", "Name", "Decision", "Date"],
        [
            ["VP Commercial Operations, Europe",   "Sophie Marchetti", "Approved", "28 Mar 2025"],
            ["Finance Director, Europe",           "Marc Dupont",      "Approved", "26 Mar 2025"],
            ["CS Team Lead, Europe",               "Alina Kovacs",     "Reviewed", "20 Mar 2025"],
        ],
        widths=[70, 44, 28, 26],
    )

    pdf.h2("Version History")
    pdf.table(
        ["Version", "Date", "Author", "Notes"],
        [
            ["1.0", "01 Apr 2025", "A. Kovacs",
             "Initial Opella version. Adapted from Sanofi Consumer Healthcare O2C RACI "
             "v2.1 (2022). Roles updated to reflect Opella post-carve-out structure. "
             "EDI-related rows excluded pending formal EDI process documentation (target: "
             "Q3 2025 per Order Management SOP OPS-EU-CS-SOP-001 Section 1.3)."],
        ],
        widths=[17, 23, 28, 100],
    )

    pdf.h2("Related Documents")
    pdf.table(
        ["Reference", "Title"],
        [
            ["OPS-EU-CS-SOP-001",  "Order Management SOP - Opella Europe v2.1"],
            ["OPS-EU-FIN-POL-002", "Credit Management Policy - Opella Europe v1.3"],
            ["OPS-EU-CS-SOP-002",  "Returns and Credits SOP - Opella Europe v1.1"],
        ],
        widths=[50, 118],
    )

    # ── TOC ───────────────────────────────────────────────────────────────────
    pdf.add_page()
    pdf.insert_toc_placeholder(_render_toc, pages=1)
    pdf.h1("1.   Purpose and Scope")

    pdf.para(
        "This document defines the Responsible, Accountable, Consulted, and Informed "
        "(RACI) assignments for each step of the Order-to-Cash process within Opella "
        "Europe. It provides a single reference for process ownership, escalation "
        "authority, and inter-functional coordination requirements.\n\n"
        "This RACI is the authoritative reference for O2C process accountability and "
        "must be read in conjunction with the Order Management SOP (OPS-EU-CS-SOP-001) "
        "and the Credit Management Policy (OPS-EU-FIN-POL-002)."
    )
    pdf.note(
        "RACI Key",
        "R = Responsible: The role that performs the task or produces the output.\n"
        "A = Accountable: The role that owns the outcome and approves the deliverable.\n"
        "    Only one A per process step.\n"
        "C = Consulted: The role whose input is required before the step is completed.\n"
        "I  = Informed: The role that must be notified when the step is completed or\n"
        "    when its outcome is known."
    )

    # ── Section 2: Roles ──────────────────────────────────────────────────────
    pdf.h1("2.   Roles in Scope")

    pdf.table(
        ["Role", "Current Post-holder", "O2C Responsibility Summary"],
        [
            ["Customer Service Representative (CSR)",
             "CS Team (4 FTE)",
             "Day-to-day order processing: receipt, validation, confirmation, "
             "monitoring, and first-line customer query resolution."],
            ["Customer Service Team Lead",
             "Alina Kovacs",
             "Operational oversight of CS function. Second-level escalation. "
             "SOP maintenance. Monthly KPI reporting."],
            ["Credit Controller",
             "Raj Patel",
             "All credit-related decisions: limit maintenance, credit hold "
             "releases, overdue collections, AR reporting."],
            ["Account Manager (AM)",
             "Multiple (by market)",
             "Commercial relationship ownership. Credit limit review requests. "
             "MOQ exception approvals. Strategic escalation management."],
            ["DC Operations",
             "DC Control Rooms (per market)",
             "Order fulfilment: pick, pack, despatch, and partial shipment "
             "notification."],
            ["Finance Director",
             "Marc Dupont",
             "Final approval for credit decisions above Credit Controller tier. "
             "AR governance. Monthly Finance review."],
            ["VP Commercial Operations",
             "Sophie Marchetti",
             "Policy ownership. Strategic escalation. Board-level reporting."],
        ],
        widths=[46, 40, 82],
    )

    # ── Section 3: O2C RACI Matrix ────────────────────────────────────────────
    pdf.add_page()
    pdf.h1("3.   O2C Process RACI Matrix")

    pdf.para(
        "The RACI matrix below covers the full Order-to-Cash process for orders "
        "received through manual (telephone) and email channels. Each row represents "
        "a distinct process step. Column abbreviations: CSR = Customer Service "
        "Representative; CS TL = CS Team Lead; CC = Credit Controller; AM = Account "
        "Manager; DC = DC Operations; FD = Finance Director; VP = VP Commercial Ops."
    )
    pdf.note(
        "SCOPE NOTE",
        "This RACI covers Manual (telephone) and Email order channels only. EDI channel\n"
        "process steps are not included in this version of the RACI. Formal accountability\n"
        "assignments for EDI order processing will be documented upon completion of the\n"
        "EDI SOP currently under development (target: Q3 2025). Personnel handling EDI\n"
        "queries should refer to working notes OPS-EU-IT-WN-001 and contact the CS Team\n"
        "Lead for process guidance."
    )

    raci_headers = ["Process Step", "CSR", "CS TL", "CC", "AM", "DC", "FD", "VP"]
    raci_rows = [
        # --- ORDER RECEIPT ---
        ["ORDER RECEIPT", "", "", "", "", "", "", ""],
        ["Receive telephone order from authorised customer contact",
         "R", "A", "", "I", "", "", ""],
        ["Receive email order from designated order mailbox",
         "R", "A", "", "I", "", "", ""],
        ["Acknowledge receipt to customer (email)",
         "R", "A", "", "", "", "", ""],
        # --- ORDER VALIDATION ---
        ["ORDER VALIDATION", "", "", "", "", "", "", ""],
        ["Check customer account status in SAP S/4HANA",
         "R", "A", "C", "", "", "", ""],
        ["Verify credit limit against outstanding balance in SAP S/4HANA",
         "R", "A", "C", "", "", "", ""],
        ["Notify Credit Controller of credit hold trigger (within 4 hrs)",
         "R", "I", "R/A", "I", "", "", ""],
        ["Credit hold review and release/reject decision",
         "I", "C", "R", "C", "A", "", ""],
        ["Verify product availability at DC",
         "R", "A", "", "", "C", "", ""],
        ["Check MOQ compliance for account tier",
         "R", "A", "", "C", "", "", ""],
        ["Obtain AM written approval for sub-MOQ exception",
         "R", "I", "", "R/A", "", "", ""],
        ["Validate pricing against SAP price list",
         "R", "A", "", "C", "", "", ""],
        # --- ORDER CONFIRMATION ---
        ["ORDER CONFIRMATION", "", "", "", "", "", "", ""],
        ["Issue formal order confirmation to customer (manual: 4hrs; email: 2hrs)",
         "R", "A", "", "I", "", "", ""],
        ["Resolve order confirmation discrepancy with customer",
         "R", "A", "", "C", "", "", ""],
        # --- ORDER RELEASE & FULFILMENT ---
        ["ORDER RELEASE AND FULFILMENT", "", "", "", "", "", "", ""],
        ["Release validated order to DC in SAP S/4HANA",
         "R", "A", "", "", "I", "", ""],
        ["Process order at DC (pick, pack, despatch)",
         "I", "I", "", "", "R/A", "", ""],
        ["Monitor order status through to despatch confirmation",
         "R", "A", "", "", "C", "", ""],
        ["Notify customer of delivery delay (within 2 hrs of identifying)",
         "R", "A", "", "I", "", "", ""],
        ["Log delayed order in CS exception register",
         "R", "A", "", "", "", "", ""],
        ["Agree partial shipment terms with customer (written confirmation)",
         "R", "A", "", "I", "C", "", ""],
        ["Create backorder in SAP for unshipped partial quantity",
         "R", "A", "", "", "", "", ""],
        # --- INVOICING ---
        ["INVOICING AND PAYMENT", "", "", "", "", "", "", ""],
        ["Verify invoice auto-generation in SAP (within 1 BD of despatch)",
         "R", "I", "A", "", "", "", ""],
        ["Log invoice dispute in SAP (within 1 BD of receipt)",
         "R", "A", "C", "", "", "", ""],
        ["Cash application and AR reconciliation",
         "I", "I", "R/A", "", "", "I", ""],
        ["Overdue collections (31-60 days)",
         "I", "C", "R/A", "C", "", "I", ""],
        ["Overdue escalation (91+ days / credit hold)",
         "I", "C", "C", "C", "A", "R", ""],
        # --- RETURNS & CREDIT NOTES ---
        ["RETURNS AND CREDIT NOTES", "", "", "", "", "", "", ""],
        ["Receive and log returns request from customer",
         "R", "A", "I", "I", "", "", ""],
        ["Validate return eligibility against returns policy",
         "R", "A", "C", "", "", "", ""],
        ["Authorise and issue credit note",
         "C", "I", "R", "I", "A", "", ""],
        # --- REPORTING ---
        ["REPORTING AND GOVERNANCE", "", "", "", "", "", "", ""],
        ["Monthly CS KPI report to VP Commercial Ops",
         "C", "R", "I", "", "", "I", "A"],
        ["Monthly aged debtors report to Finance Director",
         "I", "I", "R", "", "", "A", "I"],
        ["Quarterly O2C self-assessment",
         "I", "R", "C", "", "", "C", "A"],
    ]

    raci_widths = [66, 12, 14, 12, 12, 12, 12, 12]
    pdf.table(raci_headers, raci_rows, widths=raci_widths)

    # ── Section 4: Governance ─────────────────────────────────────────────────
    pdf.h1("4.   Governance and Review")

    pdf.h2("4.1   RACI Maintenance")
    pdf.para(
        "This RACI is owned by the VP Commercial Operations, Europe and must be "
        "reviewed annually or when there is a material change to the O2C process, "
        "organisation structure, or systems landscape. Proposed changes must be "
        "approved by the VP Commercial Operations and the Finance Director before "
        "taking effect."
    )

    pdf.h2("4.2   Escalation Path")
    pdf.bullets([
        "For day-to-day process queries: CS Team Lead (A. Kovacs).",
        "For credit-related process queries: Credit Controller (R. Patel).",
        "For process ownership and governance: VP Commercial Operations (S. Marchetti).",
    ])

    pdf.h2("4.3   EDI Process Documentation Status")
    pdf.para(
        "The Order Management SOP (OPS-EU-CS-SOP-001, Section 1.3) notes that EDI "
        "order channel process documentation is under development with a target "
        "publication date of Q3 2025. This RACI will be updated at that time to "
        "include EDI-specific accountability assignments. Until that version is "
        "published, all EDI process accountability questions must be directed to "
        "the CS Team Lead."
    )

    pdf.output(path)


# =============================================================================
# Doc 04 — EDI Integration Register
# F3 signal: 14 connections total; 6 still managed by Sanofi Shared Services
#            under TSA with "See TSA Schedule Annex C" — Annex C not in the pack.
# =============================================================================

def generate_edi_integration_register(path: str) -> None:
    """Doc 04 — ~10pp professional EDI Integration Register.
    F3: 6 of 14 connections remain with Sanofi Shared Services under TSA Annex C."""

    pdf = _SopPdf(
        ref="OPS-EU-IT-REG-001",
        title="EDI Integration Register",
        subtitle="Technical Reference  |  Opella Digital  |  Version 1.1",
        version="1.1",
        eff_date="15 September 2025",
        review_date="15 December 2025",
        classification="INTERNAL - RESTRICTED",
        doc_owner="Head of Opella Digital, Europe",
        proc_owner="EDI Integration Lead (J. Okafor)",
    )

    pdf.cover()

    # ── Document Control ──────────────────────────────────────────────────────
    pdf.add_page()
    pdf.h1("Document Control")

    pdf.h2("Document Information")
    pdf.table(
        ["Field", "Details"],
        [
            ["Document Title",     "EDI Integration Register - Opella Europe"],
            ["Document Reference", "OPS-EU-IT-REG-001"],
            ["Process Area",       "IT / Digital / EDI"],
            ["Maintained By",      "Opella Digital (James Okafor, EDI Integration Lead)"],
            ["Document Owner",     "Head of Opella Digital, Europe"],
            ["Process Owner",      "EDI Integration Lead (J. Okafor)"],
            ["Version",            "1.1"],
            ["Last Updated",       "15 September 2025"],
            ["Next Review",        "15 December 2025 (quarterly)"],
            ["Classification",     "INTERNAL - RESTRICTED"],
        ],
        widths=[62, 106],
    )
    pdf.note(
        "IMPORTANT - Restricted Distribution",
        "This document contains details of active trading partner integrations and\n"
        "TSA governance status. Distribution is restricted to: Opella Digital,\n"
        "CS Team Lead, Finance Director, and TSA Programme Office. Do not circulate\n"
        "to customers, external partners, or non-Opella personnel."
    )

    pdf.h2("Version History")
    pdf.table(
        ["Version", "Date", "Author", "Summary"],
        [
            ["1.1", "15 Sep 2025", "J. Okafor",
             "Updated connection status: Tesco UK and Mercadona confirmed fully "
             "transitioned to Opella Digital management. Boots UK new connection "
             "added (went live 01 Aug 2025). TSA status column clarified. "
             "Connections 9-14 remain Sanofi Shared Services managed."],
            ["1.0", "01 May 2025", "J. Okafor",
             "Initial register at Opella operational independence. "
             "Reflects EDI landscape at April 2025 carve-out. "
             "8 connections under Opella Digital management, 6 under Sanofi "
             "Shared Services TSA."],
        ],
        widths=[17, 23, 28, 100],
    )

    # ── TOC ───────────────────────────────────────────────────────────────────
    pdf.add_page()
    pdf.insert_toc_placeholder(_render_toc, pages=1)
    pdf.h1("1.   Purpose and Scope")

    pdf.h2("1.1   Purpose")
    pdf.para(
        "This register documents all active Electronic Data Interchange (EDI) "
        "connections between Opella Europe and its retail and pharmacy trading partners. "
        "It records the connection configuration, managing entity, operational status, "
        "and TSA governance status for each connection.\n\n"
        "The register provides the authoritative reference for:\n"
        "- Identifying the management responsibility for each EDI connection.\n"
        "- Understanding which connections remain subject to the Sanofi Transition "
        "Services Agreement (TSA) and where to direct operational queries.\n"
        "- Tracking the migration timeline for TSA-managed connections.\n"
        "- Supporting incident management and customer escalation handling."
    )

    pdf.h2("1.2   Scope")
    pdf.para(
        "The register covers all EDI connections between Opella Europe and external "
        "trading partners, including connections that are currently managed by Sanofi "
        "Shared Services under the TSA. It does not cover:"
    )
    pdf.bullets([
        "Web portal or API-based order integrations (documented separately).",
        "Internal system integrations between Opella entities.",
        "EDI connections in markets outside the Opella Europe commercial region.",
        "Connections in setup or testing phase (not yet live in production).",
    ])

    pdf.h2("1.3   Relationship to Other Documents")
    pdf.para(
        "This register is referenced in the Order Management SOP (OPS-EU-CS-SOP-001, "
        "Section 1.3) and the EDI Dispute Resolution Working Notes (OPS-EU-IT-WN-001). "
        "Operational queries regarding specific connections should be directed per the "
        "contact information in Section 5."
    )

    # ── Section 2: Architecture Overview ─────────────────────────────────────
    pdf.h1("2.   Architecture Overview")

    pdf.h2("2.1   EDI Platform")
    pdf.para(
        "Opella Digital manages active EDI connections through the Opella Europe EDI "
        "platform (IBM Sterling B2B Integrator, hosted on Opella private cloud, "
        "Frankfurt). All Opella Digital-managed connections in this register are routed "
        "through this platform.\n\n"
        "Connections managed by Sanofi Shared Services remain on the Sanofi EDI "
        "platform (SAP Integration Suite, managed by Sanofi Global IT) under the terms "
        "of the TSA. These connections will be migrated to the Opella platform per "
        "the migration schedule in Section 4."
    )

    pdf.h2("2.2   Message Types in Use")
    pdf.table(
        ["EDI Message", "Standard", "Description"],
        [
            ["ORDERS",  "EDIFACT D96A", "Inbound purchase order from trading partner."],
            ["ORDRSP",  "EDIFACT D96A", "Outbound order acknowledgement/confirmation."],
            ["DESADV",  "EDIFACT D96A", "Outbound advance ship notice (ASN)."],
            ["INVOIC",  "EDIFACT D96A", "Outbound invoice."],
        ],
        widths=[20, 30, 118],
    )

    # ── Section 3: Active Connections Register ────────────────────────────────
    pdf.add_page()
    pdf.h1("3.   Active Connections Register")

    pdf.para(
        "All 14 active production EDI connections as of the document update date "
        "are listed below. Connections are categorised by managing entity: "
        "8 under Opella Digital management (connections 1-8) and 6 remaining "
        "under Sanofi Shared Services management under TSA terms (connections 9-14)."
    )
    pdf.table(
        ["#", "Customer", "Ctry", "Message Types", "Status", "Managed By", "TSA Status"],
        [
            ["1",  "Tesco UK",            "UK",
             "ORDERS / ORDRSP / DESADV / INVOIC",
             "Live",
             "Opella Digital",
             "N/A - Opella owned"],
            ["2",  "Mercadona",           "ES",
             "ORDERS / ORDRSP",
             "Live",
             "Opella Digital",
             "N/A - Opella owned"],
            ["3",  "REWE Group",          "DE",
             "ORDERS / ORDRSP",
             "Live",
             "Opella Digital",
             "N/A - Opella owned"],
            ["4",  "Boots UK (new)",      "UK",
             "ORDERS / ORDRSP",
             "Live (since 01 Aug 2025)",
             "Opella Digital",
             "N/A - Opella owned"],
            ["5",  "Alliance Healthcare", "EU",
             "ORDERS / DESADV",
             "Live",
             "Opella Digital",
             "N/A - Opella owned"],
            ["6",  "Rite Aid Europe",     "EU",
             "ORDERS / ORDRSP",
             "Live",
             "Opella Digital",
             "N/A - Opella owned"],
            ["7",  "Aldi Europe",         "EU",
             "ORDERS",
             "Live",
             "Opella Digital",
             "N/A - Opella owned"],
            ["8",  "Coop Group (new)",    "EU",
             "ORDERS / ORDRSP / INVOIC",
             "Live",
             "Opella Digital",
             "N/A - Opella owned"],
            ["9",  "Carrefour France",    "FR",
             "ORDERS / ORDRSP / INVOIC",
             "Live",
             "Sanofi Shared Services",
             "See TSA Schedule Annex C"],
            ["10", "Boots UK (legacy)",   "UK",
             "ORDERS / ORDRSP / INVOIC",
             "Live",
             "Sanofi Shared Services",
             "See TSA Schedule Annex C"],
            ["11", "dm (Drogerie Markt)", "DE",
             "ORDERS / ORDRSP",
             "Live",
             "Sanofi Shared Services",
             "See TSA Schedule Annex C"],
            ["12", "E.Leclerc",           "FR",
             "ORDERS / ORDRSP / DESADV",
             "Live",
             "Sanofi Shared Services",
             "See TSA Schedule Annex C"],
            ["13", "Lidl Europe",         "EU",
             "ORDERS / ORDRSP",
             "Live",
             "Sanofi Shared Services",
             "See TSA Schedule Annex C"],
            ["14", "Coop Group (legacy)", "EU",
             "ORDERS / INVOIC",
             "Live",
             "Sanofi Shared Services",
             "See TSA Schedule Annex C"],
        ],
        widths=[8, 36, 12, 44, 24, 26, 18],
    )

    # ── Section 4: TSA-Managed Connections ────────────────────────────────────
    pdf.add_page()
    pdf.h1("4.   TSA-Managed Connections - Transition Status")

    pdf.h2("4.1   TSA Governance")
    pdf.para(
        "Connections 9-14 in Section 3 are operated by Sanofi Shared Services "
        "under the terms of the Transition Services Agreement (TSA) between Opella "
        "and Sanofi. Under the TSA, Sanofi continues to provide EDI connectivity "
        "services for these six trading partners until each connection is formally "
        "transferred to Opella Digital management.\n\n"
        "The specific service terms, SLAs, handover process, and migration timeline "
        "for these connections are defined in TSA Schedule Annex C. TSA Schedule "
        "Annex C is a separate controlled document held by the Opella TSA Programme "
        "Office and is not reproduced in this register."
    )
    pdf.note(
        "TSA SCHEDULE ANNEX C",
        "The terms governing connections 9-14 are set out in TSA Schedule Annex C.\n"
        "For questions about SLAs, incident response, or migration timelines for\n"
        "TSA-managed connections, contact the Opella TSA Programme Office.\n\n"
        "DO NOT contact Sanofi IT directly for operational issues on these connections\n"
        "without first notifying the TSA Programme Office - all contact with Sanofi\n"
        "Shared Services must be managed through the TSA governance framework."
    )

    pdf.h2("4.2   TSA Connection Migration Overview")
    pdf.table(
        ["Connection", "Customer", "Target Migration Quarter", "Migration Lead", "Status"],
        [
            ["9",  "Carrefour France",    "Q4 2025", "J. Okafor",
             "Technical scoping in progress."],
            ["10", "Boots UK (legacy)",   "Q1 2026", "J. Okafor",
             "Decommission pending: Boots UK new connection (#4) already live."],
            ["11", "dm (Drogerie Markt)", "Q1 2026", "J. Okafor",
             "Pre-scoping. Awaiting Sanofi handover documentation."],
            ["12", "E.Leclerc",           "Q2 2026", "TBD",
             "Not yet scoped. Volume complexity requires dedicated resource."],
            ["13", "Lidl Europe",         "Q2 2026", "TBD",
             "Not yet scoped. Multi-country routing requires review."],
            ["14", "Coop Group (legacy)", "Q3 2026", "TBD",
             "Planned decommission: Coop new connection (#8) already live."],
        ],
        widths=[14, 36, 28, 26, 64],
    )
    pdf.para(
        "Migration targets are indicative and subject to TSA Programme Office "
        "confirmation. All targets for connections 12-14 are provisional pending "
        "technical scoping. The Opella Digital team will update this section "
        "quarterly as part of the standard register review."
    )

    # ── Section 5: Support and Incident Management ────────────────────────────
    pdf.h1("5.   Support and Incident Management")

    pdf.h2("5.1   Opella Digital-Managed Connections (1-8)")
    pdf.para(
        "For connections managed by Opella Digital (connections 1-8), all incidents "
        "and operational queries must be directed to:"
    )
    pdf.table(
        ["Contact", "Details", "Hours"],
        [
            ["EDI Integration Lead",
             "James Okafor — james.okafor@opella.com — +44 7700 900 123",
             "Mon-Fri 08:00-18:00 CET"],
            ["Opella Digital IT Helpdesk",
             "helpdesk.digital@opella.com — ticket portal: jira.opella.com/edi",
             "Mon-Fri 08:00-20:00 CET"],
        ],
        widths=[44, 84, 40],
    )
    pdf.table(
        ["Priority", "Definition", "Response SLA", "Resolution SLA"],
        [
            ["P1 - Critical",
             "Connection fully down; orders not transmitting for accounts with "
             "daily order volume > EUR 500K.",
             "30 minutes",
             "4 business hours"],
            ["P2 - High",
             "Connection degraded; intermittent failures or message errors affecting "
             "order processing for any active connection.",
             "2 business hours",
             "1 business day"],
            ["P3 - Normal",
             "Non-critical issues: mapping queries, test message failures, "
             "minor configuration requests.",
             "1 business day",
             "5 business days"],
        ],
        widths=[24, 72, 30, 42],
    )

    pdf.h2("5.2   TSA-Managed Connections (9-14)")
    pdf.para(
        "For connections managed by Sanofi Shared Services (connections 9-14), "
        "incident and support escalation must follow the TSA governance process. "
        "CS Representatives and CS Team Lead must NOT contact Sanofi IT directly. "
        "All incidents must be reported to the Opella Digital team, who will "
        "escalate through the TSA framework."
    )
    pdf.bullets([
        "First contact: Opella Digital (J. Okafor) — who will determine whether the "
        "issue is Opella-side or Sanofi-side and escalate accordingly.",
        "For Sanofi-side issues: Opella Digital submits a TSA incident ticket to Sanofi "
        "Shared Services EDI support. SLAs are governed by TSA Schedule Annex C.",
        "Escalation for unresolved TSA incidents: Opella TSA Programme Office.",
    ])

    # ── Section 6: Maintenance and Governance ────────────────────────────────
    pdf.h1("6.   Register Maintenance and Governance")

    pdf.para(
        "This register is reviewed quarterly by Opella Digital. Changes to connection "
        "status, management ownership, or TSA classification must be notified to the "
        "EDI Integration Lead within five business days of the change taking effect. "
        "The following types of change trigger an immediate (unscheduled) update:\n\n"
        "- Addition or decommission of a production connection.\n"
        "- Transfer of a connection from TSA to Opella Digital management.\n"
        "- Material change to a connection's message types or technical configuration.\n"
        "- Change to the TSA migration target date for connections 9-14."
    )

    pdf.output(path)


# =============================================================================
# Doc 05 — Retail Customer Onboarding Guide
# Signal: "create the customer record in our systems" — no system named,
# implies parallel records in ERP + CRM by default.
# =============================================================================

def generate_retail_onboarding_guide(path: str) -> None:
    """Doc 05 — ~11pp professional Retail Customer Onboarding Guide.
    Signal: system setup section uses 'our systems' without naming ERP vs CRM."""

    pdf = _SopPdf(
        ref="OPS-EU-CS-GUIDE-001",
        title="Retail Customer Onboarding Guide",
        subtitle="Process Guide  |  Opella Europe  |  Commercial Operations",
        version="1.2",
        eff_date="01 May 2025",
        review_date="01 May 2026",
        classification="INTERNAL",
        doc_owner="VP Commercial Operations, Europe",
        proc_owner="Customer Service Team Lead, Europe",
    )

    pdf.cover()

    # ── Document Control ──────────────────────────────────────────────────────
    pdf.add_page()
    pdf.h1("Document Control")

    pdf.h2("Document Information")
    pdf.table(
        ["Field", "Details"],
        [
            ["Document Title",     "Retail Customer Onboarding Guide - Opella Europe"],
            ["Document Reference", "OPS-EU-CS-GUIDE-001"],
            ["Process Area",       "Customer Service / Commercial Operations"],
            ["Audience",           "Account Managers, Customer Service Team, Credit Control"],
            ["Document Owner",     "VP Commercial Operations, Europe"],
            ["Process Owner",      "Customer Service Team Lead, Europe"],
            ["Version",            "1.2"],
            ["Effective Date",     "01 May 2025"],
            ["Review Date",        "01 May 2026"],
            ["Classification",     "INTERNAL"],
        ],
        widths=[62, 106],
    )

    pdf.h2("Version History")
    pdf.table(
        ["Version", "Date", "Author", "Notes"],
        [
            ["1.2", "01 May 2025", "A. Kovacs",
             "Section 5 (System Account Setup) updated to clarify process for "
             "accounts transitioning from Sanofi. New checklist in Appendix A. "
             "EDI setup timelines updated (Section 6)."],
            ["1.1", "15 Jan 2025", "A. Kovacs",
             "Interim update: credit assessment requirements aligned to "
             "Credit Management Policy OPS-EU-FIN-POL-002 v1.2."],
            ["1.0", "01 Nov 2024", "A. Kovacs",
             "Initial Opella guide. Adapted from Sanofi account setup documentation."],
        ],
        widths=[17, 23, 28, 100],
    )

    # ── TOC ───────────────────────────────────────────────────────────────────
    pdf.add_page()
    pdf.insert_toc_placeholder(_render_toc, pages=1)
    pdf.h1("1.   Introduction")

    pdf.para(
        "This guide describes the end-to-end process for onboarding a new retail or "
        "pharmacy customer to Opella Europe. It covers every stage from initial "
        "commercial agreement through to first live order, and provides the Account "
        "Manager and Customer Service team with a single reference for what needs to "
        "happen, in what sequence, and who is responsible at each stage.\n\n"
        "A new customer is not ready to place orders until all stages in this guide "
        "are complete. Placing an order before onboarding is complete creates risk: "
        "the customer may not have a credit limit set, the system record may be "
        "incomplete, and the order confirmation process may not function correctly. "
        "The CS Team Lead must confirm account readiness before the Account Manager "
        "communicates a go-live date to the customer."
    )

    pdf.h2("1.1   Audience")
    pdf.bullets([
        "Account Managers: responsible for initiating the process, providing commercial "
        "information, and coordinating customer-side requirements.",
        "Customer Service Team Lead: responsible for system account setup and CS "
        "team readiness.",
        "Credit Controller: responsible for credit assessment and initial limit setting.",
        "Opella Digital: responsible for EDI setup (where applicable).",
    ])

    pdf.h2("1.2   New Account vs. Migrated Account")
    pdf.para(
        "This guide applies to two distinct scenarios. The process is similar in "
        "both cases, but there are important differences in the system setup and "
        "credit assessment steps:"
    )
    pdf.table(
        ["Scenario", "Description", "Key Differences"],
        [
            ["New Account",
             "A customer with no prior trading history with Opella or Sanofi.",
             "Full credit assessment required. No pre-existing system record. "
             "Longer onboarding timeline (typically 3-4 weeks)."],
            ["Migrated / Transitioning Account",
             "A customer previously served by Sanofi that is transitioning to "
             "direct Opella trading.",
             "Credit assessment may reference Sanofi trading history. System "
             "record may already exist but must be reviewed and updated. "
             "EDI connection may already be live (but may be TSA-managed)."],
        ],
        widths=[36, 70, 62],
    )

    # ── Section 2: Onboarding Stages Overview ─────────────────────────────────
    pdf.h1("2.   Onboarding Stages Overview")

    pdf.para(
        "A new retail or pharmacy account must complete the following stages before "
        "it is ready to place its first live order. The CS Team Lead tracks progress "
        "against these stages using the checklist in Appendix A."
    )
    pdf.table(
        ["Stage", "Activity", "Lead", "Typical Duration"],
        [
            ["1", "Commercial Agreement and KYC",
             "Account Manager",
             "1-2 weeks"],
            ["2", "Credit Application and Assessment",
             "Credit Controller",
             "3-5 business days"],
            ["3", "System Account Setup",
             "CS Team Lead",
             "1-2 business days"],
            ["4", "EDI / Electronic Trading Setup (if applicable)",
             "Opella Digital",
             "4-6 weeks (may run parallel to stages 1-3)"],
            ["5", "First Order Hypercare",
             "CS Representative (supervised by CS TL)",
             "First 3 orders"],
            ["6", "Account Activation",
             "CS Team Lead",
             "1 business day"],
        ],
        widths=[10, 66, 44, 48],
    )
    pdf.note(
        "SEQUENCING NOTE",
        "Stages 1, 2, and 3 must be completed in sequence. Stage 4 (EDI setup)\n"
        "can run in parallel with stages 1-3 and does not gate the account going\n"
        "live — the account can begin trading on manual/email orders while EDI\n"
        "setup completes. Stage 5 begins with the first live order."
    )

    # ── Section 3: Commercial Agreement and KYC ───────────────────────────────
    pdf.add_page()
    pdf.h1("3.   Stage 1 - Commercial Agreement and KYC")

    pdf.h2("3.1   Commercial Agreement Prerequisites")
    pdf.para(
        "Before the onboarding process starts, the Account Manager must confirm that "
        "the following are in place:"
    )
    pdf.bullets([
        "A signed commercial agreement (framework agreement, terms of trade, or "
        "purchase order terms) accepted by both parties.",
        "Agreed price list reference applicable to the account.",
        "Agreed account tier (Tier 1, 2, or 3 per Credit Management Policy "
        "OPS-EU-FIN-POL-002) and indicative credit limit expectation.",
        "Agreed standard payment terms (or Finance Director approval for any "
        "deviation from standard terms).",
        "Designated order contact and invoice contact at the customer.",
        "Confirmed delivery address(es) and any specific delivery requirements.",
    ])

    pdf.h2("3.2   Know Your Customer (KYC) Requirements")
    pdf.para(
        "Opella's legal and compliance requirements mandate KYC screening for all new "
        "trading accounts. The Account Manager initiates KYC screening by submitting "
        "the customer's legal entity details (registered name, company number, "
        "registered address, VAT number) to Finance/Compliance.\n\n"
        "KYC clearance is a prerequisite for credit assessment (Stage 2) and system "
        "account creation (Stage 3). Onboarding may not proceed until KYC clearance "
        "is confirmed in writing by Finance/Compliance."
    )

    # ── Section 4: Credit Assessment ─────────────────────────────────────────
    pdf.h1("4.   Stage 2 - Credit Assessment and Limit Setting")

    pdf.para(
        "The Account Manager submits the Credit Application Form to the Credit "
        "Controller once KYC clearance is confirmed. The full credit assessment "
        "process is governed by the Credit Management Policy (OPS-EU-FIN-POL-002, "
        "Section 3).\n\n"
        "The Account Manager should indicate the commercial context for the "
        "requested credit limit: expected annual order value, typical order size "
        "and frequency, and any commitments made to the customer about credit terms. "
        "The Credit Controller will use this information as context but the final "
        "limit is set independently under the Credit Management Policy."
    )
    pdf.note(
        "FOR MIGRATED / TRANSITIONING ACCOUNTS",
        "If the customer previously traded with Sanofi, the Credit Controller may\n"
        "request the Sanofi trading record as a reference. This information may\n"
        "be available from the Sanofi TSA. However, the Opella credit limit is\n"
        "set independently under Opella governance. The Sanofi credit limit does\n"
        "not automatically apply to the Opella account.\n\n"
        "Account Managers must NOT advise customers that their previous Sanofi\n"
        "credit limit will carry over to Opella without written Credit Controller\n"
        "confirmation."
    )

    # ── Section 5: System Account Setup ───────────────────────────────────────
    pdf.h1("5.   Stage 3 - System Account Setup")

    pdf.h2("5.1   Account Creation Responsibility")
    pdf.para(
        "The CS Team Lead is responsible for creating and configuring the new customer "
        "account in our systems. Account creation must not be delegated to a CS "
        "Representative for new accounts. The CS Team Lead must personally verify "
        "that all mandatory fields are correctly populated before the account is "
        "made available for order entry."
    )

    pdf.h2("5.2   Account Creation Process")
    pdf.numbered([
        "Receive written confirmation from the Credit Controller of the approved credit "
        "limit and agreed payment terms. Do not create the account without this "
        "confirmation.",
        "Create the customer record in our systems, populating all mandatory fields "
        "as listed in Section 5.3. The account must be created in all systems that "
        "are used for customer management and order processing. Ensure consistency "
        "of data across all systems.",
        "Attach the signed commercial agreement and the Credit Controller's credit "
        "approval to the account record.",
        "Configure the account's price list, payment terms, MOQ settings, and "
        "delivery address(es) to match the agreed commercial terms.",
        "Flag the account as 'New - Hypercare' to trigger the additional validation "
        "checks in Section 7 for the first three orders.",
        "Notify the Account Manager and CS team that the account is created and "
        "ready for order entry. Confirm the account number and any relevant notes "
        "for the CS team.",
    ])

    pdf.h2("5.3   Mandatory Account Fields")
    pdf.table(
        ["Field", "Source", "Notes"],
        [
            ["Customer Legal Name",
             "KYC documentation",
             "Must match legal entity exactly."],
            ["Customer Trading Name",
             "Commercial Agreement",
             "If different from legal name."],
            ["SAP Account Number",
             "System-generated",
             "Confirm correct number range for account type."],
            ["Company Registration Number",
             "KYC documentation",
             ""],
            ["VAT Registration Number",
             "KYC documentation",
             "Required for invoice compliance."],
            ["Account Tier",
             "Credit Controller",
             "Tier 1 / 2 / 3 per Credit Management Policy."],
            ["Credit Limit",
             "Credit Controller written approval",
             "Enter exactly as stated in Credit Controller approval. Do not adjust."],
            ["Payment Terms",
             "Credit Controller / Commercial Agreement",
             "Must match agreed terms. Finance Director approval needed for deviations."],
            ["Price List Reference",
             "Account Manager",
             "Confirm correct price list version."],
            ["Primary Delivery Address",
             "Commercial Agreement",
             "Verify postcode and country code formatting."],
            ["Order Contact Name & Email",
             "Account Manager",
             "Used for order confirmation dispatch."],
            ["Invoice Contact Name & Email",
             "Account Manager",
             "May differ from order contact."],
        ],
        widths=[52, 48, 68],
    )

    pdf.h2("5.4   Migrated / Transitioning Account Setup")
    pdf.para(
        "For customers that were previously served by Sanofi and have a pre-existing "
        "record in our systems from the carve-out migration, the CS Team Lead must "
        "review the existing record rather than creating a new one. A duplicate record "
        "must not be created.\n\n"
        "The CS Team Lead must verify that all fields in the existing record are "
        "accurate and up to date, paying particular attention to: credit limit "
        "(must reflect the Opella-approved limit, not the inherited Sanofi figure), "
        "payment terms (may have been updated for the Opella commercial relationship), "
        "and delivery addresses (confirm these are still valid for the Opella supply "
        "point). Any discrepancies must be corrected before the account is activated "
        "for Opella order entry."
    )

    # ── Section 6: EDI Setup ───────────────────────────────────────────────────
    pdf.add_page()
    pdf.h1("6.   Stage 4 - EDI and Electronic Trading Setup")

    pdf.para(
        "Stage 4 applies only to accounts that require EDI connectivity. "
        "If the account will trade via manual and email channels only, Stage 4 "
        "is not required and the onboarding moves directly to Stage 5 (Hypercare).\n\n"
        "EDI setup is managed by Opella Digital. The Account Manager notifies "
        "Opella Digital as early as possible in the onboarding process — EDI "
        "setup typically requires 4 to 6 weeks from the date technical scoping is "
        "agreed. Delays in notifying Opella Digital will delay the go-live date."
    )

    pdf.h2("6.1   EDI Scoping Requirements")
    pdf.para("The Account Manager must provide Opella Digital with the following:")
    pdf.bullets([
        "Customer's EDI provider or VAN (Value Added Network) name and contact.",
        "Required message types (ORDERS, ORDRSP, INVOIC, DESADV).",
        "Communication protocol (AS2, SFTP, or VAN routing).",
        "Customer's GLN (Global Location Number) and buyer/supplier codes.",
        "Expected go-live date and any customer-side testing requirements.",
        "For migrated accounts: current EDI connection details (if any), including "
        "whether the connection is currently managed by Sanofi Shared Services under "
        "the TSA (see EDI Integration Register OPS-EU-IT-REG-001).",
    ])

    pdf.h2("6.2   EDI Testing")
    pdf.para(
        "Before an EDI connection goes live, Opella Digital must complete a minimum "
        "of three successful end-to-end test cycles for each message type in scope. "
        "Test results must be confirmed in writing by both Opella Digital and the "
        "customer's EDI team before live orders are accepted via EDI.\n\n"
        "The Account Manager is responsible for coordinating the customer's "
        "participation in EDI testing. Opella Digital will not sign off an EDI "
        "connection as live-ready without confirmed test results from the customer side."
    )

    # ── Section 7: First Order Hypercare ──────────────────────────────────────
    pdf.h1("7.   Stage 5 - First Order Hypercare")

    pdf.para(
        "Hypercare applies to the first three orders placed by any new account. "
        "The CS Representative processes these orders with additional validation "
        "steps, supervised by the CS Team Lead."
    )
    pdf.table(
        ["Hypercare Validation Step", "When", "Standard Process"],
        [
            ["Confirm order details directly with the customer's designated order "
             "contact before processing (in addition to standard receipt procedure).",
             "Before SAP order entry.",
             "No (standard process accepts written order as received)."],
            ["Confirm delivery address against account record AND against the "
             "customer's confirmation.",
             "At order entry.",
             "No (standard process checks SAP record only)."],
            ["Credit Controller verbal confirmation that credit limit is sufficient "
             "before order entry (in addition to standard SAP check).",
             "Before SAP order entry.",
             "No (standard process uses SAP check only)."],
            ["CS Team Lead personal review of the order confirmation before issue.",
             "Before issue of confirmation.",
             "No (standard process: CS Rep issues directly)."],
        ],
        widths=[78, 36, 54],
    )
    pdf.para(
        "After three successful orders with no errors or customer queries, the CS "
        "Team Lead removes the 'Hypercare' flag from the account and it moves to "
        "standard processing. The CS Team Lead must document the transition in the "
        "account record."
    )

    # ── Section 8: Account Activation ─────────────────────────────────────────
    pdf.h1("8.   Stage 6 - Account Activation Confirmation")

    pdf.para(
        "Once Stages 1-5 are complete, the CS Team Lead confirms account activation "
        "by sending a written confirmation to the Account Manager. The confirmation "
        "must include:"
    )
    pdf.bullets([
        "SAP account number.",
        "Confirmed credit limit and payment terms.",
        "Order channels available (manual, email, EDI if applicable).",
        "CS Representative assigned as the primary contact for the account.",
        "Any account-specific notes relevant to order processing.",
    ])
    pdf.para(
        "The Account Manager may then communicate the go-live date and account "
        "details to the customer. The Account Manager must not communicate go-live "
        "to the customer before receiving the CS Team Lead's written activation "
        "confirmation."
    )

    # ── Appendix A ─────────────────────────────────────────────────────────────
    pdf.add_page()
    pdf.h1("Appendix A:   New Account Onboarding Checklist")

    pdf.para(
        "This checklist is used by the CS Team Lead to track onboarding progress. "
        "It must be completed and filed before account activation is confirmed."
    )
    pdf.table(
        ["#", "Item", "Responsibility", "Complete"],
        [
            ["1.1", "Signed commercial agreement received and filed.",
             "Account Manager", ""],
            ["1.2", "Agreed price list version confirmed.",
             "Account Manager", ""],
            ["1.3", "KYC clearance received from Finance/Compliance.",
             "Finance/Compliance", ""],
            ["2.1", "Credit Application Form submitted to Credit Controller.",
             "Account Manager", ""],
            ["2.2", "Credit assessment completed and limit confirmed in writing.",
             "Credit Controller", ""],
            ["3.1", "Customer record created / reviewed in all systems.",
             "CS Team Lead", ""],
            ["3.2", "Credit limit set exactly per Credit Controller approval.",
             "CS Team Lead", ""],
            ["3.3", "Payment terms, price list, MOQ, delivery address configured.",
             "CS Team Lead", ""],
            ["3.4", "Account flagged as 'New - Hypercare' in system.",
             "CS Team Lead", ""],
            ["4.1", "EDI scoping information submitted to Opella Digital (if applicable).",
             "Account Manager", "N/A if no EDI"],
            ["4.2", "EDI testing completed and signed off (if applicable).",
             "Opella Digital", "N/A if no EDI"],
            ["5.1", "First 3 orders processed under hypercare with no issues.",
             "CS Rep / CS TL", ""],
            ["6.1", "Account activation confirmation sent to Account Manager.",
             "CS Team Lead", ""],
        ],
        widths=[10, 84, 46, 28],
    )

    pdf.output(path)


# =============================================================================
# Doc 12 — Sanofi Consumer Healthcare O2C SOP 2023
# Signal: EDI is a documented, established channel with its own section.
#         This is the predecessor to Opella's SOP — which excluded EDI entirely.
#         Cross-referencing explains finding F2.
# =============================================================================

def generate_sanofi_o2c_sop_2023(path: str) -> None:
    """Doc 12 — ~18pp Sanofi O2C SOP 2023 (predecessor document).
    EDI fully documented as established channel with dedicated section.
    Contrasts sharply with Opella Order Management SOP which excludes EDI."""

    pdf = _SopPdf(
        ref="SCH-OPS-CS-SOP-001",
        title="Consumer Healthcare - Order-to-Cash Standard Operating Procedure",
        subtitle="Standard Operating Procedure  |  Sanofi Consumer Healthcare Division",
        version="4.0",
        eff_date="01 January 2023",
        review_date="01 January 2024",
        classification="SANOFI INTERNAL - CONFIDENTIAL",
        doc_owner="VP Consumer Healthcare Operations, Europe",
        proc_owner="Head of CS Operations, Consumer Healthcare EMEA",
        org_name="Sanofi",
        org_sub="Consumer Healthcare Division",
        brand_color=C_SANOFI,
    )

    # ── Cover ─────────────────────────────────────────────────────────────────
    pdf.cover()

    # ── Document Status Notice ─────────────────────────────────────────────────
    pdf.add_page()
    pdf.h1("Document Status and Usage Notes")

    pdf.note(
        "IMPORTANT - Document Status",
        "This document (SCH-OPS-CS-SOP-001 v4.0) was effective for Sanofi Consumer\n"
        "Healthcare EMEA operations from 1 January 2023 until the Opella carve-out\n"
        "(April 2025). It is retained as a reference document only.\n\n"
        "It is NOT authoritative for Opella operations. Opella's Order Management SOP\n"
        "(OPS-EU-CS-SOP-001 v2.1) supersedes this document for all Opella Europe order\n"
        "management activities. Personnel must not apply procedures from this document\n"
        "to Opella operations without CS Team Lead confirmation of applicability."
    )

    pdf.h2("Document Control")
    pdf.table(
        ["Field", "Details"],
        [
            ["Document Title",     "Consumer Healthcare O2C Standard Operating Procedure"],
            ["Document Reference", "SCH-OPS-CS-SOP-001"],
            ["Issuing Organisation","Sanofi Consumer Healthcare Division"],
            ["Scope",              "EMEA Consumer Healthcare Order Management Operations"],
            ["Version",            "4.0"],
            ["Effective Date",     "01 January 2023"],
            ["Status at April 2025","Superseded for Opella operations. Retained for reference."],
            ["Classification",     "SANOFI INTERNAL - CONFIDENTIAL"],
        ],
        widths=[62, 106],
    )

    pdf.h2("Version History (Sanofi)")
    pdf.table(
        ["Version", "Date", "Author", "Summary of Changes"],
        [
            ["4.0", "01 Jan 2023", "Sanofi CS Ops",
             "Updated for SAP S/4HANA migration completed Q4 2022. EDI section "
             "(Section 11) expanded. EDI active connection list (Appendix A) updated."],
            ["3.2", "01 Jun 2021", "Sanofi CS Ops",
             "EDI eligibility criteria revised. Priority EDI SLA table added."],
            ["3.0", "01 Jan 2020", "Sanofi CS Ops",
             "Consolidated EMEA regional variants into single document."],
            ["2.0", "01 Mar 2018", "Sanofi CS Ops",
             "Introduced central credit management model and single customer master."],
            ["1.0", "01 Jan 2015", "Sanofi CS Ops",
             "Initial issue."],
        ],
        widths=[17, 23, 28, 100],
    )

    # ── TOC ───────────────────────────────────────────────────────────────────
    pdf.add_page()
    pdf.insert_toc_placeholder(_render_toc, pages=1)
    pdf.h1("1.   Purpose and Scope")

    pdf.h2("1.1   Purpose")
    pdf.para(
        "This Standard Operating Procedure (SOP) defines the end-to-end process for "
        "receiving, validating, confirming, and fulfilling customer orders within "
        "Sanofi Consumer Healthcare EMEA. It applies to all Customer Service, Credit "
        "Control, and Operations personnel involved in the Order-to-Cash process.\n\n"
        "This document provides a single, consistent reference for all order management "
        "activities, covering manual, email, and Electronic Data Interchange (EDI) "
        "order channels. All three channels are documented with equal rigour; channel "
        "choice is determined by the customer's technical capability and the trading "
        "volume criteria in Section 6.3."
    )

    pdf.h2("1.2   Scope")
    pdf.bullets([
        "All Consumer Healthcare customer orders from retail pharmacy chains, "
        "hospital buying groups, specialist wholesalers, and pharmacy multiples "
        "across the EMEA region.",
        "All three order channels: manual (telephone), email, and EDI.",
        "All customer accounts in the Sanofi global SAP S/4HANA instance with a "
        "Consumer Healthcare product range.",
        "All CS Representatives, CS Team Leads, EDI Integration Specialists, "
        "Credit Controllers, Account Managers, and DC Operations personnel in scope.",
    ])

    # ── Section 2: Business Model Context ─────────────────────────────────────
    pdf.h1("2.   Business Model Context")

    pdf.para(
        "Sanofi Consumer Healthcare operates a focused product portfolio in the "
        "self-care and OTC categories, distributed through retail pharmacy chains, "
        "hospital buying groups, and specialist wholesalers across EMEA. "
        "The order profile is characterised by:"
    )
    pdf.bullets([
        "High-value, lower-frequency orders from major pharmacy chains and wholesalers, "
        "typically weekly or bi-weekly on agreed replenishment cycles.",
        "A growing proportion of EDI-based orders from accounts where the commercial "
        "relationship and order volume justify the technical investment in connectivity.",
        "A residual manual and email order base, principally from independent pharmacies "
        "and smaller specialist accounts.",
        "A very small number of fax orders from legacy accounts in certain markets, "
        "accepted under derogation from the standard channel policy.",
    ])
    pdf.para(
        "At the time of this version (v4.0), EDI accounts for approximately 60% of "
        "total order volume by value across EMEA. The strategic direction is to "
        "expand EDI connectivity to further accounts that meet the eligibility "
        "criteria in Section 6.3, with a target of 75% EDI order volume by value "
        "by end of 2024."
    )

    # ── Section 3: Definitions ─────────────────────────────────────────────────
    pdf.h1("3.   Definitions and Abbreviations")

    pdf.table(
        ["Term", "Definition"],
        [
            ["AM (Account Manager)",
             "The commercial relationship owner for a customer account."],
            ["DESADV",
             "Despatch Advice: EDIFACT message sent to the customer confirming "
             "that goods have been despatched, including shipment details."],
            ["EDI (Electronic Data Interchange)",
             "The electronic exchange of standardised business documents "
             "(purchase orders, confirmations, invoices) between Sanofi and "
             "trading partners using the EDIFACT standard."],
            ["GLN (Global Location Number)",
             "A unique identifier assigned to a trading location, used in EDI "
             "messages to identify the sender and receiver."],
            ["INVOIC",
             "Invoice: EDIFACT message sent to the customer following despatch, "
             "constituting the formal invoice."],
            ["MOQ (Minimum Order Quantity)",
             "The minimum quantity of a given SKU accepted per order line."],
            ["ORDERS",
             "Purchase Order: EDIFACT message received from the trading partner "
             "containing the customer's purchase order."],
            ["ORDRSP",
             "Order Response: EDIFACT message sent by Sanofi to confirm, amend, "
             "or reject a received ORDERS message."],
            ["SAP S/4HANA",
             "Sanofi's global ERP system. The single source of truth for all "
             "customer accounts, credit limits, inventory, and order processing."],
            ["TSA",
             "Transition Services Agreement: agreement under which Sanofi provides "
             "defined services to carve-out entities post-separation."],
            ["VAN (Value Added Network)",
             "A third-party network provider that routes EDI messages between "
             "trading partners where direct AS2 connectivity is not in place."],
        ],
        widths=[42, 126],
    )

    # ── Section 4: Roles ───────────────────────────────────────────────────────
    pdf.add_page()
    pdf.h1("4.   Roles and Responsibilities")

    pdf.table(
        ["Role", "Responsibility Summary"],
        [
            ["CS Representative",
             "Day-to-day order processing across all channels (manual, email, EDI "
             "exception handling). First-line customer queries. Order confirmation "
             "and monitoring."],
            ["CS Team Lead",
             "Team management and quality oversight. Second-level escalation. "
             "Process documentation. Monthly KPI reporting."],
            ["EDI Integration Specialist",
             "Technical management of all EDI connections: onboarding new trading "
             "partners, monitoring connection health, resolving message failures, "
             "and liaising with Sanofi IT."],
            ["Credit Controller",
             "Customer credit limit maintenance (SAP S/4HANA). Credit hold decisions "
             "and releases. Overdue collections. Monthly AR reporting."],
            ["Account Manager",
             "Commercial relationship ownership. Credit review requests. EDI "
             "connectivity coordination. Strategic customer escalation."],
            ["Sanofi Shared Services - IT (EDI)",
             "Platform management for EDI infrastructure (SAP Integration Suite). "
             "Tier 2 incident support. Trading partner technical onboarding."],
            ["DC Operations",
             "Order fulfilment: pick, pack, despatch. Partial shipment notification. "
             "Short delivery investigation."],
        ],
        widths=[52, 116],
    )

    # ── Section 5: Customer Master Data ───────────────────────────────────────
    pdf.h1("5.   Customer Master Data")

    pdf.h2("5.1   Single Source of Truth")
    pdf.para(
        "All customer master data — including account status, credit limits, "
        "payment terms, price lists, delivery addresses, and EDI configuration — "
        "is maintained centrally in the Sanofi global SAP S/4HANA instance by "
        "Sanofi Shared Services Master Data. There is a single record per customer "
        "entity. Local market teams do not maintain separate customer records or "
        "credit limit overrides in any other system.\n\n"
        "This single-record architecture ensures that the credit limit used for "
        "order release decisions is always current and consistent regardless of the "
        "order channel. CS Representatives performing order validation do not need "
        "to cross-check credit data across multiple systems."
    )

    pdf.h2("5.2   Authorised Master Data Changes")
    pdf.para(
        "All customer master data changes require submission through the Sanofi "
        "Master Data workflow in SAP S/4HANA. Changes are reviewed by Sanofi "
        "Shared Services Master Data before taking effect. Ad hoc manual updates "
        "outside the workflow are not permitted and will be reversed.\n\n"
        "Credit limit changes specifically require Credit Management team "
        "approval (for standard limits) or European Credit Director approval "
        "(for limits above EUR 500,000 or for emergency intra-year increases "
        "above EUR 200,000). Account Managers do not have authority to modify "
        "credit limits."
    )

    # ── Section 6: Order Receipt ────────────────────────────────────────────────
    pdf.add_page()
    pdf.h1("6.   Order Receipt")

    pdf.h2("6.1   Approved Order Channels")
    pdf.para(
        "Sanofi Consumer Healthcare EMEA accepts customer orders through three "
        "approved channels. The appropriate channel for each account is determined "
        "by the EDI eligibility criteria in Section 6.3 and is documented in the "
        "customer's SAP account record."
    )
    pdf.table(
        ["Channel", "Description", "Order Volume at Version 4.0"],
        [
            ["EDI",
             "Fully automated order receipt via EDIFACT ORDERS message. "
             "Orders flow directly into SAP S/4HANA without manual intervention. "
             "Real-time ORDRSP confirmation returned.",
             "Approximately 60% of order volume by value."],
            ["Email",
             "Written orders received to the designated regional order mailbox. "
             "Manually entered into SAP by CS Representative within one business day.",
             "Approximately 30% of order volume by value."],
            ["Manual / Telephone",
             "Orders placed verbally and entered into SAP by CS Representative "
             "during or immediately after the call.",
             "Approximately 10% of order volume by value."],
        ],
        widths=[34, 90, 44],
    )

    pdf.h2("6.2   Manual and Email Order Processing")
    pdf.para(
        "The manual and email order processes follow standard CS procedures. "
        "The CS Representative is responsible for all validation steps in Section 7 "
        "before confirming the order to the customer."
    )
    pdf.numbered([
        "Receipt: acknowledge receipt to the customer within two business hours of "
        "order arrival (telephone: immediate; email: written acknowledgement).",
        "Information capture: confirm all required order details (account number, "
        "SKU(s), quantities, delivery address, customer PO reference, requested "
        "delivery date).",
        "SAP entry: enter the order in SAP S/4HANA. For telephone orders: within "
        "30 minutes of call end. For email orders: within one business day of receipt.",
        "Validation: complete all steps in Section 7.",
        "Confirmation: issue formal confirmation within the timelines in Section 8.",
    ])

    pdf.h2("6.3   EDI Order Processing")
    pdf.para(
        "EDI orders arrive in SAP S/4HANA automatically via the Sanofi EDI platform "
        "(SAP Integration Suite). Under standard conditions, EDI orders pass through "
        "the automated validation rules in SAP without CS intervention and are "
        "confirmed via an automated ORDRSP message.\n\n"
        "The CS Representative is responsible for monitoring the EDI order queue "
        "for exception messages: orders that have failed automated validation and "
        "require manual intervention. Exceptions are flagged in the SAP worklist "
        "and must be resolved within four business hours of appearing."
    )

    pdf.h2("6.4   EDI Eligibility Criteria")
    pdf.para(
        "EDI connectivity is available to accounts that meet the following criteria:"
    )
    pdf.bullets([
        "Annual order value with Sanofi Consumer Healthcare exceeding EUR 5 million "
        "at current or projected run rate.",
        "Order frequency of at least three purchase orders per week on a regular cadence.",
        "Dedicated EDI technical capability at the trading partner (internal EDI team "
        "or third-party VAN provider).",
        "Willingness to complete Sanofi's EDI onboarding and testing process, "
        "including a minimum of three full message cycle tests before going live.",
    ])
    pdf.para(
        "EDI connectivity is available as a service for accounts below the EUR 5M "
        "threshold where the Account Manager makes a business case and the EDI "
        "Integration Specialist confirms technical feasibility. Such cases require "
        "VP Consumer Healthcare Operations approval."
    )

    # ── Section 7: Order Validation ────────────────────────────────────────────
    pdf.add_page()
    pdf.h1("7.   Order Validation")

    pdf.para(
        "All orders — regardless of channel — must pass the following validation "
        "sequence before confirmation. EDI orders are validated automatically by "
        "SAP S/4HANA rules; exceptions require manual CS intervention. Manual and "
        "email orders are validated by the CS Representative in SAP."
    )
    pdf.table(
        ["Validation Step", "EDI (Automated)", "Manual / Email (CS Rep)"],
        [
            ["Account status check",
             "SAP rule: blocks ORDRSP if account not Active.",
             "CS Rep verifies account status in SAP before entry."],
            ["Credit limit check",
             "SAP rule: places order on credit hold if limit exceeded.",
             "CS Rep checks outstanding balance + order value vs. limit."],
            ["Product availability",
             "SAP rule: flags exception if DC stock < ordered quantity.",
             "CS Rep checks DC inventory in SAP."],
            ["MOQ compliance",
             "SAP rule: flags exception if quantity < MOQ.",
             "CS Rep verifies MOQ before entry."],
            ["Pricing validation",
             "SAP rule: flags exception if price deviates > 1% from price list.",
             "CS Rep confirms price list reference with AM if discrepancy found."],
        ],
        widths=[44, 62, 62],
    )

    # ── Section 8: Order Confirmation ──────────────────────────────────────────
    pdf.h1("8.   Order Confirmation")

    pdf.h2("8.1   Confirmation Methods by Channel")
    pdf.table(
        ["Channel", "Confirmation Method", "Timeline"],
        [
            ["EDI",
             "Automated ORDRSP message sent directly to the trading partner's EDI "
             "platform within 30 minutes of order receipt (automated SAP process). "
             "Exception ORDRSP (accepting with amendments) sent within 2 hrs of "
             "exception resolution.",
             "30 minutes (automated); 2 hrs (exceptions)."],
            ["Email",
             "Email reply to the original order email, attaching the SAP order "
             "confirmation as a PDF.",
             "Within 2 business hours of SAP order entry."],
            ["Manual",
             "Email to the customer's order contact, attaching SAP confirmation PDF. "
             "Verbal confirmation of key details at end of call.",
             "Within 4 business hours of call."],
        ],
        widths=[20, 102, 46],
    )

    # ── Section 9: Order Fulfilment ─────────────────────────────────────────────
    pdf.h1("9.   Order Fulfilment and Despatch")

    pdf.h2("9.1   Release to Distribution")
    pdf.para(
        "Orders confirmed to customers are released automatically to the allocated "
        "Distribution Centre in SAP S/4HANA following successful credit and inventory "
        "validation. For EDI orders, release is automatic. For manual and email orders, "
        "the CS Representative releases the confirmed order in SAP."
    )

    pdf.h2("9.2   Standard Lead Times")
    pdf.table(
        ["Market", "Lead Time (Business Days)", "Primary DC"],
        [
            ["France",               "2", "Chartres, FR"],
            ["United Kingdom",       "3", "Reading, UK (Sanofi CS DC)"],
            ["Germany",              "2", "Frankfurt, DE"],
            ["Spain / Portugal",     "3", "Barcelona, ES"],
            ["Benelux",              "2", "Antwerp, BE"],
            ["Italy",                "3", "Milan, IT (3PL managed)"],
            ["Rest of EMEA",         "3-5", "Market-specific."],
        ],
        widths=[50, 30, 88],
    )

    # ── Section 10: Invoicing ──────────────────────────────────────────────────
    pdf.add_page()
    pdf.h1("10.   Invoicing")

    pdf.h2("10.1   Invoice Generation")
    pdf.para(
        "Invoices are generated automatically in SAP S/4HANA upon despatch "
        "confirmation from the DC. For EDI-enabled accounts, the invoice is also "
        "transmitted electronically as an INVOIC message via the EDI platform "
        "within one hour of SAP invoice generation. For non-EDI accounts, the "
        "invoice is dispatched by email as a PDF attachment."
    )

    pdf.h2("10.2   Payment Terms")
    pdf.table(
        ["Account Type", "Standard Payment Terms"],
        [
            ["Major Retail Pharmacy Chains",  "NET 45 days from invoice date."],
            ["Hospital Buying Groups",        "NET 45 days from invoice date."],
            ["Wholesalers",                   "NET 30 days from invoice date."],
            ["Independent Pharmacies",        "NET 30 days from invoice date."],
        ],
        widths=[70, 98],
    )

    # ── Section 11: EDI Programme (dedicated section — the key contrast) ───────
    pdf.h1("11.   EDI Programme")

    pdf.h2("11.1   Programme Overview")
    pdf.para(
        "The EDI programme is a strategic initiative to maximise the proportion of "
        "Sanofi Consumer Healthcare orders transacted electronically. The programme "
        "is owned by the CS Operations function and delivered by the EDI Integration "
        "team in partnership with Sanofi Shared Services IT.\n\n"
        "As of January 2023, 34 active EDI connections are live across the EMEA "
        "region, processing approximately 60% of order volume by value. The "
        "programme target is 75% by end of 2024, requiring the onboarding of "
        "approximately 8-10 additional accounts."
    )

    pdf.h2("11.2   Active EDI Connections — EMEA (Selected)")
    pdf.para(
        "The full EDI active connection list is maintained in the Sanofi Shared "
        "Services EDI Connection Register (Appendix A contains a representative "
        "extract). The register is maintained by the EDI Integration team and "
        "reviewed quarterly."
    )
    pdf.table(
        ["Market", "Trading Partner", "Messages", "Annual Volume (EUR M)", "Priority SLA"],
        [
            ["FR", "Carrefour France",    "ORDERS/ORDRSP/INVOIC", "38.2", "4 hrs"],
            ["FR", "E.Leclerc",           "ORDERS/ORDRSP/DESADV", "22.7", "4 hrs"],
            ["UK", "Boots UK",            "ORDERS/ORDRSP/INVOIC", "29.4", "4 hrs"],
            ["DE", "dm (Drogerie Markt)", "ORDERS/ORDRSP",        "16.8", "8 hrs"],
            ["DE", "REWE Group",          "ORDERS/ORDRSP",        "11.2", "8 hrs"],
            ["EU", "Lidl Europe",         "ORDERS/ORDRSP",        "18.9", "4 hrs"],
            ["UK", "Tesco UK",            "ORDERS/ORDRSP/DESADV/INVOIC", "24.1", "4 hrs"],
            ["EU", "Alliance Healthcare", "ORDERS/DESADV",        "13.4", "8 hrs"],
        ],
        widths=[14, 42, 44, 30, 38],
    )

    pdf.h2("11.3   EDI Incident Management")
    pdf.para(
        "EDI connection incidents are managed by the Sanofi IT helpdesk (EDI "
        "support line: contact details in Appendix B). The following SLAs apply:"
    )
    pdf.table(
        ["Priority", "Trigger", "Response SLA", "Resolution SLA"],
        [
            ["Priority 1",
             "EDI connection fully down for an account with annual volume > EUR 10M.",
             "30 minutes",
             "4 business hours"],
            ["Priority 2",
             "Intermittent failures or message errors on any active EDI connection.",
             "2 hours",
             "1 business day"],
            ["Priority 3",
             "Non-urgent issues: mapping queries, configuration changes, "
             "new partner setup questions.",
             "1 business day",
             "5 business days"],
        ],
        widths=[22, 72, 34, 40],
    )
    pdf.para(
        "CS Representatives must not contact trading partner EDI teams directly "
        "for connection issues. All EDI incidents must be logged through the "
        "Sanofi IT helpdesk. The EDI Integration Specialist will manage the "
        "incident and provide regular status updates to the CS Team Lead."
    )

    pdf.h2("11.4   EDI Onboarding for New Accounts")
    pdf.para(
        "The EDI onboarding process for a new trading partner takes approximately "
        "6-8 weeks from the date scoping is agreed. The Account Manager initiates "
        "onboarding by submitting the EDI Onboarding Request form to the EDI "
        "Integration team, with technical details from the trading partner. "
        "Test cycles must be completed successfully before go-live."
    )

    # ── Section 12: Credit Management ─────────────────────────────────────────
    pdf.h1("12.   Credit Management")

    pdf.para(
        "Customer credit limits are maintained centrally in SAP S/4HANA by the "
        "Sanofi Credit Management team. There is no secondary credit system. "
        "The SAP credit limit is the authoritative figure for all order release "
        "decisions, regardless of the order channel.\n\n"
        "For EDI orders, credit hold status is assessed automatically by SAP on "
        "receipt of the ORDERS message. A held order triggers an automated "
        "exception flag in the CS worklist. The CS Representative notifies the "
        "Credit Controller within four business hours of a credit hold exception."
    )

    # ── Section 13: Escalation ─────────────────────────────────────────────────
    pdf.h1("13.   Escalation and Dispute Resolution")

    pdf.h2("13.1   Order Processing Escalation")
    pdf.table(
        ["Level", "Role", "Escalation Trigger", "Target Response"],
        [
            ["1", "CS Representative",
             "Standard order queries within SOP scope.",
             "Immediate."],
            ["2", "CS Team Lead",
             "Non-standard orders. Queries unresolved at Level 1 in 4 hrs. "
             "EDI exceptions unresolved in 4 hrs. Credit holds unresolved.",
             "2 business hours."],
            ["3", "VP Consumer Healthcare Operations",
             "Strategic account service failure. Revenue impact > EUR 100K. "
             "Regulatory or compliance implications.",
             "4 business hours."],
        ],
        widths=[10, 44, 76, 38],
    )

    pdf.h2("13.2   EDI-Specific Escalation")
    pdf.para(
        "For EDI connection failures affecting order processing, the CS Team Lead "
        "has authority to approve a temporary switch to manual/email order processing "
        "for the affected account while the EDI incident is being resolved. This "
        "decision must be communicated to the Account Manager and documented in SAP."
    )

    # ── Section 14: Compliance ─────────────────────────────────────────────────
    pdf.h1("14.   Compliance and Audit")

    pdf.para(
        "Compliance with this SOP is mandatory. Annual internal audit covers: order "
        "confirmation timeliness across all channels, EDI exception resolution times, "
        "credit hold governance and release documentation, and SAP order record "
        "completeness for non-standard decisions.\n\n"
        "This SOP is subject to annual review by the Global Consumer Healthcare "
        "Operations team. Changes require sign-off from the VP Consumer Healthcare "
        "Operations, Europe."
    )

    # ── Appendix A: EDI Connection Extract ────────────────────────────────────
    pdf.add_page()
    pdf.h1("Appendix A:   EDI Active Connection List (EMEA Extract)")

    pdf.para(
        "The following is a representative extract from the Sanofi Shared Services "
        "EDI Connection Register as at January 2023. The full register (34 active "
        "connections) is maintained by the EDI Integration team."
    )
    pdf.table(
        ["#", "Market", "Trading Partner", "Msg Types", "Protocol", "Annual Vol (EUR M)"],
        [
            ["1",  "FR", "Carrefour France",     "ORDERS/ORDRSP/INVOIC",       "AS2",  "38.2"],
            ["2",  "FR", "E.Leclerc",            "ORDERS/ORDRSP/DESADV",       "SFTP", "22.7"],
            ["3",  "UK", "Boots UK",             "ORDERS/ORDRSP/INVOIC",       "AS2",  "29.4"],
            ["4",  "UK", "Tesco UK",             "ORDERS/ORDRSP/DESADV/INVOIC","AS2",  "24.1"],
            ["5",  "DE", "dm (Drogerie Markt)",  "ORDERS/ORDRSP",              "VAN",  "16.8"],
            ["6",  "DE", "REWE Group",           "ORDERS/ORDRSP",              "AS2",  "11.2"],
            ["7",  "EU", "Lidl Europe",          "ORDERS/ORDRSP",              "AS2",  "18.9"],
            ["8",  "EU", "Alliance Healthcare",  "ORDERS/DESADV",              "SFTP", "13.4"],
            ["9",  "ES", "Mercadona",            "ORDERS/ORDRSP",              "AS2",  "9.7"],
            ["10", "EU", "Aldi Europe",          "ORDERS",                     "VAN",  "8.1"],
            ["11", "BE", "Delhaize Group",       "ORDERS/ORDRSP/INVOIC",       "AS2",  "7.3"],
            ["12", "EU", "Coop Group",           "ORDERS/INVOIC",              "SFTP", "6.2"],
        ],
        widths=[8, 14, 42, 46, 20, 38],
    )

    # ── Appendix B: Key Contacts ───────────────────────────────────────────────
    pdf.h1("Appendix B:   Key Contact Directory (Sanofi CS - EMEA)")

    pdf.table(
        ["Role", "Name / Team", "Contact"],
        [
            ["Head of CS Operations, Consumer Healthcare EMEA",
             "A. Laurent",
             "a.laurent@sanofi.com"],
            ["CS Team Lead, EMEA North (UK/IE)",
             "CS Team UK",
             "cs.uk@sanofi.com"],
            ["CS Team Lead, EMEA West (FR/BE/NL/LU)",
             "CS Team FR",
             "cs.fr@sanofi.com"],
            ["CS Team Lead, EMEA Central (DE/AT/CH)",
             "CS Team DE",
             "cs.de@sanofi.com"],
            ["EDI Integration Lead",
             "Sanofi Shared Services EDI",
             "edi.support@sanofi.com"],
            ["Sanofi IT Helpdesk (EDI)",
             "IT Helpdesk",
             "+33 1 53 77 40 00, Option 3"],
            ["Credit Management Team",
             "Credit Management EMEA",
             "credit.emea@sanofi.com"],
        ],
        widths=[68, 44, 56],
    )

    pdf.output(path)
