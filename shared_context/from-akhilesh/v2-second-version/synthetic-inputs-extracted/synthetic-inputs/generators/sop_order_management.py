"""
Professional Order Management SOP generator for Opella Europe.
Produces a ~14-page PDF with cover, document control, auto-linked TOC,
structured sections/sub-sections, tables, note boxes, and page headers/footers.

Finding seeded: F2 -- SOP covers only manual and email orders (zero EDI mention),
despite EDI representing ~67% of actual order volume.
"""
import os, sys
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
from generators.sop_utils import (
    FONT, C_NAVY, C_BLUE, C_ACCENT, C_GRAY, C_LGRAY, C_NOTE, C_WHITE, C_BLACK,
    _s, _SopPdf, _render_toc,
)


# ── Main generator function ───────────────────────────────────────────────────

def generate_order_management_sop(path: str) -> None:
    """
    Doc 01 - Order Management SOP, Opella Europe.
    ~14 pages. Cover + document control + TOC + 11 sections + 2 appendices.
    F2 signal: zero EDI mention in any section (noted as out of scope).
    """
    pdf = _SopPdf(
        ref="OPS-EU-CS-SOP-001",
        title="Order Management",
        subtitle="Standard Operating Procedure  |  Opella Europe  |  Commercial Operations",
        version="2.1",
        eff_date="01 June 2025",
        review_date="01 June 2026",
        classification="INTERNAL",
        doc_owner="VP Commercial Operations, Europe",
        proc_owner="Customer Service Team Lead, Europe",
    )

    # ── 1. COVER ──────────────────────────────────────────────────────────────
    pdf.cover()

    # ── 2. DOCUMENT CONTROL ───────────────────────────────────────────────────
    pdf.add_page()
    pdf.h1("Document Control")

    pdf.h2("Document Information")
    pdf.table(
        ["Field", "Details"],
        [
            ["Document Title",    "Order Management - Standard Operating Procedure"],
            ["Document Reference","OPS-EU-CS-SOP-001"],
            ["Process Area",      "Customer Service / Order-to-Cash"],
            ["Business Unit",     "Commercial Operations, Opella Europe"],
            ["Document Owner",    "VP Commercial Operations, Europe"],
            ["Process Owner",     "Customer Service Team Lead, Europe"],
            ["Version",           "2.1"],
            ["Effective Date",    "01 June 2025"],
            ["Review Date",       "01 June 2026"],
            ["Classification",    "INTERNAL"],
        ],
        widths=[62, 106],
    )

    pdf.h2("Approval and Authorisation")
    pdf.table(
        ["Role", "Name", "Signature", "Date"],
        [
            ["VP Commercial Operations, Europe",      "Sophie Marchetti", "Approved", "28 May 2025"],
            ["Finance Director, Europe",              "Marc Dupont",      "Approved", "26 May 2025"],
            ["Customer Service Team Lead, Europe",    "Alina Kovacs",     "Reviewed", "22 May 2025"],
            ["Legal & Compliance, Europe",            "Isabelle Fontaine","Noted",    "20 May 2025"],
        ],
        widths=[68, 42, 28, 30],
    )

    pdf.h2("Version History")
    pdf.table(
        ["Version", "Date", "Author", "Summary of Changes"],
        [
            ["2.1", "01 Jun 2025", "A. Kovacs",
             "Annual review. Section 4.5 (Non-Standard Orders) added. Credit hold notification timeline "
             "updated from 8 hrs to 4 hrs per Finance Director instruction. Escalation contacts refreshed."],
            ["2.0", "01 Apr 2025", "A. Kovacs",
             "Initial Opella version. Adapted from Sanofi Consumer Healthcare SOP v4.0 (Jan 2023). "
             "Scope, org structure, and system references updated for Opella post-carve-out operating model."],
            ["1.0 (Sanofi)", "01 Jan 2023", "Sanofi CS Ops",
             "Sanofi Consumer Healthcare inherited reference document. Superseded at Opella carve-out "
             "and no longer authoritative for Opella operations."],
        ],
        widths=[17, 23, 28, 100],
    )

    pdf.h2("Related Documents")
    pdf.table(
        ["Reference", "Title", "Ver"],
        [
            ["OPS-EU-FIN-POL-002", "Credit Management Policy - Opella Europe",                        "1.3"],
            ["OPS-EU-CS-SOP-002",  "Returns and Credits - Standard Operating Procedure",              "1.1"],
            ["OPS-EU-CS-SOP-003",  "Export Orders - Standard Operating Procedure",                    "1.0"],
            ["OPS-EU-CS-RACI-001", "Order-to-Cash Process RACI Matrix - Opella Europe",               "1.0"],
            ["OPS-EU-LOG-SOP-001", "Distribution Centre Operations - Standard Operating Procedure",   "2.0"],
            ["OPS-EU-IT-WN-001",   "EDI Dispute Resolution - Working Notes (A. Kovacs, informal)",    "N/A"],
        ],
        widths=[50, 98, 20],
    )

    # ── 3. TABLE OF CONTENTS (placeholder - filled at output time) ────────────
    pdf.add_page()
    pdf.insert_toc_placeholder(_render_toc, pages=1)
    # insert_toc_placeholder already performs its own page break internally

    # ── 4. SECTION 1 - PURPOSE AND SCOPE ─────────────────────────────────────
    pdf.h1("1.   Purpose and Scope")

    pdf.h2("1.1   Purpose")
    pdf.para(
        "This Standard Operating Procedure (SOP) establishes the authoritative process "
        "for receiving, validating, confirming, and fulfilling customer orders across "
        "Opella Europe. It provides a single, consistent reference for all personnel "
        "involved in the Order-to-Cash (O2C) process, from order receipt through to "
        "despatch confirmation and invoice issuance.\n\n"
        "This document supersedes the Sanofi Consumer Healthcare Order Management SOP "
        "(version 4.0, effective January 2023). It has been adapted to reflect Opella's "
        "post-carve-out operating model, revised organisational structure, and European "
        "commercial footprint. Adherence to this SOP is mandatory for all personnel "
        "listed in Section 3 (Roles and Responsibilities)."
    )

    pdf.h2("1.2   Scope")
    pdf.para("This SOP applies to all of the following:")
    pdf.bullets([
        "Customer orders received from retail, pharmacy, and wholesale accounts within "
        "the Opella Europe commercial region, covering France, United Kingdom, Germany, "
        "Spain, Italy, Benelux, Austria, Switzerland, and wider EMEA markets where "
        "Opella Europe holds commercial responsibility.",
        "All Customer Service Representatives, Customer Service Team Leads, Credit "
        "Controllers, and Account Managers involved in any stage of order processing.",
        "All order management activities conducted within SAP S/4HANA for Opella Europe "
        "accounts, including order entry, validation, release, and exception handling.",
        "Manual (telephone) and email order channels as defined in Section 4.",
    ])

    pdf.h2("1.3   Exclusions")
    pdf.para("The following are explicitly outside the scope of this SOP:")
    pdf.bullets([
        "Direct-to-pharmacy distribution managed by local market co-manufacturing "
        "partners or third-party logistics providers under separate service agreements.",
        "Transfer orders between Opella manufacturing sites and distribution centres, "
        "which are governed by Supply Chain SOPs.",
        "Export orders to markets outside the defined Opella Europe region, covered by "
        "OPS-EU-CS-SOP-003.",
        "Electronic Data Interchange (EDI) channel operations. EDI is not covered by "
        "this version of the SOP. EDI represents a material share of total order volume "
        "but formal process documentation is under development. Personnel handling EDI "
        "queries should refer to the interim working notes (OPS-EU-IT-WN-001).",
    ])

    pdf.note(
        "NOTE - EDI Exclusion",
        "Electronic Data Interchange (EDI) order processing is outside the scope of this SOP.\n"
        "A formal EDI SOP is under development (target: Q3 2025). Until published, all EDI\n"
        "operational queries must be directed to the CS Team Lead (A. Kovacs) or Opella Digital\n"
        "(J. Okafor). Do not apply this SOP's validation or confirmation procedures to EDI\n"
        "orders without explicit instruction from the CS Team Lead."
    )

    pdf.h2("1.4   Regulatory and Policy Context")
    pdf.para(
        "Opella Europe operates as a standalone commercial entity following its legal and "
        "operational separation from Sanofi, effective April 2025. Customer data, credit "
        "terms, and order processes are governed by Opella's own policies and are not "
        "subject to Sanofi group policies unless explicitly carried over and confirmed "
        "under Opella governance.\n\n"
        "Personnel must not rely on Sanofi-originated system configurations, credit data, "
        "or process documentation without confirming that these have been reviewed, "
        "validated, and accepted under Opella's governance framework. In particular, credit "
        "limits inherited from the Sanofi customer master should be validated against the "
        "current Opella Credit Management Policy (OPS-EU-FIN-POL-002) before being applied "
        "to order release decisions."
    )

    # ── SECTION 2 - DEFINITIONS ───────────────────────────────────────────────
    pdf.h1("2.   Definitions and Abbreviations")

    pdf.table(
        ["Term / Abbreviation", "Definition"],
        [
            ["Account Manager (AM)",
             "The commercial relationship owner for a customer account. Responsible for "
             "commercial escalations and credit limit review requests."],
            ["Credit Hold",
             "A system-triggered or manually applied restriction preventing order release "
             "pending credit authorisation from the Credit Controller."],
            ["Credit Limit",
             "The maximum aggregate outstanding balance approved for a customer account "
             "at any given time, as maintained in SAP S/4HANA."],
            ["CSR (Customer Service Representative)",
             "The team member responsible for day-to-day order processing, validation, "
             "confirmation, and first-line customer query resolution."],
            ["DC (Distribution Centre)",
             "An Opella warehouse facility responsible for picking, packing, and despatch "
             "of customer orders."],
            ["MOQ (Minimum Order Quantity)",
             "The minimum unit volume accepted for a given SKU or account tier, as "
             "configured in SAP S/4HANA."],
            ["O2C (Order-to-Cash)",
             "The end-to-end process from customer order receipt through to cash "
             "collection, encompassing order management, fulfilment, invoicing, and AR."],
            ["SAP S/4HANA",
             "Opella's primary ERP system. The authoritative source of record for customer "
             "accounts, credit limits, inventory availability, and order processing."],
            ["SKU (Stock Keeping Unit)",
             "A unique product identifier used for inventory management and order entry."],
            ["TSA (Transition Services Agreement)",
             "The agreement under which Sanofi continues to provide defined services to "
             "Opella during the carve-out transition period."],
        ],
        widths=[48, 120],
    )

    # ── SECTION 3 - ROLES AND RESPONSIBILITIES ────────────────────────────────
    pdf.h1("3.   Roles and Responsibilities")

    pdf.para(
        "This section defines the responsibilities of each role in the order management "
        "process. Detailed RACI mapping (Responsible / Accountable / Consulted / Informed) "
        "is available in OPS-EU-CS-RACI-001."
    )

    pdf.h2("3.1   Customer Service Representative (CSR)")
    pdf.bullets([
        "Receipt and accurate entry of all manual and email orders into SAP S/4HANA.",
        "Completion of all pre-release validation checks as defined in Section 5: account "
        "status, credit limit, product availability, MOQ, and pricing.",
        "Issuance of order confirmations within the timelines defined in Section 6.",
        "Monitoring of orders from confirmation through to despatch confirmation.",
        "First-line resolution of order queries received from customers.",
        "Escalation of all non-standard situations to the CS Team Lead within the "
        "timelines defined in Section 9.",
        "Accurate documentation of all non-standard decisions and exceptions in the SAP "
        "order record.",
    ])

    pdf.h2("3.2   Customer Service Team Lead")
    pdf.para(
        "Currently: Alina Kovacs. The CS Team Lead provides operational oversight of the "
        "CS function and is the primary internal escalation point."
    )
    pdf.bullets([
        "Day-to-day management and quality oversight of the CS team.",
        "Second-level escalation for order queries not resolved at CSR level within "
        "four business hours.",
        "Authorisation of exceptions to standard order processing procedures, with "
        "documented rationale in the relevant SAP order record.",
        "Liaison with Credit Control, Account Management, and DC Operations on "
        "cross-functional order issues.",
        "Maintenance and periodic review of this SOP and related process documentation.",
        "Monthly reporting on CS KPIs to the VP Commercial Operations, Europe.",
    ])

    pdf.h2("3.3   Credit Controller")
    pdf.para(
        "Currently: Raj Patel (UK & Europe). The Credit Controller owns all credit-related "
        "decisions within the order process."
    )
    pdf.bullets([
        "Review and release (or rejection) of orders on credit hold within the timelines "
        "defined in Section 5.3.",
        "Maintenance of customer credit limits in SAP S/4HANA as the system of record.",
        "Annual review of credit limits for all accounts in scope.",
        "Monthly reporting on credit exposure, overdue accounts, and credit hold volumes "
        "to the Finance Director.",
        "Escalation of material credit risk situations to the Finance Director without delay.",
    ])

    pdf.h2("3.4   Account Manager (AM)")
    pdf.bullets([
        "First point of commercial contact for customer escalations: service level "
        "concerns, credit disputes, threatened delistings.",
        "Provision of commercial context to the Credit Controller and CS Team Lead when "
        "credit or service issues arise on strategic accounts.",
        "Submission of formal credit limit review requests with supporting trading data.",
        "Notification to CS Team Lead when a new account is ready to place its first order.",
        "Approval of MOQ exceptions (within two business hours of CSR notification).",
    ])

    pdf.h2("3.5   Distribution Centre (DC) Operations")
    pdf.bullets([
        "Receipt and acknowledgement of released orders from SAP.",
        "Processing of orders within the standard lead times defined in Section 7.2.",
        "Prompt notification to the CSR of despatch confirmation, partial shipment, or "
        "fulfilment exception.",
        "Investigation and response to short-delivery claims within three business days.",
    ])

    # ── SECTION 4 - ORDER RECEIPT ─────────────────────────────────────────────
    pdf.add_page()
    pdf.h1("4.   Order Receipt")

    pdf.h2("4.1   Approved Order Channels")
    pdf.para(
        "Opella Europe accepts customer purchase orders through the following two "
        "approved channels. Other methods (fax, web portal, electronic messaging) are "
        "only accepted where explicitly agreed with the CS Team Lead and documented in "
        "the customer account record in SAP S/4HANA."
    )
    pdf.table(
        ["Channel", "Description", "SAP Entry Method"],
        [
            ["Telephone / Manual",
             "Orders placed verbally by telephone by an authorised customer representative.",
             "Direct entry into SAP S/4HANA by the CSR during or immediately after the call."],
            ["Email",
             "Written orders received to the designated regional order mailbox.",
             "Entry into SAP S/4HANA by CSR within one business day of email receipt."],
        ],
        widths=[36, 76, 56],
    )

    pdf.h2("4.2   Telephone / Manual Order Processing")
    pdf.para(
        "When a telephone order is received, the CSR shall complete the following steps "
        "in sequence:"
    )
    pdf.numbered([
        "Identify the caller and confirm they are listed as an authorised order contact "
        "for the account in SAP. If the caller is not listed, do not accept the order. "
        "Request them to arrange authorisation through their Account Manager.",
        "Record the following information before confirming receipt: customer account "
        "name and SAP account number; product SKU(s), product descriptions, and "
        "quantities requested; requested delivery date; delivery address (verify against "
        "SAP account record); and customer purchase order (PO) reference number.",
        "Verbally confirm the full order details back to the caller before ending the "
        "call. Confirm the expected order confirmation timeline.",
        "Enter the order into SAP S/4HANA within 30 minutes of the call ending, "
        "provided no simultaneous customer contacts prevent immediate entry. If "
        "entry is delayed, note the delay reason in the order record.",
        "Complete all validation steps defined in Section 5 before issuing the "
        "order confirmation.",
        "Issue a written order confirmation to the customer within four business hours "
        "of order entry (see Section 6).",
    ])

    pdf.h2("4.3   Email Order Processing")
    pdf.para(
        "When an order is received to a regional order mailbox, the CSR shall:"
    )
    pdf.numbered([
        "Acknowledge receipt to the sender within two business hours, using the standard "
        "acknowledgement template (available on the Opella CS SharePoint portal).",
        "Review the email to confirm it contains all required information: SKU(s) and "
        "quantities, requested delivery date, delivery address, and a customer PO "
        "reference. If any information is missing, contact the customer to obtain the "
        "missing detail before entering the order. Document the follow-up interaction "
        "in the SAP order record.",
        "Enter the order into SAP S/4HANA within one business day of email receipt, "
        "after confirming all required information has been received.",
        "Complete all validation steps defined in Section 5.",
        "Issue a formal order confirmation within two business hours of order entry "
        "(see Section 6). The confirmation may be issued by reply to the original "
        "order email.",
    ])

    pdf.h2("4.4   Order Cut-off Times")
    pdf.para(
        "Orders must be received and entered into SAP by the following times to be "
        "processed (validated, confirmed, and released) on the same business day. Orders "
        "received after cut-off will be processed the following business day. The customer "
        "must be informed at acknowledgement if their requested delivery date is affected."
    )
    pdf.table(
        ["Market / Region", "Order Entry Cut-off", "Time Zone", "Same-Day Processing"],
        [
            ["France",                 "14:00",  "CET / CEST", "Yes"],
            ["United Kingdom",         "13:00",  "GMT / BST",  "Yes"],
            ["Germany / Austria / CH", "14:00",  "CET / CEST", "Yes"],
            ["Spain / Portugal",       "14:00",  "CET / CEST", "Yes"],
            ["Benelux",                "14:00",  "CET / CEST", "Yes"],
            ["Italy",                  "13:00",  "CET / CEST", "Yes, via 3PL handover."],
            ["Rest of Europe",         "12:00",  "CET / CEST", "Best efforts. Contact DC Ops to confirm."],
        ],
        widths=[52, 32, 26, 58],
    )

    pdf.h2("4.5   Non-Standard Order Requests")
    pdf.para(
        "Non-standard order requests include, but are not limited to: orders for "
        "discontinued or restricted SKUs; orders below agreed MOQ without AM pre-approval; "
        "split-site deliveries to addresses not in the SAP account record; urgent orders "
        "requested outside standard lead times; and orders from accounts on credit review.\n\n"
        "All non-standard requests must be escalated to the CS Team Lead before SAP "
        "entry. The CS Team Lead will advise on acceptance, amendment, or rejection, and "
        "will confirm their decision in writing to the CSR and the Account Manager within "
        "two business hours. The CS Team Lead's decision must be documented in the SAP "
        "order record before processing proceeds."
    )

    # ── SECTION 5 - ORDER VALIDATION ──────────────────────────────────────────
    pdf.add_page()
    pdf.h1("5.   Order Validation")

    pdf.para(
        "All orders must pass the validation sequence below before being confirmed to "
        "the customer or released to the DC. Validation is performed by the CSR in SAP "
        "S/4HANA. The steps must be completed in the order shown. An order must not be "
        "confirmed or released until all applicable steps are satisfied."
    )

    pdf.h2("5.1   Customer Account Status Check")
    pdf.para(
        "The CSR must verify the customer account status in SAP S/4HANA before proceeding."
    )
    pdf.table(
        ["SAP Account Status", "Required Action"],
        [
            ["Active",
             "Proceed to Step 5.2."],
            ["Credit Review",
             "Notify Credit Controller immediately. Do not enter or confirm the order "
             "until Credit Controller confirms account status. Target: 4 business hours."],
            ["On Hold",
             "Notify CS Team Lead and Account Manager within 1 hour. Do not enter or "
             "confirm the order. CS Team Lead will advise on next steps."],
            ["Inactive / Closed",
             "Do not process under any circumstances. Contact CS Team Lead. Account "
             "Manager must be notified."],
        ],
        widths=[38, 130],
    )

    pdf.h2("5.2   Credit Limit Verification")
    pdf.para(
        "Before confirming the order, the CSR must verify in SAP S/4HANA that the "
        "order value, combined with the customer's current outstanding balance, does "
        "not exceed the customer's approved credit limit.\n\n"
        "The credit limit in SAP S/4HANA is the sole authoritative figure for this "
        "check. Credit figures from other sources - including verbal guidance from "
        "Account Managers or records in other systems - must not be used as the basis "
        "for a credit release decision without written confirmation from the Credit "
        "Controller."
    )

    pdf.h2("5.3   Credit Hold Procedure")
    pdf.para(
        "Where an order would cause the outstanding balance to exceed the approved "
        "credit limit, SAP S/4HANA will automatically place the order on credit hold. "
        "The following procedure must be followed:"
    )
    pdf.numbered([
        "The CSR receives a SAP system notification when a credit hold is triggered.",
        "The CSR must notify the Credit Controller within four business hours, providing: "
        "customer name and SAP account number, order reference and value, current "
        "outstanding balance, and approved credit limit.",
        "The Credit Controller will decide one of: (a) release the hold with documented "
        "commercial justification; (b) approve a temporary limit increase with a defined "
        "expiry date; or (c) request partial payment as a condition of release.",
        "The Credit Controller's decision must be recorded in the SAP order record "
        "before the hold is released. The decision must be in writing (email is "
        "sufficient).",
        "CSRs must not release a credit hold without written Credit Controller "
        "authorisation. Unauthorised release constitutes a policy breach and will be "
        "escalated to the Finance Director.",
        "If the Credit Controller does not respond within four business hours, the CSR "
        "must escalate to the CS Team Lead.",
    ])
    pdf.note(
        "POLICY REQUIREMENT",
        "A credit hold must never be released by a CSR based solely on instructions from\n"
        "an Account Manager or commercial team member. Only the Credit Controller may\n"
        "authorise the release of a credit hold. Refer to Credit Management Policy\n"
        "OPS-EU-FIN-POL-002 for the full credit hold governance framework."
    )

    pdf.h2("5.4   Product Availability Check")
    pdf.para(
        "The CSR must confirm product availability at the allocated DC before confirming "
        "the order. Availability is checked in SAP S/4HANA inventory management."
    )
    pdf.bullets([
        "SKU available in full: proceed to Step 5.5.",
        "SKU available in part: offer the customer a partial shipment at the available "
        "quantity, with a confirmed date for the remaining quantity. Document the "
        "customer's decision in the SAP order record. If the available quantity is "
        "insufficient to meet the customer's minimum acceptable delivery, treat as "
        "'SKU unavailable'.",
        "SKU unavailable: check the expected restock date in SAP. Offer the customer "
        "the restock date as an alternative delivery date. If the restock date is "
        "unacceptable to the customer, escalate to the CS Team Lead.",
        "SKU discontinued: notify the CS Team Lead before advising the customer. The "
        "CS Team Lead will confirm whether a substitute SKU is available and authorised.",
    ])

    pdf.h2("5.5   Minimum Order Quantity (MOQ) Check")
    pdf.para(
        "The CSR must verify that the ordered quantity for each SKU meets the MOQ "
        "applicable to the customer's account tier, as configured in SAP. Where an "
        "order falls below MOQ:"
    )
    pdf.numbered([
        "Notify the Account Manager and request written approval to proceed below MOQ.",
        "The Account Manager has two business hours to respond.",
        "If the Account Manager approves, document the approval reference in the SAP "
        "order record before proceeding.",
        "If the Account Manager does not respond within two business hours, escalate "
        "to the CS Team Lead, who will make the final decision.",
    ])

    pdf.h2("5.6   Pricing Validation")
    pdf.para(
        "The CSR must confirm that the unit prices in the customer's purchase order "
        "match the agreed price list for that account in SAP S/4HANA."
    )
    pdf.table(
        ["Discrepancy Level", "Required Action"],
        [
            ["Less than 2% variance",
             "Process at SAP price list price. Notify Account Manager in writing. "
             "Document discrepancy in order record."],
            ["2% or greater variance",
             "Contact customer to confirm the correct price before processing. If "
             "unresolved within 2 business hours, escalate to Account Manager."],
            ["Structural pricing issue (e.g. wrong price list applied)",
             "Do not process. Escalate to CS Team Lead and Account Manager "
             "immediately. Suspend order entry until resolved."],
        ],
        widths=[48, 120],
    )

    # ── SECTION 6 - ORDER CONFIRMATION ────────────────────────────────────────
    pdf.h1("6.   Order Confirmation")

    pdf.h2("6.1   Confirmation Requirements")
    pdf.para(
        "Once all validation steps in Section 5 are satisfied, the CSR must issue a "
        "formal order confirmation to the customer. The confirmation is Opella's "
        "commitment to fulfil the order on the stated terms. No order should be released "
        "to the DC before the confirmation has been issued."
    )

    pdf.h2("6.2   Confirmation Timelines")
    pdf.table(
        ["Order Channel", "Confirmation Method", "Confirmation Deadline"],
        [
            ["Telephone / Manual",
             "Email to the customer's designated order contact.",
             "Within 4 business hours of order entry into SAP."],
            ["Email",
             "Reply to the original order email, attaching confirmation.",
             "Within 2 business hours of order entry into SAP."],
        ],
        widths=[38, 78, 52],
    )

    pdf.h2("6.3   Confirmation Content")
    pdf.para(
        "All order confirmations must include the following information. Omission of any "
        "mandatory field requires CS Team Lead approval before issue."
    )
    pdf.bullets([
        "Opella order number (SAP sales order reference).",
        "Customer purchase order (PO) reference number.",
        "Confirmed product SKU(s), descriptions, and quantities.",
        "Confirmed unit price(s) and total order value (excluding VAT).",
        "Applicable VAT rate and total VAT amount.",
        "Confirmed delivery address, verified against SAP account record.",
        "Confirmed despatch date and expected delivery date by market (per Section 7.2).",
        "Delivery instructions (if applicable and documented in the account record).",
        "Name and direct contact details of the CSR issuing the confirmation.",
    ])

    pdf.h2("6.4   Confirmation Discrepancy Handling")
    pdf.para(
        "If a discrepancy is identified between the customer's purchase order and the "
        "order confirmation (e.g. quantity, price, delivery address), the CSR must "
        "contact the customer immediately to clarify and agree the correct details. The "
        "order must not be released to the DC until the discrepancy is resolved and the "
        "correct details are confirmed in the SAP order record.\n\n"
        "Where a discrepancy cannot be resolved within four business hours, the CSR "
        "must escalate to the CS Team Lead. The CS Team Lead will decide whether to "
        "hold, amend, or cancel the order."
    )

    # ── SECTION 7 - ORDER FULFILMENT ──────────────────────────────────────────
    pdf.add_page()
    pdf.h1("7.   Order Release and Fulfilment")

    pdf.h2("7.1   Release to Distribution Centre")
    pdf.para(
        "Once all validation steps are complete and the order confirmation has been "
        "issued, the CSR releases the order to the appropriate DC in SAP S/4HANA. "
        "Release must not occur before both conditions are met.\n\n"
        "The DC allocation is determined automatically by SAP based on the customer's "
        "account record and the product's inventory position. Where SAP proposes a "
        "non-standard DC allocation (e.g. due to stock positioning), the CSR must "
        "confirm the allocation with the CS Team Lead before release."
    )

    pdf.h2("7.2   Standard Lead Times")
    pdf.para(
        "Standard lead times from order confirmation to customer delivery are as follows. "
        "These lead times assume cut-off requirements in Section 4.4 are met and normal "
        "DC operating conditions apply."
    )
    pdf.table(
        ["Market", "Lead Time (Business Days)", "Primary DC", "Notes"],
        [
            ["France",              "2", "Chartres, FR",    ""],
            ["United Kingdom",      "3", "Swindon, UK",     ""],
            ["Germany",             "2", "Frankfurt, DE",   ""],
            ["Austria / Switzerland","3", "Frankfurt, DE",  "Cross-border transit time."],
            ["Spain",               "3", "Barcelona, ES",   ""],
            ["Portugal",            "4", "Barcelona, ES",   ""],
            ["Benelux",             "2", "Antwerp, BE",     ""],
            ["Italy",               "3", "Milan, IT",       "3PL managed. Confirm with DC Ops."],
            ["Rest of Europe",      "3-5", "Multiple",      "Market-specific. Contact DC Ops."],
        ],
        widths=[50, 28, 36, 54],
    )
    pdf.para(
        "Priority (next-business-day) delivery is available for France, UK, and Germany "
        "only, subject to cut-off times and DC capacity. Priority orders require CS Team "
        "Lead authorisation and will incur the priority handling surcharge specified in "
        "the customer's commercial terms."
    )

    pdf.h2("7.3   Order Monitoring and Exception Handling")
    pdf.para("The CSR is responsible for monitoring order status from release to despatch confirmation.")
    pdf.bullets([
        "If a despatch confirmation has not been received within the standard lead time, "
        "the CSR must contact DC Operations directly to investigate, without waiting for "
        "a further trigger.",
        "The CSR must update the customer proactively if a delay is identified, providing "
        "a revised delivery date within two business hours of identifying the delay.",
        "All delayed orders (more than one business day beyond standard lead time) must "
        "be logged in the CS exception register maintained by the CS Team Lead.",
        "If a delay exceeds two business days beyond the standard lead time, the CS Team "
        "Lead and Account Manager must both be notified.",
    ])

    pdf.h2("7.4   Partial Shipments")
    pdf.para(
        "Partial shipments occur where the DC can fulfil only part of an order due to "
        "stock availability constraints or at the customer's request."
    )
    pdf.numbered([
        "The partial shipment must be confirmed with the customer in writing before "
        "DC release, including the confirmed quantity to be despatched and the "
        "confirmed date for the remaining quantity.",
        "A backorder must be created in SAP for the remaining quantity. The CSR must "
        "confirm the expected fulfilment date to the customer at the time the partial "
        "shipment is agreed.",
        "The CS Team Lead must be notified of all partial shipments for monitoring "
        "and reporting purposes.",
        "Where the customer does not agree to a partial shipment, the order must be "
        "held until full availability is confirmed. The customer must be given a firm "
        "full-order delivery date within two business hours.",
    ])

    # ── SECTION 8 - INVOICING ─────────────────────────────────────────────────
    pdf.h1("8.   Invoicing and Payment Terms")

    pdf.h2("8.1   Invoice Generation")
    pdf.para(
        "Invoices are generated automatically in SAP S/4HANA upon despatch confirmation "
        "from the DC. The CSR is responsible for verifying that the invoice has been "
        "generated within one business day of despatch confirmation and that the invoice "
        "details are accurate. Where an invoice is not generated within this timeframe, "
        "the CSR must raise a finance system query with the Credit Controller."
    )

    pdf.h2("8.2   Payment Terms by Account Tier")
    pdf.table(
        ["Account Tier", "Standard Payment Terms", "Notes"],
        [
            ["Major Retail (Tier 1)",    "NET 45 days",  "Applies to all Tier 1 retail accounts per SAP credit master."],
            ["Pharmacy Chain (Tier 2)",  "NET 30 days",  ""],
            ["Wholesale (Tier 3)",       "NET 30 days",  ""],
            ["Independent / Other",      "NET 30 days",  "Subject to Credit Controller review at onboarding."],
        ],
        widths=[50, 40, 78],
    )
    pdf.para(
        "Payment terms are maintained in the SAP customer master by the Credit "
        "Controller. Deviations from the standard terms applicable to an account tier "
        "require Finance Director approval and must be documented in the account record."
    )

    pdf.h2("8.3   Invoice Disputes")
    pdf.para(
        "Where a customer disputes an invoice (value, quantity, or VAT), the CSR "
        "must log the dispute in SAP within one business day of receiving it and "
        "notify the Credit Controller. Resolution timelines are governed by the "
        "Returns and Credits SOP (OPS-EU-CS-SOP-002)."
    )

    # ── SECTION 9 - ESCALATION ────────────────────────────────────────────────
    pdf.h1("9.   Escalation Framework")

    pdf.h2("9.1   Escalation Principles")
    pdf.para(
        "Timely escalation is a professional responsibility, not an exception. CSRs "
        "are expected to escalate whenever a situation is outside the scope of this "
        "SOP, a defined timeframe cannot be met, or a customer faces a risk of service "
        "failure. Late escalation that results in a customer service failure or financial "
        "loss is a non-compliance matter and will be reviewed by the CS Team Lead."
    )

    pdf.h2("9.2   Escalation Matrix")
    pdf.table(
        ["Level", "Role", "Escalation Trigger", "Target Response"],
        [
            ["1",
             "CS Representative",
             "Standard order queries and customer contacts within SOP scope.",
             "Immediate, during contact."],
            ["2",
             "CS Team Lead\n(A. Kovacs)",
             "Non-standard orders. Queries unresolved at Level 1 within 4 hrs. "
             "Credit holds unresolved. All partial shipments. Delivery delays > 1 day "
             "beyond lead time.",
             "2 business hours."],
            ["3",
             "Commercial Planning Director\n(S. Marchetti)",
             "Strategic account escalations. Customer threats to delist. Revenue "
             "impact > EUR 50,000. Regulatory or compliance implications. Any media "
             "or press enquiry.",
             "4 business hours."],
        ],
        widths=[10, 40, 80, 38],
    )

    pdf.h2("9.3   Account Manager Parallel Notification")
    pdf.para(
        "For all Level 2 and Level 3 escalations involving a named strategic account, "
        "the Account Manager must be notified at the same time as the internal escalation. "
        "The Account Manager owns the commercial response to the customer; the CS Team "
        "Lead owns the operational response. Both responses must be coordinated before "
        "external communication."
    )

    # ── SECTION 10 - KPIS ─────────────────────────────────────────────────────
    pdf.h1("10.   Key Performance Indicators")

    pdf.para(
        "Performance against this SOP is measured using the KPIs below. Results are "
        "reported monthly by the CS Team Lead to the VP Commercial Operations, Europe. "
        "Any KPI below target for two consecutive months triggers a formal root cause "
        "analysis and improvement plan."
    )
    pdf.table(
        ["KPI", "Definition", "Target"],
        [
            ["Order Confirmation Timeliness",
             "% of orders confirmed within the SOP-defined timelines (Section 6.2).",
             ">= 98%"],
            ["Order Accuracy Rate",
             "% of orders fulfilled with zero quantity or product errors.",
             ">= 99.5%"],
            ["On-Time Delivery Rate",
             "% of orders despatched within the standard lead time (Section 7.2).",
             ">= 97%"],
            ["Credit Hold Resolution Time",
             "Average elapsed time from Credit Controller notification to decision.",
             "<= 4 hours"],
            ["Credit Note Resolution Time",
             "Average elapsed time from credit note request to issuance.",
             "<= 2 business days"],
            ["Customer Complaint Rate",
             "Number of formal customer complaints per 1,000 order lines processed.",
             "<= 0.5"],
            ["SAP Order Record Completeness",
             "% of non-standard orders with documented decision in SAP order record.",
             "100%"],
        ],
        widths=[56, 78, 34],
    )

    # ── SECTION 11 - COMPLIANCE ───────────────────────────────────────────────
    pdf.h1("11.   Compliance and Audit")

    pdf.h2("11.1   Policy Compliance")
    pdf.para(
        "Compliance with this SOP is mandatory for all personnel in scope. Non-compliance "
        "identified through self-reporting, customer complaints, internal audit, or "
        "management review will be escalated to the document owner and the relevant line "
        "manager. Repeated non-compliance may result in formal corrective action under "
        "Opella's HR performance management process."
    )

    pdf.h2("11.2   Audit Scope")
    pdf.para("This SOP is subject to the Opella Europe internal audit programme. Annual audit will include:")
    pdf.bullets([
        "Sample review of order confirmation timelines and documentation accuracy.",
        "Review of credit hold decisions, documentation quality, and resolution times.",
        "Review of credit note authorisation compliance and issuance timelines.",
        "Verification that SAP order records adequately document non-standard decisions.",
        "Spot-check of account status and credit limit validation at point of order entry.",
    ])

    pdf.h2("11.3   Quarterly Self-Assessment")
    pdf.para(
        "The CS Team Lead will conduct a quarterly self-assessment against the KPIs "
        "defined in Section 10 and report results to the VP Commercial Operations, "
        "Europe. The self-assessment report must identify any KPIs below target, root "
        "cause analysis, and planned corrective actions with timelines."
    )

    # ── APPENDIX A ────────────────────────────────────────────────────────────
    pdf.add_page()
    pdf.h1("Appendix A:   Order Validation Checklist")

    pdf.para(
        "This checklist must be completed by the CSR at order entry. For non-standard "
        "orders, a written record of the checklist completion must be attached to the "
        "SAP order record."
    )
    pdf.table(
        ["#", "Validation Step", "Pass Condition", "Action if Failed"],
        [
            ["1", "Account Status",
             "Account is ACTIVE in SAP.",
             "Sec. 5.1 - notify Credit Controller or CS Team Lead."],
            ["2", "Credit Limit",
             "Order + outstanding balance does not exceed SAP credit limit.",
             "Sec. 5.3 - notify Credit Controller within 4 hrs."],
            ["3", "Product Availability",
             "All SKUs available at DC in ordered quantity.",
             "Sec. 5.4 - offer partial ship or alternative date."],
            ["4", "MOQ",
             "All SKUs meet MOQ for account tier.",
             "Sec. 5.5 - obtain AM written approval before entry."],
            ["5", "Pricing",
             "Order prices match SAP price list for account.",
             "Sec. 5.6 - contact customer / AM to resolve."],
            ["6", "Delivery Address",
             "Delivery address confirmed against SAP account record.",
             "Confirm with customer before confirming order."],
            ["7", "PO Reference",
             "Customer PO reference provided and noted.",
             "Request from customer before issuing confirmation."],
            ["8", "Authorised Contact",
             "Order received from a contact listed in SAP account record.",
             "Do not accept. Request customer arranges authorisation via AM."],
        ],
        widths=[8, 38, 60, 62],
    )

    # ── APPENDIX B ────────────────────────────────────────────────────────────
    pdf.h1("Appendix B:   Key Contact Directory")

    pdf.table(
        ["Role", "Name", "Email / Contact"],
        [
            ["CS Team Lead, Europe",                  "Alina Kovacs",     "alina.kovacs@opella.com"],
            ["Commercial Planning Director, Europe",  "Sophie Marchetti", "sophie.marchetti@opella.com"],
            ["Credit Controller, UK & Europe",        "Raj Patel",        "raj.patel@opella.com"],
            ["Account Manager, France",               "Thomas Beaumont",  "thomas.beaumont@opella.com"],
            ["CS Analyst, DACH",                      "Helena Brandt",    "helena.brandt@opella.com"],
            ["Opella Digital (EDI / IT)",             "James Okafor",     "james.okafor@opella.com"],
            ["DC Operations - France (Chartres)",     "DC Control Room",  "+33 2 37 21 00 00"],
            ["DC Operations - UK (Swindon)",          "DC Control Room",  "+44 1793 512 000"],
            ["DC Operations - Germany (Frankfurt)",   "DC Control Room",  "+49 69 240 080 00"],
            ["DC Operations - Spain (Barcelona)",     "DC Control Room",  "+34 93 298 00 00"],
        ],
        widths=[66, 42, 60],
    )

    pdf.output(path)


# ── CLI convenience ────────────────────────────────────────────────────────────
if __name__ == "__main__":
    import os, sys
    out = os.path.join(os.path.dirname(__file__), "..", "output", "o2c",
                       "order-management-sop-opella-europe.pdf")
    os.makedirs(os.path.dirname(out), exist_ok=True)
    generate_order_management_sop(out)
    print(f"Written: {out}")
