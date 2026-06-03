def generate_ar_review_notes(path: str) -> None:
    """Doc 07 — ~600 words. Seeds F1. Key signal: Carrefour France credit limit
    discrepancy (CRM EUR 2,400,000 vs ERP EUR 1,800,000) and Boots UK payment terms conflict."""

    content = """\
ACCOUNTS RECEIVABLE REVIEW — Q4 2025
Prepared by: Raj Patel, Credit Controller UK & Europe
Date: 2026-01-08
Distribution: Sophie Marchetti, Finance Director EU

---

This note summarises outstanding credit data inconsistencies identified during the Q4 2025
accounts receivable close. These issues were flagged informally during the year but have
not been formally escalated or resolved. I am raising them now as they are beginning to
affect collection timelines and customer service decisions.

---

CREDIT LIMIT DISCREPANCIES

During Q4 close I ran a reconciliation between the SAP S/4HANA customer master and the
credit limits visible in SAP CRM. For most accounts these align. For a subset of our
largest retail accounts they do not.

Carrefour France is showing two different credit limits depending on which system you look
at — CRM has EUR 2,400,000 and ERP has EUR 1,800,000. This is a material difference. The
CRM figure appears to have been manually updated at some point after the carve-out — the
audit trail shows "manually updated by account manager post-carve-out" but no approval
record. Our credit policy does not define which system is authoritative. As a result,
Carrefour FR is currently operating against the CRM limit. Whether that was an intended
decision or a data entry artefact is not clear to me.

The same pattern exists for Boots UK: ERP shows EUR 1,200,000 on NET45 terms. CRM shows
EUR 1,550,000 on NET30 terms. Boots UK's commercial team has been invoicing to the NET30
terms and the account manager was not aware this differed from the ERP record. Raj raised
this with Thomas Beaumont in November — no resolution yet.

E.Leclerc and dm (Drogerie Markt) have smaller discrepancies in the same direction — CRM
limits are higher than ERP limits in both cases. I have not investigated these further but
they follow the same pattern.

---

ACCOUNTS MIGRATED FROM SANOFI

Six of our largest accounts were migrated from the Sanofi legacy customer master in May
2024. The migration brought the account structure and historical credit limits across.
What it did not bring was any reconciliation with the CRM data that Sanofi Consumer
Healthcare was maintaining separately. Both datasets were live at carve-out — and both
were migrated, creating two records for the same customer in two systems.

---

RECOMMENDATIONS

1. Define which system — ERP or CRM — is the system of record for customer credit limits.
   This decision needs to come from finance and commercial, not from the credit team.

2. Run a full reconciliation for the top 50 accounts before end of Q1 2026. I can prepare
   the extract but cannot make the system-of-record decision unilaterally.

3. Establish an approval workflow for any manual override of credit limits in CRM. The
   current situation — where account managers can update CRM limits without ERP
   alignment — is a credit risk exposure that is not visible in our standard reporting.

The underlying root cause is that we inherited two active customer data systems from Sanofi
and have not yet decided how to consolidate them. Until that decision is made, credit
exposure for our top accounts cannot be accurately assessed from any single source.

Raj Patel
Credit Controller, UK & Europe
2026-01-08
"""

    with open(path, "w") as f:
        f.write(content)


def generate_edi_working_notes(path: str) -> None:
    """Doc 11 — ~1,100 words. Seeds F2 and F3. Most important document in the set.
    Contains the verbatim passage about Sanofi IT helpdesk dependency for 6 connections."""

    content = """\
EDI DISPUTE RESOLUTION — HOW WE ACTUALLY DO IT
Written by: Alina Kovacs, Customer Service Lead Europe
Last updated: 2025-11-14
Purpose: Onboarding guide for new CS team members

This is not an official SOP. Our official Order Management SOP does not cover EDI, which
is a problem because roughly two-thirds of our order volume comes through EDI. Until
someone writes the official version, this document is the closest thing we have to a
procedure. Please keep it updated if you discover something I've missed.

---

BACKGROUND

When Opella separated from Sanofi in April 2025, we inherited 14 active EDI connections
to retail and pharmacy customers across Europe. EDI is how our largest customers send us
purchase orders automatically — it accounts for around 67% of our total order volume.

Opella Digital manages 8 of those connections directly. For those 8, if there is a problem
you contact James Okafor or raise a ticket in the Opella Digital helpdesk. Response time
is usually same day.

For the other 6 connections — Carrefour France, Boots UK, dm (Drogerie Markt), E.Leclerc,
Lidl Europe, and Coop Group — the connections were established by Sanofi Shared Services
and were not yet handed over at the time of carve-out. Opella Digital doesn't manage these
yet. If there is an outage or a mapping error on one of those connections, you need to
contact the Sanofi IT helpdesk on the number below. They will respond but it can take 24
to 48 hours. Do not open a ticket with Opella Digital for these connections — they cannot
access the Sanofi systems.

Sanofi IT Helpdesk (EDI): +33 1 53 77 40 00 (option 3 — EDI and Integration Support)
Reference: Opella / [connection name] / Ticket type: EDI

I know this is not how it should work. I have flagged it to James Okafor twice. It is on
the TSA review list but I do not know when it will be resolved.

---

COMMON ISSUES AND WHAT TO DO

1. ORDER NOT RECEIVED

The customer's system shows the order was sent. Our system shows nothing. This is an EDI
channel failure — the order was not transmitted, or it was transmitted and rejected at our
end before creating a record.

Check: Go to the EDI monitoring dashboard (Opella Digital have access — ask James). If the
connection is one of the 6 Sanofi-managed ones, call the Sanofi helpdesk first.

Action: Manually re-enter the order while the EDI issue is investigated. Do not wait for
the EDI channel to be fixed before processing — the customer will complain about late
delivery long before the EDI issue is resolved.

2. DUPLICATE ORDERS

Sometimes an EDI order arrives twice — the customer's system sent it, got no acknowledgement,
and sent it again. We process both. The customer receives double the stock and refuses
the second delivery.

Check: Look for orders from the same customer on the same date with the same PO number.
If they match, flag to Helena Brandt who handles DACH, or Thomas Beaumont for France.

Action: Cancel the duplicate in our system. Issue a cancellation confirmation to the
customer by email (not via EDI — it is faster and creates a clear audit trail).

3. MAPPING ERRORS

An EDI mapping error means the product codes in the customer's order do not match ours.
This usually happens when a customer updates their internal catalogue without telling us.

For the 8 Opella Digital-managed connections, James Okafor can update the mapping table.
For the 6 Sanofi-managed connections, the Sanofi IT helpdesk updates the mapping. This
can take several days. In the meantime, process the order manually.

4. CREDIT HOLDS BLOCKING EDI ORDERS

Sometimes an EDI order arrives but is automatically placed on hold because the customer
has exceeded their credit limit. The problem is that our credit limits differ between ERP
and CRM. Raj Patel has been trying to resolve this since Q3 but it is not fixed yet.

If an EDI order from Carrefour France, Boots UK, dm, E.Leclerc, Lidl, or Coop is on
credit hold, check with Raj before releasing. Do not release based on what you see in CRM
alone — the ERP limit is lower.

5. ESCALATIONS FROM THE SANOFI-MANAGED CONNECTIONS

If a customer on one of the 6 Sanofi-managed connections is threatening to escalate
(delist a product, escalate to a director), contact Sophie Marchetti as well as the
Sanofi helpdesk. Do not let a Sanofi helpdesk delay become a commercial relationship
problem without escalating internally.

---

TIMELINE EXPECTATIONS FOR SANOFI-MANAGED CONNECTION ISSUES

When you contact the Sanofi IT helpdesk for one of the 6 Sanofi-managed connections,
here is what to expect:

Initial acknowledgement: Usually within 2 hours during business hours (Paris time).
First diagnosis: Usually same day for Priority 1 issues (account cannot send orders at
all). 24 to 48 hours for mapping errors and standard failures.

Priority 1 means the customer cannot transmit orders at all — zero connectivity. If Boots
UK or Carrefour France is completely dark on EDI, use those words: "Priority 1, customer
cannot transmit, account is Opella." They respond faster when you are specific.

If you do not hear back within 4 hours on a Priority 1 issue, escalate to James Okafor.
Even though Opella Digital does not manage these connections, James has a direct line to
the Sanofi EDI team lead and can expedite. He will not be happy about it — he has told
me that every escalation weakens our negotiating position on the TSA handover timeline —
but customer impact takes priority.

Do not promise the customer a resolution time based on the Sanofi SLA. Tell them you are
working on it and will update them by end of business. Under-promise and update frequently.

---

WHAT WE STILL DON'T HAVE

- A formal SOP for EDI order management (the official Order Management SOP covers manual
  and email orders only).
- A RACI for EDI dispute resolution (there is no row in the O2C RACI for EDI).
- A clear date for when the 6 Sanofi-managed connections will be transferred to Opella Digital.
- A single answer on credit limits for the migrated accounts.

I have raised all of these gaps with Sophie Marchetti. They are known. They are not yet fixed.

Alina Kovacs
Customer Service Lead, Europe
November 2025
"""

    with open(path, "w") as f:
        f.write(content)
