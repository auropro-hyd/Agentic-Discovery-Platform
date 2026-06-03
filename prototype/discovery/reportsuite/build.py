"""Build a SynthesisContent for the 6-report suite.

Two sources:
  - fixture (demo default): hand-grounded content in fixture_o2c(); every number traces to the
    verified findings, validated through synthesis.validate_synthesis at build time.
  - live (--live-synth): synthesis.run_synthesis() output mapped onto the dataclasses.

Code (not the model) owns the PP<->OPP links, prerequisite_for, matrix quadrant, and the
deterministic source index.
"""
from __future__ import annotations

from .. import docnames
from ..models import (
    BusinessImpact, CurrentState, Handoff, InventoryItem, MatrixQuadrant, NumberRef, Opportunity,
    OppPattern, PainPoint, ProcessStep, RaciRow, RoadmapHorizon, RoadmapItem, SourceDoc,
    SourceRef, SynthesisContent,
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
                    doc_keys=None, model=None, suppress_names=None) -> SynthesisContent:
    if live:
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
    return content


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
    )

    pain_points = [
        PainPoint(
            id="PP1", title="Two customer systems disagree on credit limits", impact_rank=1,
            from_finding="F1",
            description="Your ERP and CRM hold different credit limits and payment terms for the "
                        "same major retail accounts, with no single agreed source of truth.",
            root_cause="Both systems were carried over at carve-out and were never reconciled; CRM "
                       "limits were updated by hand without an approval trail.",
            failure_pattern="Orders are released against whichever limit the system resolves first, "
                            "so the same account can trade on two different limits.",
            quantified=[
                NumberRef(value=267, unit="accounts", label="accounts with different credit limits",
                          text="267 of the shared accounts", sources=_src(ERP, CRM)),
                NumberRef(value=600000, unit="eur", label="largest single gap (Carrefour France)",
                          text="€600,000", sources=_src(ERP, CRM, AR)),
            ],
            sources=_src(ERP, CRM, AR, POLICY)),
        PainPoint(
            id="PP2", title="Two-thirds of orders run on an undocumented channel", impact_rank=2,
            from_finding="F2",
            description="EDI carries most of your order volume, yet it is not covered by the Order "
                        "Management SOP and has no owner in the Order-to-Cash RACI.",
            root_cause="The documented process was written for manual and email orders; EDI grew "
                       "to dominate without the procedure or accountability catching up.",
            failure_pattern="EDI orders that fail are handled informally, with no governed process "
                            "or named owner.",
            quantified=[
                NumberRef(value=67, unit="percent", label="EDI share of orders",
                          text="67% of orders (5,667 of 8,420)", sources=_src(FLOW, NOTES)),
            ],
            sources=_src(FLOW, RACI, SOP, NOTES)),
        PainPoint(
            id="PP3", title="EDI order failures concentrate on the unowned channel", impact_rank=3,
            from_finding="F3",
            description="A large block of EDI orders is not fulfilled, on the same channel that has "
                        "no documented process or owner.",
            root_cause="Without a governed EDI process, failures are absorbed reactively through "
                       "manual re-entry rather than prevented.",
            failure_pattern="EDI orders not processed is the single most common customer-service "
                            "escalation.",
            quantified=[
                NumberRef(value=1196, unit="orders", label="EDI orders not fulfilled",
                          text="1,196 EDI orders", sources=_src(FLOW)),
                NumberRef(value=12362493.74, unit="eur", label="value not fulfilled",
                          text="€12.4M", sources=_src(FLOW)),
                NumberRef(value=34, unit="escalations", label="EDI-not-processed escalations",
                          text="34 escalations", sources=_src(ESC, NOTES)),
            ],
            sources=_src(FLOW, ESC, NOTES)),
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
        value_rating="high", feasibility_rating="low", value_score=5, feasibility_score=2,
        matrix_quadrant=MatrixQuadrant.PLAN_FOR, sources=_src(FLOW, RACI))

    roadmap = [
        RoadmapHorizon(horizon="H1", window="0-6 months", theme="Stabilise the foundations", items=[
            RoadmapItem(title="Customer Master Reconciliation", opportunity_id="OPP1",
                        rationale="Establishes the single source of truth the rest depends on."),
            RoadmapItem(title="EDI Order Exception Handling", opportunity_id="OPP2",
                        rationale="Cuts the most frequent escalation; independent, can run now."),
            RoadmapItem(title="Transition the EDI connections still operated under the transitional "
                              "service arrangement", rationale="Brings the inherited connections "
                              "under the organisation's own control as part of standing up "
                              "independently."),
        ]),
        RoadmapHorizon(horizon="H2", window="6-18 months", theme="Close the credit gap", items=[
            RoadmapItem(title="AI Credit Decisioning", opportunity_id="OPP3",
                        rationale="Credit-checks the dominant EDI channel; needs OPP1 first.",
                        depends_on=["OPP1"]),
            RoadmapItem(title="EDI middleware assessment",
                        rationale="Assess the EDI integration layer ahead of modernisation."),
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
        opportunities=[opp1, opp2, opp3],
        sequencing_rationale="Customer Master Reconciliation (OPP1) comes first because AI Credit "
                             "Decisioning (OPP3) needs a clean, single credit limit per account to "
                             "work. EDI Order Exception Handling (OPP2) is independent and runs in "
                             "parallel from the start.",
        strategic_readiness="The current state can support the near-term moves once the customer "
                            "master is reconciled; the credit decisioning step is the main capability "
                            "to build toward.",
        dependency_notes="OPP3 depends on OPP1. OPP1 and OPP2 are independent of each other.",
        roadmap=roadmap,
        strategy_profile={"posture": "consolidate_modernize",
                          "notes": "Consolidate the inherited landscape while modernising for the "
                                   "EDI-dominated order reality."})


def _from_payload(payload: dict) -> SynthesisContent:
    """Map a live emit_synthesis payload onto the dataclasses. Defensive: tolerates missing
    optional keys so a partial emit degrades rather than crashes."""
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
                           for h in cs.get("handoff_catalogue", [])])
    pain_points = [PainPoint(
        id=p["id"], title=p["title"], impact_rank=p.get("impact_rank", 1),
        from_finding=p.get("from_finding", ""), description=p.get("description", ""),
        root_cause=p.get("root_cause", ""), failure_pattern=p.get("failure_pattern", ""),
        quantified=[_num(n) for n in p.get("quantified", [])],
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
        strategy_profile=payload.get("strategy_profile", {}))


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
        sources=[_sref(s) for s in o.get("sources", [])])
