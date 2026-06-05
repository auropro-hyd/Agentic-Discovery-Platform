"""Build a SynthesisContent for the 6-report suite.

Two sources:
  - fixture (demo default): hand-grounded content in fixture_o2c(); every number traces to the
    verified findings, validated through synthesis.validate_synthesis at build time.
  - live (--live-synth): synthesis.run_synthesis() output mapped onto the dataclasses.

Code (not the model) owns the PP<->OPP links, prerequisite_for, matrix quadrant, and the
deterministic source index.
"""
from __future__ import annotations

import re

from .. import docnames
from ..models import (
    BoundedContext, BusinessImpact, ContextRelationship, CurrentState, DataTable, EvidenceRow,
    ExecutiveSummary, FormatPattern, Handoff, InventoryItem, KeyStat, MatrixQuadrant, MetricItem,
    NumberRef, Opportunity, OppPattern, PainPoint, ProcessDetail, ProcessStep, RaciRow, RiskItem,
    RoadmapHorizon, RoadmapItem, SourceDoc, SourceRef, SynthesisContent, SystemProfile, TraceRow,
)
from ..synthesis import OPP_TO_PP, PP_TO_OPP, allowed_numbers, validate_synthesis


def _q(quadrant: str) -> MatrixQuadrant:
    return MatrixQuadrant(quadrant)


# The hand-grounded fixture is O2C-only. It must NEVER be rendered for another domain (that would
# silently show Order-to-Cash content for, say, a Procurement engagement).
FIXTURE_DOMAINS = {"o2c"}


class NoFixtureForDomain(Exception):
    """Raised when a non-fixture domain has no live synthesis and thus no safe content."""


def build_synthesis(raw_payload: dict, *, domain: str = "o2c", live=False, llm=None,
                    doc_keys=None, model=None, suppress_names=None, reg=None,
                    fanout=True) -> SynthesisContent:
    """Build the report content. Live runs use the DEEP per-report fan-out by default (fact-store →
    per-report/per-opportunity generation → reference-depth SynthesisContent); pass fanout=False for
    the legacy single-emit path. `reg` (the domain registry) is required by the fan-out to build the
    grounded fact-store; it falls back to the legacy path when absent."""
    if live and fanout and reg is not None:
        from .. import fanout_specs
        merged, planning, fs, strat, omitted = fanout_specs.run_report_fanout(
            llm, raw_payload, reg, doc_keys=doc_keys, model=model)
        content = _from_payload(merged)
        content.fact_store = fs
        content.strategy = strat
        content.planning_assumptions = planning
        content.omitted_sections = omitted
        # surface only the NON-EMPTY strategy fields alongside r05's posture (don't blank anything).
        # Defensive: a live section occasionally emits strategy_profile as a bare string instead of
        # an object — spreading that would raise "'str' object is not a mapping" and abort the whole
        # suite. Coerce to a dict (a stray string is discarded; the typed StrategyProfile wins).
        base = content.strategy_profile if isinstance(content.strategy_profile, dict) else {}
        content.strategy_profile = {**base,
                                    **{k: v for k, v in strat.to_dict().items() if v}}
    elif live:
        from .. import synthesis
        payload = synthesis.run_synthesis(llm, raw_payload, doc_keys or [], model=model,
                                          suppress_names=suppress_names)
        content = _from_payload(payload)
    elif domain in FIXTURE_DOMAINS:
        content = fixture_o2c()
    else:
        # no hand-grounded fixture for this domain — refuse rather than show wrong-domain content
        raise NoFixtureForDomain(
            f"domain '{domain}' has no grounded fixture; it must be generated live "
            f"(a fixture from another domain must never be reused here).")
    _apply_derived_links(content)
    content.source_index = build_source_index(raw_payload, doc_keys)
    content.charts = derive_charts(raw_payload, content.current_state)
    return content


def derive_charts(raw_payload: dict, current_state: CurrentState | None = None) -> list[dict]:
    """Code-owned chart series, built ONLY from grounded numbers (the tools' computed_values AND the
    synthesis data tables). Never model-set, so a chart can't carry a fabricated figure — every
    segment value is copied verbatim from a real cell/computed value. Domain-agnostic and graceful:
    a chart is included only when it has >= 2 real numeric segments; otherwise omitted.

    Two sources, in order of richness:
      1. data_tables — any table with a categorical first column + a numeric column becomes a chart
         (the natural business breakdowns: channel mix, credit CRM-vs-ERP, escalations by cause…).
      2. findings' computed_values — the legacy "unfulfilled by channel" pattern, as a fallback."""
    charts: list[dict] = []
    seen_titles: set[str] = set()

    # ---- 1. charts from the grounded data tables ----
    for t in (current_state.data_tables if current_state else []):
        cols = [str(c) for c in (t.columns or [])]
        rows = t.rows or []
        if len(cols) < 2 or len(rows) < 2:
            continue
        label_col = 0
        # only chart tables whose first column is a real CATEGORY (channel, system, measure…), not
        # a date or a per-row id/log — those produce noise, not a useful business breakdown.
        if not _is_categorical(cols[label_col], [r[label_col] for r in rows if r]):
            continue
        # pick the FIRST numeric column (most tables lead with a name then a count/amount)
        num_col = _first_numeric_col(cols, rows)
        if num_col is None or num_col == label_col:
            continue
        segs = []
        for r in rows:
            if num_col >= len(r) or label_col >= len(r):
                continue
            v = _num_cell(r[num_col])
            lab = str(r[label_col]).strip()
            if v is None or not lab:
                continue
            segs.append({"label": lab, "value": v})
        if len(segs) < 2:
            continue
        title = (t.title or t.caption or cols[num_col]).strip()
        if title.lower() in seen_titles:
            continue
        seen_titles.add(title.lower())
        unit = _unit_from_col(cols[num_col])
        # a small set of categories → donut (share); more → bar (magnitude). Cap at the top 8.
        segs = sorted(segs, key=lambda s: -s["value"])[:8]
        kind = "donut" if 2 <= len(segs) <= 5 else "bar"
        charts.append({"key": f"tbl-{len(charts)}", "unit": unit, "kind": kind,
                       "title": title, "segments": segs})
        if len(charts) >= 4:           # keep the suite focused — the richest few, not every table
            break

    # ---- 2. fallback: unfulfilled-by-channel from computed_values (only if tables gave nothing) ----
    if not charts:
        vals: dict[str, float] = {}
        for f in raw_payload.get("findings", []):
            for cv in f.get("computed_values", []):
                try:
                    vals[str(cv.get("label", "")).lower()] = float(cv["value"])
                except (TypeError, ValueError, KeyError):
                    continue
        unf = [(lbl.split("unfulfilled")[1].split("order")[0].strip().title() or "Channel", v)
               for lbl, v in vals.items()
               if "unfulfilled" in lbl and "order" in lbl and "value" not in lbl]
        unf = [(c, v) for c, v in unf if v > 0]
        if len(unf) >= 2:
            seg = [{"label": c, "value": v} for c, v in sorted(unf, key=lambda x: -x[1])]
            charts.append({"key": "unfulfilled_by_channel", "unit": "orders", "kind": "bar",
                           "title": "Unfulfilled orders by channel", "segments": seg})
            charts.append({"key": "unfulfilled_share", "unit": "orders", "kind": "donut",
                           "title": "Share of unfulfilled orders by channel", "segments": seg})
    return charts


def _num_cell(cell) -> float | None:
    """Parse a numeric value out of a table cell ("5,667", "EUR 61,225,000", "67.3%"). Returns the
    bare number (verbatim magnitude) or None if the cell isn't numeric."""
    if cell is None:
        return None
    s = str(cell).strip().replace(",", "")
    m = re.search(r"-?\d+(?:\.\d+)?", s)
    return float(m.group()) if m else None


_DATE_RE = re.compile(r"^\d{4}-\d{2}-\d{2}|^\d{1,2}[/-]\d{1,2}")


def _is_categorical(header: str, cells: list) -> bool:
    """True if a label column is a genuine category to group by (Channel, System, Measure…), not a
    date column or a per-row log/id. Heuristic: reject date-headed/date-valued columns, and reject
    columns where almost every value is unique (a log, not a breakdown)."""
    lo = header.lower()
    if lo in ("date", "datetime", "timestamp", "time", "id", "order id", "po id"):
        return False
    vals = [str(c).strip() for c in cells if str(c).strip()]
    if not vals:
        return False
    if sum(1 for v in vals if _DATE_RE.match(v)) > len(vals) // 2:
        return False
    # a useful breakdown repeats categories OR has a small fixed set; a log is nearly all-unique
    uniq = len(set(v.lower() for v in vals))
    return uniq <= 8 or uniq <= len(vals) * 0.6


def _first_numeric_col(cols: list[str], rows: list) -> int | None:
    """The index of the first column (after col 0) whose cells are predominantly numeric."""
    for c in range(1, len(cols)):
        nums = sum(1 for r in rows if c < len(r) and _num_cell(r[c]) is not None)
        if nums >= max(2, len(rows) // 2):
            return c
    return None


def _unit_from_col(col: str) -> str:
    lo = col.lower()
    if "%" in col or "share" in lo or "percent" in lo:
        return "percent"
    if "eur" in lo or "value" in lo or "€" in col or "amount" in lo:
        return "eur"
    return ""


# ---------------------------------------------------------------------------
# derived links (code-owned, never model-set)
# ---------------------------------------------------------------------------
def _apply_derived_links(c: SynthesisContent) -> None:
    for pp in c.pain_points:
        pp.opportunity_signal = PP_TO_OPP.get(pp.id, "")
    for opp in c.opportunities:
        opp.addresses_pain_point = OPP_TO_PP.get(opp.id, "")
    # prerequisite_for is the inverse of dependencies
    for opp in c.opportunities:
        opp.prerequisite_for = sorted(
            o.id for o in c.opportunities if opp.id in o.dependencies)


def build_source_index(raw_payload: dict, all_doc_ids: list[str] | None = None) -> list[SourceDoc]:
    """Deterministic: which findings each document supported. Report 06 audit trail.

    Lists every document in the run (from all_doc_ids), deriving names generically. Falls back to
    just the docs cited by findings if no full list is given."""
    supported: dict[str, set] = {}
    for f in raw_payload.get("findings", []):
        for s in f.get("sources", []):
            supported.setdefault(docnames.stem(s.get("doc_id", "")), set()).add(f["id"])
    doc_ids = [docnames.stem(d) for d in (all_doc_ids or [])] or sorted(supported)
    seen, out = set(), []
    for doc_id in doc_ids:
        if doc_id in seen:
            continue
        seen.add(doc_id)
        out.append(SourceDoc(
            doc_id=doc_id, business_name=docnames.friendly(doc_id), doc_type=docnames.kind(doc_id),
            what_we_read=docnames.phrase(doc_id),
            supported_findings=sorted(supported.get(doc_id, set())),
        ))
    return out


# ---------------------------------------------------------------------------
# the hand-grounded fixture (demo default) — every number traces to a finding
# ---------------------------------------------------------------------------
def _src(*ids) -> list[SourceRef]:
    return [SourceRef(doc_id=i) for i in ids]


def fixture_o2c() -> SynthesisContent:
    ERP, CRM = "sap-s4-customer-master-export", "sap-crm-customer-export"
    AR = "accounts-receivable-review-notes-q4-2025"
    POLICY = "credit-management-policy-opella-europe"
    FLOW = "order-flow-analysis-export-2025"
    RACI = "o2c-process-raci-opella-europe"
    SOP = "order-management-sop-opella-europe"
    ESC = "customer-service-escalation-log-2025"
    NOTES = "edi-dispute-resolution-cs-working-notes"

    current = CurrentState(
        domain_overview=(
            "Order-to-Cash covers how customer orders are received, credit-checked, "
            "fulfilled, invoiced and collected. Orders arrive through several channels, with "
            "electronic data interchange (EDI) carrying the largest share."),
        process_summary=(
            "Orders enter through EDI, manual entry, email and fax. Customer and credit information "
            "is held in two systems — SAP S/4HANA and SAP CRM. Orders are checked against a credit "
            "limit, released to the warehouse for fulfilment, then invoiced and collected by the "
            "accounts receivable team."),
        process_flow=[
            ProcessStep(seq=1, name="Order receipt", actor="Customer Service",
                        system="EDI / order management",
                        description="Orders arrive by EDI, manual entry, email or fax and are "
                                    "recorded for processing."),
            ProcessStep(seq=2, name="Credit check", actor="Credit Control", system="SAP S/4HANA",
                        description="Each order is checked against the customer's credit limit "
                                    "before it is released."),
            ProcessStep(seq=3, name="Fulfilment", actor="Warehouse", system="Order management",
                        description="Released orders are picked, packed and dispatched."),
            ProcessStep(seq=4, name="Invoicing", actor="Finance", system="SAP S/4HANA",
                        description="Dispatched orders are invoiced to the customer."),
            ProcessStep(seq=5, name="Collections", actor="Accounts Receivable", system="SAP S/4HANA",
                        description="Outstanding invoices are tracked and collected."),
        ],
        process_inventory=[
            InventoryItem(name="Order receipt and entry", purpose="Capture customer orders"),
            InventoryItem(name="Credit assessment", purpose="Check orders against credit limits"),
            InventoryItem(name="Fulfilment", purpose="Pick, pack and dispatch"),
            InventoryItem(name="Invoicing and collections", purpose="Bill and collect"),
        ],
        ownership_map=[
            RaciRow(activity="Manual order processing", responsible="Customer Service",
                    accountable="Customer Service Lead"),
            RaciRow(activity="Credit decisions", responsible="Credit Control",
                    accountable="Credit Controller"),
            RaciRow(activity="EDI order processing", responsible="Customer Service",
                    accountable="Not assigned"),
            RaciRow(activity="EDI dispute resolution", responsible="Customer Service",
                    accountable="Not assigned"),
        ],
        system_inventory=[
            InventoryItem(name="SAP S/4HANA", purpose="Core ERP — orders, invoicing, collections",
                          system_of_record_for="Customer credit limits (per the Credit Policy)"),
            InventoryItem(name="SAP CRM", purpose="Customer relationship management"),
            InventoryItem(name="EDI / order management", purpose="Receives electronic orders"),
        ],
        handoff_catalogue=[
            Handoff(from_step="Order receipt", to_step="Credit check", mechanism="Order record"),
            Handoff(from_step="Credit check", to_step="Fulfilment", mechanism="Released order"),
            Handoff(from_step="Fulfilment", to_step="Invoicing", mechanism="Dispatch confirmation"),
            Handoff(from_step="Invoicing", to_step="Collections", mechanism="Open invoice"),
        ],
        system_profiles=[
            SystemProfile(
                name="SAP S/4HANA",
                role="The core ERP and the system of record for orders, credit limits, invoicing "
                     "and collections.",
                how_used="Customer Service, Credit Control, Finance and Accounts Receivable all work "
                         "in S/4HANA: orders are recorded here, the credit check reads the credit "
                         "limit held against the account, and invoices and open receivables are "
                         "tracked here through to collection.",
                owners="Owned by Finance Systems; used daily by Customer Service, Credit Control and "
                       "Accounts Receivable.",
                limitations="Holds its own credit limit per account. For 267 shared accounts that "
                            "value differs from the one held in CRM, and the credit check reads "
                            "whichever record the system resolves first."),
            SystemProfile(
                name="SAP CRM",
                role="The customer-relationship system, holding account and commercial relationship "
                     "data for the same retail customers.",
                how_used="Used by the commercial team to manage account relationships; it also holds "
                         "credit limits and payment terms that were updated by hand over time.",
                owners="Owned by the commercial function; no shared governance with Finance Systems "
                       "over the credit fields.",
                limitations="CRM credit limits were edited manually without an approval trail. Its "
                            "values differ from the ERP — Carrefour France shows €2.4M in CRM "
                            "against €1.8M in the ERP, a €600,000 difference on a single account."),
            SystemProfile(
                name="EDI / order-management channel",
                role="The electronic data interchange channel through which the largest share of "
                     "customer orders arrives.",
                how_used="Carries 67% of order volume (5,667 of 8,420 orders). Orders flow straight "
                         "into order management for fulfilment; exceptions are picked up by hand by "
                         "Customer Service.",
                owners="No named owner — the Order-to-Cash RACI leaves EDI order processing and EDI "
                       "dispute resolution as 'Not assigned'.",
                limitations="Not covered by the Order Management SOP, and no credit check runs on it "
                            "before release. 1,196 EDI orders (€12.4M) sit unfulfilled, and 'EDI "
                            "order not processed' appears 34 times in the escalation log."),
        ],
        format_taxonomy=[
            FormatPattern(
                label="Type 1 — Structured transactional export",
                description="Row-per-transaction tabular data with typed columns (amounts, dates, "
                            "account IDs, channel). Machine-readable and directly aggregatable.",
                examples="Order-flow export, customer-master extracts from the ERP and CRM, "
                         "accounts-receivable ledger."),
            FormatPattern(
                label="Type 2 — Governance &amp; policy document",
                description="Prose documents that state the intended (to-be) rules: who approves "
                            "what, which system is authoritative, and the documented procedure.",
                examples="Order Management SOP, Credit Policy, the Order-to-Cash process RACI."),
            FormatPattern(
                label="Type 3 — Operational log &amp; working notes",
                description="Semi-structured incident and escalation records plus free-text agent "
                            "notes — the lived reality of how exceptions are actually handled.",
                examples="Customer-service escalation log, EDI dispute-resolution working notes."),
        ],
        baseline_stats=[
            KeyStat(value="8,420", label="Total orders processed", sublabel="calendar year 2025"),
            KeyStat(value="67.3%", label="Orders received via EDI", sublabel="5,667 of 8,420"),
            KeyStat(value="14", label="Active EDI connections", sublabel="8 owned + 6 under TSA"),
            KeyStat(value="340", label="Active customer accounts", sublabel="in the ERP master"),
        ],
        data_tables=[
            DataTable(
                title="Order channel mix — 2025",
                columns=["Channel", "Orders", "Share", "Entry method", "Not fulfilled"],
                rows=[
                    ["EDI", "5,667", "67.3%", "Automated into order management", "1,196"],
                    ["Telephone / manual", "1,802", "21.4%", "Keyed into the ERP by an agent", "320"],
                    ["Email", "767", "9.1%", "Keyed in within one business day", "111"],
                    ["Fax", "184", "2.2%", "Keyed in; by exception agreement only", "40"],
                    ["Total", "8,420", "100%", "—", "1,667"],
                ],
                caption="Volumes and shares are counted directly from the order-flow export.",
                note="Fax appears in the order data although the Order Management SOP lists only "
                     "telephone and email as standard channels.",
                sources=[SourceRef(doc_id=FLOW)]),
            DataTable(
                title="Standard fulfilment lead times by market",
                columns=["Market", "Lead time", "Primary distribution centre"],
                rows=[
                    ["France", "2 business days", "Chartres, FR"],
                    ["United Kingdom", "3 business days", "Swindon, UK"],
                    ["Germany", "2 business days", "Frankfurt, DE"],
                    ["Austria / Switzerland", "3 business days", "Frankfurt, DE"],
                    ["Spain", "3 business days", "Barcelona, ES"],
                    ["Portugal", "4 business days", "Barcelona, ES"],
                    ["Benelux", "2 business days", "Antwerp, BE"],
                    ["Italy", "3 business days", "Milan, IT (third-party operated)"],
                ],
                caption="Documented standard lead times and the distribution centre serving each "
                        "market.",
                sources=[SourceRef(doc_id=SOP)]),
            DataTable(
                title="Credit limit approval authority",
                columns=["Credit limit band", "New account", "Limit increase"],
                rows=[
                    ["Up to €250,000", "Credit Controller", "Credit Controller"],
                    ["€250,001 – €500,000", "Finance Director", "Finance Director"],
                    ["€500,001 – €1,000,000", "Finance Director + VP Commercial",
                     "Finance Director"],
                    ["Above €1,000,000", "Finance Director + VP Commercial + CEO",
                     "Finance Director + VP Commercial"],
                ],
                caption="Approval authority for setting and changing credit limits, by band.",
                sources=[SourceRef(doc_id=POLICY)]),
            DataTable(
                title="Collections escalation ladder",
                columns=["Overdue", "Action", "Owner"],
                rows=[
                    ["1–30 days", "Automated payment reminder on day 5", "System"],
                    ["31–60 days", "Formal payment demand; account flagged", "Credit Controller"],
                    ["61–90 days", "Second demand; credit-hold proposed", "Credit Controller"],
                    ["91+ days", "Account on hold; new orders suspended; agency referral considered",
                     "Finance Director"],
                ],
                caption="The documented overdue-collections escalation ladder.",
                sources=[SourceRef(doc_id=POLICY)]),
            DataTable(
                title="EDI connection inventory",
                columns=["#", "Trading partner", "Country", "Managed by", "Transition status"],
                rows=[
                    ["1", "Tesco", "UK", "Own platform", "Owned"],
                    ["2", "Mercadona", "ES", "Own platform", "Owned"],
                    ["3", "REWE Group", "DE", "Own platform", "Owned"],
                    ["4", "Boots (new)", "UK", "Own platform", "Owned (live Aug 2025)"],
                    ["5", "Alliance Healthcare", "EU", "Own platform", "Owned"],
                    ["6", "Rite Aid Europe", "EU", "Own platform", "Owned"],
                    ["7", "Aldi Europe", "EU", "Own platform", "Owned"],
                    ["8", "Coop Group (new)", "EU", "Own platform", "Owned"],
                    ["9", "Carrefour France", "FR", "Parent (TSA)", "Target Q4 2025"],
                    ["10", "Boots (legacy)", "UK", "Parent (TSA)", "Target Q1 2026"],
                    ["11", "dm (Drogerie Markt)", "DE", "Parent (TSA)", "Target Q1 2026"],
                    ["12", "E.Leclerc", "FR", "Parent (TSA)", "Target Q2 2026 (provisional)"],
                    ["13", "Lidl Europe", "EU", "Parent (TSA)", "Target Q2 2026 (provisional)"],
                    ["14", "Coop Group (legacy)", "EU", "Parent (TSA)", "Target Q3 2026 (provisional)"],
                ],
                caption="All 14 live EDI connections: 8 on the organisation's own platform, 6 still "
                        "operated by the former parent under the transitional service arrangement.",
                note="Migration targets for connections 12–14 are provisional pending technical "
                     "scoping; the governing service terms sit in a schedule not included in the "
                     "pack.",
                sources=[SourceRef(doc_id="edi-integration-register-opella-europe")]),
            DataTable(
                title="Top trading accounts — credit baseline",
                columns=["Account", "Country", "ERP credit limit", "Payment terms", "Status"],
                rows=[
                    ["Carrefour France", "FR", "€1,800,000", "NET45", "Active"],
                    ["Boots UK", "UK", "€1,200,000", "NET45", "Active"],
                    ["E.Leclerc", "FR", "€1,100,000", "NET45", "Active"],
                    ["Tesco UK", "UK", "€1,000,000", "NET45", "Active"],
                    ["dm (Drogerie Markt)", "DE", "€950,000", "NET45", "Active"],
                    ["Lidl Europe", "EU", "€850,000", "NET45", "Active"],
                    ["Coop Group", "EU", "€800,000", "NET45", "Active"],
                    ["Mercadona", "ES", "€750,000", "NET45", "Active"],
                ],
                caption="The eight accounts that trade across all channels, with their ERP credit "
                        "baseline.",
                sources=[SourceRef(doc_id=ERP)]),
            DataTable(
                title="Systems in scope",
                columns=["System", "Role", "Hosting"],
                rows=[
                    ["SAP S/4HANA", "Core ERP; authoritative for credit limits and balances",
                     "Enterprise"],
                    ["SAP CRM", "Customer relationship records (not authoritative for credit)",
                     "Enterprise"],
                    ["Own EDI platform", "Routes the 8 owned connections",
                     "Own private cloud, Frankfurt"],
                    ["Former parent's EDI platform", "Routes the 6 connections still under the "
                     "arrangement", "Former parent"],
                ],
                caption="The systems the order-to-cash process touches and who hosts them.",
                sources=[SourceRef(doc_id="edi-integration-register-opella-europe"),
                         SourceRef(doc_id=POLICY)]),
        ],
        process_detail=[
            ProcessDetail(
                title="Order receipt",
                actor="Customer Service", system="EDI / ERP",
                body="EDI orders flow automatically into order management across 14 connections (8 "
                     "on the organisation's own platform, 6 still operated by the former parent). "
                     "Telephone orders are keyed into the ERP within 30 minutes of the call; email "
                     "orders within one business day, against per-market cut-off times.",
                sources=[SourceRef(doc_id=SOP),
                         SourceRef(doc_id="edi-integration-register-opella-europe")]),
            ProcessDetail(
                title="Order validation",
                actor="Customer Service", system="SAP S/4HANA",
                body="A mandatory sequence runs in the ERP: customer account status, credit-limit "
                     "verification against the outstanding balance, product availability at the "
                     "allocated distribution centre, minimum-order-quantity compliance, and pricing "
                     "validation (a variance under 2% is processed at the system price; 2% or more "
                     "is referred to the account manager).",
                sources=[SourceRef(doc_id=SOP)]),
            ProcessDetail(
                title="Credit assessment",
                actor="Credit Control", system="SAP S/4HANA",
                body="The ERP places an order on credit hold automatically where it would take the "
                     "account past its approved limit, or where an invoice is more than 60 days "
                     "overdue. The agent notifies the Credit Controller within four business hours; "
                     "release authority follows the approval-authority bands.",
                sources=[SourceRef(doc_id=POLICY), SourceRef(doc_id=SOP)]),
            ProcessDetail(
                title="Order confirmation & fulfilment",
                actor="Customer Service / Distribution", system="ERP / order management",
                body="Confirmation issues within four business hours for telephone orders and two "
                     "for email orders. Released orders are picked, packed and dispatched from the "
                     "market's distribution centre against the documented standard lead times.",
                sources=[SourceRef(doc_id=SOP)]),
            ProcessDetail(
                title="Invoicing",
                actor="Finance", system="SAP S/4HANA",
                body="Invoices generate automatically on dispatch confirmation. Payment terms follow "
                     "the account tier: major retail on NET 45 with a 1% early-payment discount, "
                     "pharmacy and wholesale on NET 30, and new accounts on NET 14 or cash with "
                     "order for the first six months.",
                sources=[SourceRef(doc_id=SOP), SourceRef(doc_id=POLICY)]),
            ProcessDetail(
                title="Accounts receivable & collections",
                actor="Accounts Receivable", system="SAP S/4HANA",
                body="Aged-debtor reporting runs monthly; balances over 60 days are reviewed "
                     "individually. Collections follow the overdue escalation ladder, and the team "
                     "completes a quarterly self-assessment of compliance.",
                sources=[SourceRef(doc_id=POLICY)]),
        ],
    )

    pain_points = [
        PainPoint(
            id="PP1", title="Two customer systems disagree on credit limits", impact_rank=1,
            from_finding="F1", category="Data Governance", severity="high",
            description="Your ERP and CRM hold different credit limits and payment terms for the "
                        "same major retail accounts, with no single agreed source of truth.",
            root_cause="Both systems were carried over at carve-out and were never reconciled; CRM "
                       "limits were updated by hand without an approval trail.",
            failure_pattern="Orders are released against whichever limit the system resolves first, "
                            "so the same account can trade on two different limits.",
            business_consequence="Credit can be extended beyond the policy-approved limit, and the "
                                 "same account can be invoiced on two different payment terms.",
            quantified=[
                NumberRef(value=267, unit="accounts", label="accounts with different credit limits",
                          text="267 of the shared accounts", sources=_src(ERP, CRM)),
                NumberRef(value=600000, unit="eur", label="largest single gap (Carrefour France)",
                          text="€600,000", sources=_src(ERP, CRM, AR)),
            ],
            detail_table=DataTable(
                title="Credit-limit discrepancy register — top accounts",
                columns=["Account", "Country", "ERP limit", "CRM limit", "ERP terms", "CRM terms"],
                rows=[
                    ["Carrefour France", "FR", "€1,800,000", "€2,400,000", "NET45", "NET30"],
                    ["Boots UK", "UK", "€1,200,000", "€1,550,000", "NET45", "NET30"],
                    ["E.Leclerc", "FR", "€1,100,000", "€1,400,000", "NET45", "NET30"],
                    ["Tesco UK", "UK", "€1,000,000", "€1,350,000", "NET45", "NET30"],
                    ["dm (Drogerie Markt)", "DE", "€950,000", "€1,150,000", "NET45", "NET30"],
                ],
                caption="Where the two systems disagree, account by account — limits and terms.",
                sources=[SourceRef(doc_id=ERP), SourceRef(doc_id=CRM)]),
            sources=_src(ERP, CRM, AR, POLICY)),
        PainPoint(
            id="PP2", title="Two-thirds of orders run on an undocumented channel", impact_rank=2,
            from_finding="F2", category="Process Coverage", severity="high",
            description="EDI carries most of your order volume, yet it is not covered by the Order "
                        "Management SOP and has no owner in the Order-to-Cash RACI.",
            root_cause="The documented process was written for manual and email orders; EDI grew "
                       "to dominate without the procedure or accountability catching up.",
            failure_pattern="EDI orders that fail are handled informally, with no governed process "
                            "or named owner.",
            business_consequence="The channel carrying most of the order value runs with no "
                                 "documented procedure and no accountable owner.",
            quantified=[
                NumberRef(value=67, unit="percent", label="EDI share of orders",
                          text="67% of orders (5,667 of 8,420)", sources=_src(FLOW, NOTES)),
            ],
            detail_table=DataTable(
                title="Document-level evidence",
                columns=["Document", "How it treats EDI"],
                rows=[
                    ["Order Management SOP", "Lists telephone and email as the standard channels; "
                     "EDI is out of scope."],
                    ["Order-to-Cash RACI", "Covers manual and email steps only; no EDI rows."],
                    ["EDI dispute working notes", "Informal notes, explicitly 'not an official "
                     "SOP'."],
                ],
                caption="Where each governing document leaves the EDI channel.",
                sources=[SourceRef(doc_id=SOP), SourceRef(doc_id=RACI), SourceRef(doc_id=NOTES)]),
            sources=_src(FLOW, RACI, SOP, NOTES)),
        PainPoint(
            id="PP3", title="EDI order failures concentrate on the unowned channel", impact_rank=3,
            from_finding="F3", category="Operational Resilience", severity="high",
            description="A large block of EDI orders is not fulfilled, on the same channel that has "
                        "no documented process or owner.",
            root_cause="Without a governed EDI process, failures are absorbed reactively through "
                       "manual re-entry rather than prevented.",
            failure_pattern="EDI orders not processed is the single most common customer-service "
                            "escalation.",
            business_consequence="The largest single block of unfulfilled orders — and the most "
                                 "frequent escalation — sits on the channel nobody owns.",
            quantified=[
                NumberRef(value=1196, unit="orders", label="EDI orders not fulfilled",
                          text="1,196 EDI orders", sources=_src(FLOW)),
                NumberRef(value=12362493.74, unit="eur", label="value not fulfilled",
                          text="€12.4M", sources=_src(FLOW)),
                NumberRef(value=34, unit="escalations", label="EDI-not-processed escalations",
                          text="34 escalations", sources=_src(ESC, NOTES)),
            ],
            detail_table=DataTable(
                title="Unfulfilled orders by channel",
                columns=["Channel", "Orders not fulfilled"],
                rows=[["EDI", "1,196"], ["Telephone / manual", "320"], ["Email", "111"],
                      ["Fax", "40"]],
                caption="Unfulfilled orders cluster on the EDI channel.",
                sources=[SourceRef(doc_id=FLOW)]),
            sources=_src(FLOW, ESC, NOTES)),
        PainPoint(
            id="PP4", title="Six EDI connections still run on the former parent's platform",
            impact_rank=2, from_finding="F2", category="Third-Party Dependency", severity="medium",
            description="Six of the fourteen live EDI connections are still operated by the former "
                        "parent under a transitional service arrangement, with the service terms "
                        "held in a schedule that is not in the document pack.",
            root_cause="At carve-out, eight connections moved to the organisation's own platform "
                       "while six remained on the parent's; the migration is partly complete.",
            failure_pattern="When one of these six connections has an incident, resolution depends "
                            "on the parent's team and a transitional agreement the organisation does "
                            "not control.",
            business_consequence="The organisation cannot guarantee its own response times on the "
                                 "connections carrying several of its largest retail accounts.",
            quantified=[
                NumberRef(value=6, unit="count", label="connections still under the arrangement",
                          text="6 of 14 connections", sources=_src(NOTES)),
            ],
            detail_table=DataTable(
                title="Connections still under the transitional arrangement",
                columns=["Trading partner", "Country", "Migration target"],
                rows=[
                    ["Carrefour France", "FR", "Q4 2025"],
                    ["Boots (legacy)", "UK", "Q1 2026"],
                    ["dm (Drogerie Markt)", "DE", "Q1 2026"],
                    ["E.Leclerc", "FR", "Q2 2026 (provisional)"],
                    ["Lidl Europe", "EU", "Q2 2026 (provisional)"],
                    ["Coop Group (legacy)", "EU", "Q3 2026 (provisional)"],
                ],
                caption="The six connections to bring onto the organisation's own platform.",
                note="The governing service terms sit in a schedule not included in the document "
                     "pack; the migration dates are the register's stated targets.",
                sources=[SourceRef(doc_id="edi-integration-register-opella-europe"),
                         SourceRef(doc_id=NOTES)]),
            sources=_src("edi-integration-register-opella-europe", NOTES)),
        PainPoint(
            id="PP5", title="The two customer masters are not aligned on which accounts exist",
            impact_rank=3, from_finding="F1", category="Data Governance", severity="medium",
            description="The ERP holds more customer accounts than the CRM, so the two systems do "
                        "not even agree on which accounts exist, let alone their credit terms.",
            root_cause="Accounts were created in the ERP without a matching record being maintained "
                       "in the CRM after carve-out.",
            failure_pattern="Twenty-two accounts exist in the ERP with no CRM counterpart, so any "
                            "process that reads the CRM misses them entirely.",
            business_consequence="A clean reconciliation cannot be completed until the account "
                                 "populations themselves are aligned.",
            quantified=[
                NumberRef(value=22, unit="accounts", label="accounts in the ERP but not the CRM",
                          text="22 accounts", sources=_src(ERP, CRM)),
            ],
            detail_table=DataTable(
                title="Customer-master population",
                columns=["System", "Active accounts"],
                rows=[["ERP customer master", "340"], ["CRM customer records", "318"],
                      ["In the ERP only", "22"]],
                caption="The two masters hold different account populations.",
                sources=[SourceRef(doc_id=ERP), SourceRef(doc_id=CRM)]),
            sources=_src(ERP, CRM)),
    ]

    cross = [{"pattern": "Undocumented EDI channel drives both volume and failure",
              "description": "The same channel that carries two-thirds of orders is also where "
                             "fulfilment failures and escalations concentrate — the lack of a "
                             "governed process links the two."}]

    opp1 = Opportunity(
        id="OPP1", title="Customer Master Reconciliation", pattern=OppPattern.HITL,
        overview="Agree a single source of truth for customer credit limits and reconcile the ERP "
                 "and CRM records, with the credit and commercial teams signing off the canonical "
                 "values.",
        before_process=[
            ProcessStep(seq=1, name="Order arrives", actor="Customer Service",
                        description="An order arrives for a major retail account."),
            ProcessStep(seq=2, name="Credit limit looked up", actor="Credit Control",
                        system="SAP S/4HANA / SAP CRM",
                        description="The credit check uses whichever record the system resolves "
                                    "first.",
                        failure_points=["ERP and CRM hold different limits for the same account",
                                        "No agreed source of truth, no approval trail on overrides"]),
            ProcessStep(seq=3, name="Order released", actor="Credit Control",
                        description="The order is released, sometimes against an inflated limit."),
        ],
        after_process=[
            ProcessStep(seq=1, name="Reconciliation session", actor="Credit + Commercial",
                        description="A guided session reviews the conflicting records; the platform "
                                    "surfaces every discrepancy and proposes the canonical value."),
            ProcessStep(seq=2, name="Canonical limit agreed", actor="Credit Controller",
                        description="The teams confirm the authoritative credit limit per account."),
            ProcessStep(seq=3, name="Systems aligned", actor="Finance Systems",
                        system="SAP S/4HANA / SAP CRM",
                        description="A sync rule keeps the two systems aligned going forward."),
        ],
        business_impact=BusinessImpact(
            narrative="Removes the credit-limit disagreement across the largest retail accounts and "
                      "establishes a single agreed source of truth.",
            quantified=[
                NumberRef(value=267, unit="accounts", label="accounts reconciled",
                          text="267 of the shared accounts", sources=_src(ERP, CRM)),
                NumberRef(value=600000, unit="eur", label="largest single gap closed",
                          text="€600,000", sources=_src(ERP, CRM, AR))],
            derivation="267 shared accounts differ today; the largest single gap is "
                       "Carrefour France at €600,000 (€2.4M in CRM vs €1.8M in ERP)."),
        implementation_approach="A human-in-the-loop reconciliation supported by an assistant that "
                                "surfaces conflicts and proposes the canonical record; the credit "
                                "team makes the final call.",
        required_integrations=["SAP S/4HANA customer master", "SAP CRM customer records"],
        success_metrics=["A single agreed credit limit per active retail account",
                         "An approval trail for any future limit change"],
        dependencies=[],
        risks=["The credit and commercial teams must agree the canonical-record rules"],
        personas=["Credit Controller", "Credit Control analysts", "Commercial / account managers",
                  "Finance Systems"],
        knowledge_sources=["SAP S/4HANA customer master", "SAP CRM customer records",
                           "Credit Policy"],
        document_formats=["Structured master-data export", "Governance policy document"],
        expected_behaviour="The assistant presents the conflicting ERP and CRM values side by side "
                           "for each of the 267 shared accounts, proposes the canonical limit with "
                           "its reasoning, and records the human decision. It never changes a limit "
                           "on its own — it prepares the decision and writes the agreed value back "
                           "only after sign-off.",
        escalation="Where the credit and commercial teams disagree on the canonical value, or the "
                   "gap is material (e.g. the €600,000 Carrefour France gap), the item is held for "
                   "the Credit Controller to adjudicate rather than auto-resolved.",
        data_readiness="high — both credit limits already exist as structured fields in the ERP and "
                       "CRM; the discrepancy set (267 accounts) is computable directly from the two "
                       "extracts.",
        technical_complexity="medium — read-and-compare across two SAP systems with a governed "
                             "write-back; no model judgement on the numbers themselves.",
        operational_readiness="high — Credit Control already owns credit decisions in the RACI, so "
                              "there is a clear accountable owner to run the reconciliation.",
        value_rating="high", feasibility_rating="high", value_score=5, feasibility_score=4,
        matrix_quadrant=MatrixQuadrant.DO_FIRST, sources=_src(ERP, CRM, AR, POLICY))

    opp2 = Opportunity(
        id="OPP2", title="EDI Order Exception Handling", pattern=OppPattern.AUTOMATION,
        overview="Automate the triage of EDI order exceptions so only genuine ambiguities reach the "
                 "customer-service team.",
        before_process=[
            ProcessStep(seq=1, name="EDI exception raised", actor="Order management",
                        description="An EDI order fails or is flagged."),
            ProcessStep(seq=2, name="Manual triage", actor="Customer Service",
                        description="An agent classifies, routes and resolves it by hand.",
                        failure_points=["No classification or auto-routing",
                                        "EDI-not-processed is the top escalation"]),
        ],
        after_process=[
            ProcessStep(seq=1, name="Exception classified", actor="Rule engine",
                        description="Each exception is classified by type and auto-routed to the "
                                    "right resolution path."),
            ProcessStep(seq=2, name="Only ambiguities escalate", actor="Customer Service",
                        description="Genuine ambiguities reach an agent; the rest resolve "
                                    "automatically."),
        ],
        business_impact=BusinessImpact(
            narrative="Reduces the manual customer-service load from EDI exceptions, which are today "
                      "the most frequent escalation.",
            quantified=[NumberRef(value=34, unit="escalations",
                                  label="EDI-not-processed escalations addressed",
                                  text="34 escalations", sources=_src(ESC))],
            derivation="EDI orders not processed account for 34 of the customer-service escalations."),
        implementation_approach="A deterministic, auditable rule engine on the EDI order stream; no "
                                "AI judgement required.",
        required_integrations=["EDI / order management", "Order management module"],
        success_metrics=["Fewer manual customer-service interventions on EDI exceptions"],
        dependencies=[],
        risks=["Rule completeness — uncovered edge cases will still reach the team"],
        personas=["Customer Service agents", "Customer Service Lead"],
        knowledge_sources=["EDI / order-management channel", "Order Management SOP",
                           "Customer-service escalation log"],
        document_formats=["Structured transactional export", "Operational log"],
        expected_behaviour="Each EDI exception is classified by type against the documented rules and "
                           "auto-routed to its resolution path. Clear-cut cases (the bulk of the "
                           "1,196 unfulfilled EDI orders) resolve without a person; the agent's "
                           "queue holds only genuine ambiguities.",
        escalation="Any exception that does not match a known rule, or that the rule engine "
                   "classifies with low confidence, is routed to a Customer Service agent with the "
                   "classification and source order attached — nothing is silently dropped.",
        data_readiness="high — the order-flow export already carries the fulfilment status and "
                       "channel needed to identify and type EDI exceptions.",
        technical_complexity="low — a deterministic, auditable rule engine on the EDI stream; no AI "
                             "judgement required, so it is the simplest to stand up.",
        operational_readiness="medium — Customer Service handles these exceptions today, but EDI has "
                              "no named owner in the RACI, so accountability for the new process "
                              "must be assigned first.",
        value_rating="high", feasibility_rating="high", value_score=4, feasibility_score=5,
        matrix_quadrant=MatrixQuadrant.DO_FIRST, sources=_src(ESC, FLOW, NOTES))

    opp3 = Opportunity(
        id="OPP3", title="AI Credit Decisioning", pattern=OppPattern.AI_AGENT,
        overview="Apply a real-time credit assessment to the EDI order stream so the channel that "
                 "carries most of your orders is no longer released without a credit check.",
        before_process=[
            ProcessStep(seq=1, name="EDI order arrives", actor="Order management",
                        description="An EDI order is received on the dominant channel."),
            ProcessStep(seq=2, name="Released without a credit gate", actor="—",
                        description="The order proceeds to fulfilment with no systematic credit "
                                    "check on the EDI channel.",
                        failure_points=["No credit gate on the channel carrying 67% of orders"]),
        ],
        after_process=[
            ProcessStep(seq=1, name="Real-time credit assessment", actor="AI Agent",
                        system="SAP S/4HANA credit + EDI stream",
                        description="Each EDI order is assessed against the reconciled customer "
                                    "master and credit policy: approve, hold, or flag."),
            ProcessStep(seq=2, name="Analyst reviews flags", actor="Credit Control",
                        description="Flagged orders go to a credit analyst; approved orders proceed."),
        ],
        business_impact=BusinessImpact(
            narrative="Brings a credit check to the EDI channel that carries 67% of orders, closing "
                      "the coverage gap once the customer master is clean.",
            quantified=[NumberRef(value=67, unit="percent", label="order share newly credit-checked",
                                  text="67% of orders", sources=_src(FLOW))],
            derivation="EDI carries 67% of orders (5,667 of 8,420); today these are released without "
                       "a systematic credit check."),
        implementation_approach="An AI agent on the EDI order stream that approves, holds or flags "
                                "each order; escalates low-confidence cases to a human.",
        required_integrations=["SAP S/4HANA credit module", "Reconciled customer master (OPP1)",
                               "EDI order stream"],
        success_metrics=["Credit assessment coverage of the EDI channel",
                         "Low rate of incorrectly held orders"],
        dependencies=["OPP1"],
        risks=["Needs the reconciled customer master (OPP1) first",
               "Credit analysts must trust and act on the agent's flags"],
        personas=["Credit Control analysts", "Credit Controller", "Customer Service (downstream)"],
        knowledge_sources=["Reconciled customer master (from OPP1)", "Credit Policy",
                           "EDI order stream"],
        document_formats=["Structured transactional export", "Governance policy document"],
        expected_behaviour="For each EDI order the agent reads the reconciled customer master and the "
                           "Credit Policy and returns one of three outcomes — approve, hold, or flag "
                           "— with the reasoning shown. Approved orders proceed to fulfilment; held "
                           "and flagged orders wait for a human decision.",
        escalation="Low-confidence assessments and every 'hold' are routed to a credit analyst with "
                   "the order, the limit used and the reasoning, so the analyst makes the final "
                   "call. The agent never releases a held order on its own.",
        data_readiness="medium — depends on the reconciled customer master from OPP1; until credit "
                       "limits agree across the two systems, a real-time check cannot be trusted.",
        technical_complexity="high — real-time assessment on the live EDI stream against the ERP "
                             "credit module, with model judgement that must be auditable.",
        operational_readiness="low — credit analysts must come to trust and act on the agent's "
                              "flags, and the EDI channel has no named owner today; this needs the "
                              "foundations (OPP1, EDI ownership) in place first.",
        value_rating="high", feasibility_rating="low", value_score=5, feasibility_score=2,
        matrix_quadrant=MatrixQuadrant.PLAN_FOR, sources=_src(FLOW, RACI))

    REG = "edi-integration-register-opella-europe"
    opp4 = Opportunity(
        id="OPP4", title="EDI Connection Transition Programme", pattern=OppPattern.MODERNISATION,
        overview="Bring the six EDI connections still operated by the former parent onto the "
                 "organisation's own platform, so it controls the service end to end.",
        before_process=[
            ProcessStep(seq=1, name="Incident on a parent-run connection", actor="Customer Service",
                        description="An EDI incident occurs on one of the six connections operated "
                                    "by the former parent."),
            ProcessStep(seq=2, name="Resolution waits on the parent", actor="Former parent IT",
                        description="Resolution depends on the parent's team under the transitional "
                                    "arrangement.",
                        failure_points=["No control over response times on these connections",
                                        "Governing service terms are not in the organisation's "
                                        "hands"]),
        ],
        after_process=[
            ProcessStep(seq=1, name="Connection migrated", actor="EDI integration team",
                        system="Own EDI platform",
                        description="Each connection is migrated onto the organisation's own EDI "
                                    "platform on the published schedule."),
            ProcessStep(seq=2, name="Service owned end to end", actor="EDI integration team",
                        description="Incidents are resolved under the organisation's own service "
                                    "levels, with no dependency on the former parent."),
        ],
        business_impact=BusinessImpact(
            narrative="Removes the dependency on the former parent for the connections carrying "
                      "several of the largest retail accounts.",
            quantified=[NumberRef(value=6, unit="count", label="connections brought in-house",
                                  text="6 of 14 connections", sources=_src(NOTES))],
            derivation="Six of the fourteen live connections remain under the transitional "
                       "arrangement today."),
        implementation_approach="A phased migration on the published schedule, one connection at a "
                                "time, validated against live order flow before the parent's "
                                "connection is decommissioned.",
        required_integrations=["Own EDI platform", "Former parent's EDI platform (during cutover)"],
        success_metrics=["All connections operated on the organisation's own platform",
                         "Incident resolution under the organisation's own service levels"],
        dependencies=[],
        risks=["The governing service terms are not in the document pack",
               "Migration dates for the later connections are provisional"],
        personas=["EDI integration team", "Customer Service", "Commercial / account managers"],
        knowledge_sources=["EDI integration register", "EDI dispute working notes"],
        document_formats=["Technical register", "Operational working notes"],
        expected_behaviour="Each of the six connections is migrated to the organisation's own "
                           "platform on the schedule and validated against live order flow before "
                           "the parent's connection is retired. The programme touches one connection "
                           "at a time so order flow is never interrupted.",
        escalation="Where a connection's service terms or migration date are unclear, the item is "
                   "held for the EDI integration lead and the transition programme office rather "
                   "than migrated blind.",
        data_readiness="medium — the connection inventory and managing entity are documented, but "
                       "the governing service terms sit in a schedule not included in the pack.",
        technical_complexity="high — a live cutover of production EDI connections between two "
                             "platforms, coordinated with an external party.",
        operational_readiness="medium — the organisation owns eight connections already and has run "
                              "two migrations, but the remaining six depend on the former parent's "
                              "cooperation.",
        value_rating="medium", feasibility_rating="medium", value_score=3, feasibility_score=3,
        matrix_quadrant=MatrixQuadrant.PLAN_FOR, sources=_src(REG, NOTES))

    opp5 = Opportunity(
        id="OPP5", title="Customer Master Population Alignment", pattern=OppPattern.HITL,
        overview="Align the two customer masters on which accounts exist, so the credit "
                 "reconciliation has a clean, complete population to work from.",
        before_process=[
            ProcessStep(seq=1, name="Account created in the ERP", actor="Customer Service",
                        description="A new account is set up in the ERP."),
            ProcessStep(seq=2, name="No matching CRM record", actor="—",
                        description="No matching record is maintained in the CRM.",
                        failure_points=["22 accounts exist in the ERP with no CRM counterpart",
                                        "Any process reading the CRM misses them"]),
        ],
        after_process=[
            ProcessStep(seq=1, name="Populations compared", actor="Data steward",
                        system="ERP / CRM",
                        description="The two masters are compared and the missing accounts "
                                    "surfaced for review."),
            ProcessStep(seq=2, name="Records aligned & governed", actor="Data steward",
                        description="Missing records are created or retired under a maintained "
                                    "onboarding rule so the populations stay aligned."),
        ],
        business_impact=BusinessImpact(
            narrative="Aligns the account populations so the credit reconciliation works from a "
                      "complete, agreed set of accounts.",
            quantified=[NumberRef(value=22, unit="accounts", label="accounts to align",
                                  text="22 accounts", sources=_src(ERP, CRM))],
            derivation="The ERP holds 340 active accounts to the CRM's 318 — a 22-account "
                       "difference."),
        implementation_approach="A human-in-the-loop alignment: the platform surfaces the population "
                                "difference and a data steward confirms each create-or-retire "
                                "decision.",
        required_integrations=["SAP S/4HANA customer master", "SAP CRM customer records"],
        success_metrics=["The two masters hold the same active-account population",
                         "A maintained rule keeps them aligned at onboarding"],
        dependencies=[],
        prerequisite_for=[],
        risks=["Some ERP-only accounts may be legitimately inactive and need retiring, not adding"],
        personas=["Data steward", "Commercial / account managers", "Finance Systems"],
        knowledge_sources=["SAP S/4HANA customer master", "SAP CRM customer records"],
        document_formats=["Structured master-data export"],
        expected_behaviour="The platform lists the accounts present in one master but not the other "
                           "and proposes a create-or-retire action for each; a data steward confirms "
                           "every decision. It never creates or retires a record on its own.",
        escalation="Any account whose status is ambiguous (e.g. possibly inactive) is held for the "
                   "data steward and the account manager to decide rather than auto-aligned.",
        data_readiness="high — both account populations are structured fields; the 22-account "
                       "difference is computable directly from the two extracts.",
        technical_complexity="low — a compare-and-confirm over two master-data extracts.",
        operational_readiness="medium — the alignment needs a named data steward and a maintained "
                              "onboarding rule, which do not exist today.",
        value_rating="medium", feasibility_rating="high", value_score=3, feasibility_score=4,
        matrix_quadrant=MatrixQuadrant.PLAN_FOR, sources=_src(ERP, CRM))

    roadmap = [
        RoadmapHorizon(horizon="H1", window="0-6 months", theme="Stabilise the foundations", items=[
            RoadmapItem(title="Customer Master Reconciliation", opportunity_id="OPP1",
                        rationale="Establishes the single source of truth the rest depends on."),
            RoadmapItem(title="EDI Order Exception Handling", opportunity_id="OPP2",
                        rationale="Cuts the most frequent escalation; independent, can run now."),
            RoadmapItem(title="Customer Master Population Alignment", opportunity_id="OPP5",
                        rationale="Aligns the account populations so the reconciliation is clean."),
        ]),
        RoadmapHorizon(horizon="H2", window="6-18 months", theme="Close the gaps", items=[
            RoadmapItem(title="AI Credit Decisioning", opportunity_id="OPP3",
                        rationale="Credit-checks the dominant EDI channel; needs OPP1 first.",
                        depends_on=["OPP1"]),
            RoadmapItem(title="EDI Connection Transition Programme", opportunity_id="OPP4",
                        rationale="Brings the six parent-run connections onto the own platform."),
        ]),
        RoadmapHorizon(horizon="H3", window="18+ months", theme="Rationalise the landscape", items=[
            RoadmapItem(title="CRM consolidation",
                        rationale="Consolidate customer data onto a single platform."),
            RoadmapItem(title="EDI modernisation",
                        rationale="Modernise the EDI integration estate."),
            RoadmapItem(title="ERP credit module upgrade",
                        rationale="Strengthen credit controls in the core ERP."),
        ]),
    ]

    return SynthesisContent(
        current_state=current, pain_points=pain_points, cross_process_patterns=cross,
        opportunities=[opp1, opp2, opp3, opp4, opp5],
        sequencing_rationale="Customer Master Reconciliation (OPP1) comes first because AI Credit "
                             "Decisioning (OPP3) needs a clean, single credit limit per account to "
                             "work. EDI Order Exception Handling (OPP2) and the population alignment "
                             "(OPP5) are independent and run in parallel from the start; the "
                             "connection transition (OPP4) follows on the published migration "
                             "schedule.",
        strategic_readiness="The current state can support the near-term moves once the customer "
                            "master is reconciled; the credit decisioning step is the main capability "
                            "to build toward.",
        dependency_notes="OPP3 depends on OPP1. OPP1, OPP2, OPP4 and OPP5 are independent of each "
                         "other and can run in parallel.",
        roadmap=roadmap,
        strategy_profile={"posture": "consolidate_modernize",
                          "notes": "Consolidate the inherited landscape while modernising for the "
                                   "EDI-dominated order reality."},
        metrics_framework=[
            MetricItem(
                name="Customer-master agreement",
                definition="Share of the 267 shared retail accounts holding a single agreed credit "
                           "limit across the ERP and CRM, with an approval trail on any change.",
                target="Every one of the 267 shared accounts reconciled, with no unapproved limit "
                       "change thereafter."),
            MetricItem(
                name="EDI fulfilment rate",
                definition="Share of EDI orders fulfilled without a manual exception, against the "
                           "1,196 (€12.4M) not fulfilled today.",
                target="A sustained, material reduction in unfulfilled EDI orders after go-live; the "
                       "1,196 baseline is the yardstick."),
            MetricItem(
                name="EDI escalation rate",
                definition="Customer-service escalations for 'EDI order not processed' — the single "
                           "most frequent escalation today (34 cases).",
                target="A clear downward trend against the 34-case baseline as exceptions resolve "
                       "automatically."),
            MetricItem(
                name="EDI credit coverage",
                definition="Share of the EDI channel (67% of all orders) that receives a systematic "
                           "credit check before release.",
                target="Near-complete credit coverage of the EDI channel once the customer master is "
                       "reconciled."),
            MetricItem(
                name="Credit-decision accuracy",
                definition="Share of automated credit assessments (approve/hold/flag) that a credit "
                           "analyst confirms as correct on review.",
                target="A high confirmation rate at go-live, improving through tuning; tracked "
                       "against analyst review."),
            MetricItem(
                name="EDI connection ownership",
                definition="Share of the 14 live EDI connections operated on the organisation's own "
                           "platform rather than the former parent's (8 of 14 today).",
                target="All 14 connections on the organisation's own platform on the published "
                       "migration schedule."),
            MetricItem(
                name="Customer-master population alignment",
                definition="Whether the ERP and CRM hold the same active-account population (a "
                           "22-account difference today).",
                target="A single agreed active-account population across both systems, kept aligned "
                       "at onboarding."),
        ],
        evidence_register=[
            EvidenceRow(finding="PP1", source="ERP and CRM customer exports",
                        evidence_type="Structured data",
                        data_point="267 of 318 shared accounts hold a different credit limit; "
                                   "Carrefour France differs by €600,000.", confidence="Verified"),
            EvidenceRow(finding="PP1", source="Credit Policy",
                        evidence_type="Policy document",
                        data_point="The ERP is named the sole authoritative system for credit "
                                   "limits.", confidence="Verified"),
            EvidenceRow(finding="PP1", source="Accounts Receivable review notes",
                        evidence_type="Review note",
                        data_point="'Our credit policy does not define which system is "
                                   "authoritative.'", confidence="Amber"),
            EvidenceRow(finding="PP2", source="Order flow export",
                        evidence_type="Structured data",
                        data_point="EDI carries 67.3% of orders (5,667 of 8,420).",
                        confidence="Verified"),
            EvidenceRow(finding="PP2", source="Order Management SOP; Order-to-Cash RACI",
                        evidence_type="Policy documents",
                        data_point="Neither the SOP nor the RACI covers the EDI channel.",
                        confidence="Verified"),
            EvidenceRow(finding="PP3", source="Order flow export; escalation log",
                        evidence_type="Structured data",
                        data_point="1,196 unfulfilled EDI orders (€12.4M); 34 'EDI not processed' "
                                   "escalations.", confidence="Verified"),
            EvidenceRow(finding="PP4", source="EDI integration register",
                        evidence_type="Technical register",
                        data_point="6 of 14 connections remain under the transitional service "
                                   "arrangement.", confidence="Verified"),
            EvidenceRow(finding="PP4", source="EDI dispute working notes",
                        evidence_type="Working notes",
                        data_point="Governing service terms and a firm transfer date are not in the "
                                   "pack.", confidence="Gap"),
            EvidenceRow(finding="PP5", source="ERP and CRM customer exports",
                        evidence_type="Structured data",
                        data_point="340 active accounts in the ERP versus 318 in the CRM — a "
                                   "22-account difference.", confidence="Verified"),
        ],
        risk_register=[
            RiskItem(risk="The credit and commercial teams cannot agree the canonical credit limit "
                          "for a contested account.",
                     likelihood="Medium", impact="High",
                     mitigation="Material gaps (e.g. the €600,000 Carrefour France gap) are held "
                                "for the Credit Controller to adjudicate; nothing auto-resolves.",
                     owner="Credit Controller"),
            RiskItem(risk="The automated EDI exception rules do not cover an edge case, so it still "
                          "reaches an agent.",
                     likelihood="Medium", impact="Medium",
                     mitigation="Unmatched and low-confidence exceptions route to an agent with the "
                                "source order attached; coverage is reviewed as new types appear.",
                     owner="Customer Service Lead"),
            RiskItem(risk="Credit analysts do not trust the automated credit assessment and "
                          "override it by default.",
                     likelihood="Medium", impact="High",
                     mitigation="Every hold and low-confidence case is shown with its reasoning and "
                                "the limit used, so analysts can confirm rather than re-derive.",
                     owner="Credit Controller"),
            RiskItem(risk="A TSA connection's migration slips because the former parent's "
                          "cooperation or service terms are unclear.",
                     likelihood="High", impact="Medium",
                     mitigation="Migrate one connection at a time on the published schedule, "
                                "validating against live order flow before decommissioning.",
                     owner="EDI integration lead"),
            RiskItem(risk="ERP-only accounts are added to the CRM when some should instead be "
                          "retired as inactive.",
                     likelihood="Low", impact="Medium",
                     mitigation="A data steward confirms each create-or-retire decision; ambiguous "
                                "accounts are held for the account manager.",
                     owner="Data steward"),
        ],
        traceability=[
            TraceRow(pain_point="PP1", summary="ERP/CRM disagree on credit limits",
                     severity="High", recommendation="R-01", opportunity="OPP1",
                     expected_outcome="One agreed credit limit per account, with an approval trail.",
                     horizon="H1"),
            TraceRow(pain_point="PP2", summary="EDI channel undocumented and unowned",
                     severity="High", recommendation="R-03", opportunity="OPP3",
                     expected_outcome="A credit gate on the channel carrying most order value.",
                     horizon="H2"),
            TraceRow(pain_point="PP3", summary="EDI order failures concentrate here",
                     severity="High", recommendation="R-02", opportunity="OPP2",
                     expected_outcome="Routine EDI exceptions resolve without an agent.",
                     horizon="H1"),
            TraceRow(pain_point="PP4", summary="Six connections under the former parent",
                     severity="Medium", recommendation="R-04", opportunity="OPP4",
                     expected_outcome="All connections on the organisation's own platform.",
                     horizon="H2"),
            TraceRow(pain_point="PP5", summary="Customer masters hold different populations",
                     severity="Medium", recommendation="R-05", opportunity="OPP5",
                     expected_outcome="One agreed active-account population across both systems.",
                     horizon="H1"),
        ],
        executive_summary=ExecutiveSummary(
            headline="Order-to-Cash runs on two customer systems that disagree on credit, and a "
                     "dominant electronic channel that no procedure owns — together putting "
                     "material order value and revenue at risk.",
            situation="Orders arrive mainly through EDI, which carries two-thirds of volume yet sits "
                      "outside the documented process and has no owner. Credit checks run against "
                      "two systems whose limits diverge for 267 of 318 shared accounts.",
            opportunity="Reconcile the customer master to a single agreed source of truth, bring the "
                        "electronic channel under documented ownership with automated exception "
                        "handling, then add a real-time credit gate to the channel that needs it "
                        "most."),
        target_state="Order-to-Cash converges on one trusted customer master, with every credit "
                     "limit agreed across both systems and changes governed by an approval trail. "
                     "The electronic channel is owned, documented, and self-healing: routine "
                     "exceptions resolve automatically and only genuine ambiguities reach a person. "
                     "Every order — whatever the channel — passes a consistent credit check before "
                     "release, so the volume that flows through EDI is no longer a blind spot.")


def _table(t) -> DataTable:
    return DataTable(title=t.get("title", ""), columns=list(t.get("columns", [])),
                     rows=[list(r) for r in t.get("rows", [])], caption=t.get("caption", ""),
                     note=t.get("note", ""), sources=[_sref(s) for s in t.get("sources", [])])


def _from_payload(payload: dict) -> SynthesisContent:
    """Map a live emit_synthesis / fan-out payload onto the dataclasses. Defensive: tolerates missing
    optional keys so a partial emit degrades rather than crashes. Maps the DEEP fields too (data
    tables, process detail, per-PP detail tables, evidence/risk/traceability registers, baseline
    stats) so the fan-out's merged payload reconstructs a reference-depth SynthesisContent."""
    cs = payload.get("current_state", {})
    current = CurrentState(
        domain_overview=cs.get("domain_overview", ""),
        process_summary=cs.get("process_summary", ""),
        process_flow=[_step(s) for s in cs.get("process_flow", [])],
        process_inventory=[InventoryItem(name=i["name"], purpose=i.get("purpose", ""))
                           for i in cs.get("process_inventory", [])],
        ownership_map=[RaciRow(activity=r["activity"], responsible=r.get("responsible", ""),
                               accountable=r.get("accountable", ""), consulted=r.get("consulted", ""),
                               informed=r.get("informed", "")) for r in cs.get("ownership_map", [])],
        system_inventory=[InventoryItem(name=i["name"], purpose=i.get("role", ""),
                                        system_of_record_for=i.get("system_of_record_for", ""))
                          for i in cs.get("system_inventory", [])],
        handoff_catalogue=[Handoff(from_step=h["from_step"], to_step=h["to_step"],
                                   mechanism=h.get("mechanism", ""))
                           for h in cs.get("handoff_catalogue", [])],
        bounded_contexts=[BoundedContext(
            name=b["name"], kind=b.get("kind", "core"), owner=b.get("owner", ""),
            responsibilities=b.get("responsibilities", ""),
            is_shared_kernel=bool(b.get("is_shared_kernel", False)),
            relationships=[ContextRelationship(to=r["to"], kind=r.get("kind", ""),
                                               label=r.get("label", ""))
                           for r in b.get("relationships", []) if r.get("to")])
            for b in cs.get("bounded_contexts", []) if b.get("name")],
        system_profiles=[SystemProfile(name=p["name"], role=p.get("role", ""),
                                       how_used=p.get("how_used", ""), owners=p.get("owners", ""),
                                       limitations=p.get("limitations", ""))
                         for p in cs.get("system_profiles", [])],
        format_taxonomy=[FormatPattern(label=f["label"], description=f.get("description", ""),
                                       examples=f.get("examples", ""))
                         for f in cs.get("format_taxonomy", [])],
        baseline_stats=[KeyStat(value=str(k.get("value", "")), label=k.get("label", ""),
                                sublabel=k.get("sublabel", "")) for k in cs.get("baseline_stats", [])],
        data_tables=[_table(t) for t in cs.get("data_tables", [])],
        process_detail=[ProcessDetail(title=p.get("title", ""), body=p.get("body", ""),
                                      actor=p.get("actor", ""), system=p.get("system", ""),
                                      sources=[_sref(s) for s in p.get("sources", [])])
                        for p in cs.get("process_detail", [])])
    pain_points = [PainPoint(
        id=p["id"], title=p["title"], impact_rank=p.get("impact_rank", 1),
        from_finding=p.get("from_finding", ""), description=p.get("description", ""),
        root_cause=p.get("root_cause", ""), failure_pattern=p.get("failure_pattern", ""),
        business_consequence=p.get("business_consequence", ""), category=p.get("category", ""),
        severity=p.get("severity", ""),
        quantified=[_num(n) for n in p.get("quantified", [])],
        detail_table=_table(p["detail_table"]) if p.get("detail_table") else None,
        sources=[_sref(s) for s in p.get("sources", [])]) for p in payload.get("pain_points", [])]
    opps = [_opp(o) for o in payload.get("opportunities", [])]
    tr = payload.get("transformation", {})
    roadmap = [RoadmapHorizon(horizon=h["horizon"], window=h.get("window", ""),
                              theme=h.get("theme", ""),
                              items=[RoadmapItem(title=i["title"], rationale=i.get("rationale", ""),
                                                 opportunity_id=i.get("opportunity_id"),
                                                 depends_on=i.get("depends_on", []))
                                     for i in h.get("items", [])])
               for h in payload.get("roadmap", [])]
    return SynthesisContent(
        current_state=current, pain_points=pain_points,
        cross_process_patterns=payload.get("cross_process_patterns", []),
        opportunities=opps, sequencing_rationale=tr.get("sequencing_rationale", ""),
        strategic_readiness=tr.get("strategic_readiness", ""),
        dependency_notes=tr.get("dependency_notes", ""), roadmap=roadmap,
        # guard: the model may emit strategy_profile as a string — keep it a dict so downstream
        # spreads/renders never choke (the live builder overlays the typed StrategyProfile anyway).
        strategy_profile=sp if isinstance((sp := payload.get("strategy_profile", {})), dict) else {},
        metrics_framework=[MetricItem(name=m["name"], definition=m.get("definition", ""),
                                      target=m.get("target", ""))
                           for m in payload.get("metrics_framework", [])],
        executive_summary=_exec_summary(payload.get("executive_summary", {})),
        target_state=payload.get("target_state", ""),
        evidence_register=[EvidenceRow(finding=e.get("finding", ""), source=e.get("source", ""),
                                       evidence_type=e.get("evidence_type", ""),
                                       data_point=e.get("data_point", ""),
                                       confidence=e.get("confidence", ""))
                           for e in payload.get("evidence_register", [])],
        risk_register=[RiskItem(risk=r.get("risk", ""), likelihood=r.get("likelihood", ""),
                                impact=r.get("impact", ""), mitigation=r.get("mitigation", ""),
                                owner=r.get("owner", "")) for r in payload.get("risk_register", [])],
        traceability=[TraceRow(pain_point=t.get("pain_point", ""), summary=t.get("summary", ""),
                               severity=t.get("severity", ""),
                               recommendation=t.get("recommendation", ""),
                               opportunity=t.get("opportunity", ""),
                               expected_outcome=t.get("expected_outcome", ""),
                               horizon=t.get("horizon", "")) for t in payload.get("traceability", [])])


def _exec_summary(es: dict) -> ExecutiveSummary:
    return ExecutiveSummary(headline=es.get("headline", ""), situation=es.get("situation", ""),
                            opportunity=es.get("opportunity", ""))


def _step(s) -> ProcessStep:
    return ProcessStep(seq=s["seq"], name=s["name"], actor=s.get("actor", ""),
                       system=s.get("system", ""), description=s.get("description", ""),
                       failure_points=s.get("failure_points", []),
                       sources=[_sref(x) for x in s.get("sources", [])])


def _num(n) -> NumberRef:
    return NumberRef(value=n["value"], unit=n.get("unit", "count"), label=n.get("label", ""),
                     text=n.get("text", ""), sources=[_sref(x) for x in n.get("sources", [])])


def _sref(s) -> SourceRef:
    return SourceRef(doc_id=s.get("doc_key", s.get("doc_id", "")))


def _opp(o) -> Opportunity:
    bi = o.get("business_impact", {})
    return Opportunity(
        id=o["id"], title=o["title"], pattern=OppPattern(o["pattern"]),
        overview=o.get("overview", ""), before_process=[_step(s) for s in o.get("before_process", [])],
        after_process=[_step(s) for s in o.get("after_process", [])],
        business_impact=BusinessImpact(narrative=bi.get("narrative", ""),
                                       quantified=[_num(n) for n in bi.get("quantified", [])],
                                       derivation=bi.get("derivation", "")),
        implementation_approach=o.get("implementation_approach", ""),
        required_integrations=o.get("required_integrations", []),
        success_metrics=o.get("success_metrics", []), dependencies=o.get("dependencies", []),
        risks=o.get("risks", []), value_rating=o.get("value_rating", "medium"),
        feasibility_rating=o.get("feasibility_rating", "medium"),
        value_score=o.get("value_score", 3), feasibility_score=o.get("feasibility_score", 3),
        matrix_quadrant=MatrixQuadrant(o.get("matrix_quadrant", "consider")),
        personas=o.get("personas", []), expected_behaviour=o.get("expected_behaviour", ""),
        escalation=o.get("escalation", ""),
        knowledge_sources=o.get("knowledge_sources", []),
        document_formats=o.get("document_formats", []),
        data_readiness=o.get("data_readiness", ""),
        technical_complexity=o.get("technical_complexity", ""),
        operational_readiness=o.get("operational_readiness", ""),
        sources=[_sref(s) for s in o.get("sources", [])])
