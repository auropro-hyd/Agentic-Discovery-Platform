"""Core data models for the discovery pipeline.

These are plain dataclasses (no external deps) so the prototype runs anywhere. They are
deliberately small. The two ideas that matter most for the demo live here:

- ``SourceRef``  — every finding/recommendation cites where it came from (provenance).
- confidence is an *evidence tier*, not a model-reported probability.
"""
from __future__ import annotations

from dataclasses import dataclass, field, asdict
from enum import Enum
from typing import Any


class DocCategory(str, Enum):
    STRUCTURED = "structured"
    SEMI_STRUCTURED = "semi_structured"
    SYSTEM_SIGNAL = "system_signal"
    UNSTRUCTURED = "unstructured"
    COMPARATIVE = "comparative"
    UNKNOWN = "unknown"


class Severity(str, Enum):
    HIGH = "high"      # red  — blocks a confident answer; needs SME input
    AMBER = "amber"    # flagged, carried forward at reduced confidence
    INFO = "info"


class ConfidenceTier(str, Enum):
    """Grounded in evidence provenance, NOT in LLM self-reported certainty."""
    VERIFIED = "verified"   # corroborated across >=2 independent sources
    AMBER = "amber"         # single-source / partially corroborated
    GAP = "gap"             # asserted but unverifiable, or contradicted


@dataclass
class SourceRef:
    """A pointer back to the evidence a claim rests on."""
    doc_id: str                 # filename, e.g. "08-erp-customer-export.csv"
    locator: str = ""           # section / row / line / quote that supports the claim
    quote: str = ""             # short supporting excerpt (optional)

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


# ── grounded fact-store (the KG-lite that feeds the per-report synthesis fan-out) ───────────────
@dataclass
class QuantFact:
    """A measured number with provenance — the only carrier of figures into the fact-store. Gated
    against the run's allow-list exactly like a NumberRef."""
    label: str
    value: float
    unit: str = "count"
    sources: list[str] = field(default_factory=list)   # doc ids
    tier: str = "verified"                              # verified | amber | gap

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass
class DocQuote:
    """A verbatim snippet from a source document — powers pattern-evidence and quote boxes. Must
    appear verbatim in the document (same rule as a finding's narrative_values)."""
    text: str
    doc_id: str
    locator: str = ""
    tier: str = "verified"

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass
class EntityFact:
    """A grounded entity (system / account / connection / actor / process) with typed attributes —
    e.g. an account with {erp_limit, crm_limit, migration_source}. Attribute VALUES are strings
    restated from the source; numeric attributes still trace to the allow-list when rendered."""
    kind: str                                           # generic, derived from the data (not o2c-specific)
    name: str
    attributes: dict[str, str] = field(default_factory=dict)
    sources: list[str] = field(default_factory=list)
    tier: str = "verified"

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass
class Relation:
    """A grounded relationship between two entities/steps (handoff_to / conflicts_with / owned_by /
    runs_on / triggers)."""
    src: str
    kind: str
    dst: str
    sources: list[str] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass
class FactStore:
    """The grounded data plane the synthesis fan-out reads from — a lightweight knowledge graph of
    measured numbers, verbatim quotes, typed entities, and relations. Every member carries its
    source(s) + confidence tier. Domain-agnostic: a domain simply has fewer facts where its data is
    thinner. Replaces the flat ~3-finding waist as the thing synthesis expands from."""
    quant: list[QuantFact] = field(default_factory=list)
    quotes: list[DocQuote] = field(default_factory=list)
    entities: list[EntityFact] = field(default_factory=list)
    relations: list[Relation] = field(default_factory=list)

    def numbers_allow(self) -> set[float]:
        """The measured numbers this store grounds (for the per-section grounding gate)."""
        out: set[float] = set()
        for q in self.quant:
            try:
                out.add(round(float(q.value), 4))
            except (TypeError, ValueError):
                continue
        return out

    def slice_for(self, *terms: str) -> "FactStore":
        """The relevant subset of the store for one report/opportunity generation — members whose
        label/name/text/attributes mention any of the given (case-insensitive) terms. Empty terms →
        the whole store. Deterministic (preserves order)."""
        if not terms:
            return self
        needles = [t.lower() for t in terms if t]

        def hit(*texts: str) -> bool:
            blob = " ".join(t.lower() for t in texts if t)
            return any(n in blob for n in needles)
        return FactStore(
            quant=[q for q in self.quant if hit(q.label, q.unit)],
            quotes=[d for d in self.quotes if hit(d.text, d.doc_id, d.locator)],
            entities=[e for e in self.entities
                      if hit(e.kind, e.name, " ".join(f"{k} {v}" for k, v in e.attributes.items()))],
            relations=[r for r in self.relations if hit(r.src, r.kind, r.dst)])

    def to_dict(self) -> dict[str, Any]:
        return {"quant": [q.to_dict() for q in self.quant],
                "quotes": [d.to_dict() for d in self.quotes],
                "entities": [e.to_dict() for e in self.entities],
                "relations": [r.to_dict() for r in self.relations]}


@dataclass
class StrategyProfile:
    """The locked per-engagement strategic direction (read from the domain manifest). Shapes the
    STRATEGIC reports (03 recommendation, 05 roadmap); the tactical portfolio (04) stays
    direction-agnostic. A neutral default applies when a manifest declares none."""
    direction_type: str = ""                            # consolidate|modernize|stabilize|divest|…
    horizon: str = ""                                   # e.g. "0-6 months"
    strategic_constraints: str = ""
    stakeholder_priorities: list[str] = field(default_factory=list)
    out_of_scope: str = ""
    success_definition: str = ""

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)

    def brief(self) -> str:
        """A short prompt brief for the strategic-report synthesis calls. '' when neutral."""
        bits = []
        if self.direction_type:
            bits.append(f"Direction: {self.direction_type}")
        if self.horizon:
            bits.append(f"Horizon: {self.horizon}")
        if self.strategic_constraints:
            bits.append(f"Constraints: {self.strategic_constraints}")
        if self.stakeholder_priorities:
            bits.append("Priorities: " + ", ".join(self.stakeholder_priorities))
        if self.out_of_scope:
            bits.append(f"Out of scope: {self.out_of_scope}")
        if self.success_definition:
            bits.append(f"Success: {self.success_definition}")
        return " · ".join(bits)


@dataclass
class PlanningAssumption:
    """A forward-looking statement the data cannot COMPUTE (a date, owner-by-role, SLA, threshold,
    cadence, cost, or sequence). Generated as a clearly-labelled assumption — never presented as a
    discovered fact — with the grounded `basis` it is anchored to (if any). The renderer marks it
    visibly so a reader never mistakes it for measured data."""
    statement: str
    kind: str = "sequence"                              # date|owner|sla|threshold|cadence|cost|sequence
    basis: str = ""                                     # the grounded fact it is anchored to

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass
class Document:
    doc_id: str
    path: str
    category: DocCategory = DocCategory.UNKNOWN
    title: str = ""
    summary: str = ""
    text: str = ""              # raw text (CSVs are rendered to a compact preview)

    def to_dict(self) -> dict[str, Any]:
        d = asdict(self)
        d["category"] = self.category.value
        d.pop("text", None)     # keep serialized knowledge compact
        return d


@dataclass
class Entity:
    """A system, process, actor/owner, or decision point extracted from a doc."""
    name: str
    kind: str                   # "system" | "process" | "actor" | "decision" | "handoff"
    sources: list[SourceRef] = field(default_factory=list)
    attributes: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        return {
            "name": self.name,
            "kind": self.kind,
            "sources": [s.to_dict() for s in self.sources],
            "attributes": self.attributes,
        }


@dataclass
class CandidateResolution:
    """One of the 2-3 ranked answers offered to the SME for a flagged finding."""
    id: str                     # "candidate_1"
    summary: str
    rationale: str = ""
    evidence_strength: str = "" # "strong" | "moderate" | "weak"
    sources: list[SourceRef] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        d = asdict(self)
        d["sources"] = [s.to_dict() for s in self.sources]
        return d


@dataclass
class Finding:
    """A contradiction or gap surfaced by cross-referencing documents."""
    id: str                     # "F1"
    title: str
    severity: Severity
    description: str
    business_consequence: str = ""
    sources: list[SourceRef] = field(default_factory=list)
    candidates: list[CandidateResolution] = field(default_factory=list)
    confidence: ConfidenceTier = ConfidenceTier.AMBER

    # filled in by the SME-resolve stage
    resolved: bool = False
    chosen_candidate_id: str | None = None
    resolution_note: str = ""

    def to_dict(self) -> dict[str, Any]:
        return {
            "id": self.id,
            "title": self.title,
            "severity": self.severity.value,
            "description": self.description,
            "business_consequence": self.business_consequence,
            "sources": [s.to_dict() for s in self.sources],
            "candidates": [c.to_dict() for c in self.candidates],
            "confidence": self.confidence.value,
            "resolved": self.resolved,
            "chosen_candidate_id": self.chosen_candidate_id,
            "resolution_note": self.resolution_note,
        }


@dataclass
class Recommendation:
    """A transformation recommendation with a justification and references."""
    title: str
    horizon: str                # "now" | "next" | "later"
    intervention: str           # "modernize" | "automate" | "agent" | "hitl"
    justification: str = ""
    sources: list[SourceRef] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        d = asdict(self)
        d["sources"] = [s.to_dict() for s in self.sources]
        return d


# ===========================================================================
# 6-report suite models (client-facing). A NumberRef is the only carrier of a
# quantitative claim; its value must trace to the findings' allow-list.
# ===========================================================================
class OppPattern(str, Enum):
    HITL = "hitl_workflow"
    AUTOMATION = "automation"
    AI_AGENT = "ai_agent"
    MODERNISATION = "modernisation"     # replatform / consolidate / upgrade an existing system


class MatrixQuadrant(str, Enum):
    DO_FIRST = "do_first"
    PLAN_FOR = "plan_for"
    CONSIDER = "consider"
    DEPRIORITISE = "deprioritise"


@dataclass
class NumberRef:
    value: float
    unit: str = "count"      # count|eur|percent|ratio|accounts|orders|escalations
    label: str = ""
    text: str = ""           # readable form, e.g. "5,667 of 8,420 orders (67%)"
    sources: list[SourceRef] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        d = asdict(self)
        d["sources"] = [s.to_dict() for s in self.sources]
        return d


@dataclass
class ProcessStep:
    seq: int
    name: str
    actor: str = ""
    system: str = ""          # business system NAME (e.g. "SAP S/4HANA"), never a file id
    description: str = ""
    failure_points: list[str] = field(default_factory=list)  # empty for AFTER + Report 01
    sources: list[SourceRef] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        d = asdict(self)
        d["sources"] = [s.to_dict() for s in self.sources]
        return d


@dataclass
class RaciRow:
    activity: str
    responsible: str = ""
    accountable: str = ""
    consulted: str = ""
    informed: str = ""

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass
class InventoryItem:
    name: str
    purpose: str = ""
    system_of_record_for: str = ""

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass
class Handoff:
    from_step: str
    to_step: str
    mechanism: str = ""

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass
class SystemProfile:                      # a deep, narrative per-system/source profile (Report 01)
    name: str
    role: str = ""                        # what it is / what it's for
    how_used: str = ""                    # how the business actually uses it
    owners: str = ""                      # who owns / who has access
    limitations: str = ""                 # gaps, risks, constraints observed

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass
class FormatPattern:                       # the "knowledge/data format & structure" taxonomy
    label: str                             # e.g. "Type 1: Structured transactional export"
    description: str = ""
    examples: str = ""                     # which sources/docs follow this pattern

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass
class KeyStat:                             # a single big-number stat tile (Report 01 baseline)
    value: str                            # pre-formatted grounded figure, e.g. "8,420" or "67.3%"
    label: str = ""
    sublabel: str = ""

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass
class DataTable:                          # a grounded factual table restated from source documents
    """A factual reference table (channel mix, lead-times, credit bands, EDI connections, top
    accounts, DC network, …). Cells are pre-formatted strings restated verbatim from the cited
    source(s). Carried on the FACTUAL current-state report; the renderer draws it as a table and the
    grounding gate treats its source-restated figures as sourced facts (not synthesized claims)."""
    title: str
    columns: list[str] = field(default_factory=list)
    rows: list[list[str]] = field(default_factory=list)
    caption: str = ""
    note: str = ""                        # optional footnote (e.g. a sourcing caveat)
    sources: list[SourceRef] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        return {"title": self.title, "columns": self.columns, "rows": self.rows,
                "caption": self.caption, "note": self.note,
                "sources": [s.to_dict() for s in self.sources]}


@dataclass
class ProcessDetail:                      # one numbered process-inventory subsection (Report 01 §3.x)
    title: str
    body: str = ""                        # factual prose describing how the step runs
    actor: str = ""
    system: str = ""
    sources: list[SourceRef] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        return {"title": self.title, "body": self.body, "actor": self.actor,
                "system": self.system, "sources": [s.to_dict() for s in self.sources]}


@dataclass
class CurrentState:                       # Report 01 — NO severity/confidence anywhere
    domain_overview: str = ""
    process_summary: str = ""
    process_flow: list[ProcessStep] = field(default_factory=list)
    system_profiles: list[SystemProfile] = field(default_factory=list)   # deep per-system narrative
    format_taxonomy: list[FormatPattern] = field(default_factory=list)   # data/doc format patterns
    process_inventory: list[InventoryItem] = field(default_factory=list)
    ownership_map: list[RaciRow] = field(default_factory=list)
    system_inventory: list[InventoryItem] = field(default_factory=list)
    handoff_catalogue: list[Handoff] = field(default_factory=list)
    # deeper grounded baseline (all optional — a domain without them simply omits the section)
    baseline_stats: list[KeyStat] = field(default_factory=list)          # §1 volume baseline tiles
    data_tables: list[DataTable] = field(default_factory=list)           # channel mix, EDI, DCs, …
    process_detail: list[ProcessDetail] = field(default_factory=list)    # §3 process inventory detail

    def to_dict(self) -> dict[str, Any]:
        return {"domain_overview": self.domain_overview,
                "process_summary": self.process_summary,
                "process_flow": [s.to_dict() for s in self.process_flow],
                "system_profiles": [p.to_dict() for p in self.system_profiles],
                "format_taxonomy": [f.to_dict() for f in self.format_taxonomy],
                "process_inventory": [i.to_dict() for i in self.process_inventory],
                "ownership_map": [r.to_dict() for r in self.ownership_map],
                "system_inventory": [i.to_dict() for i in self.system_inventory],
                "handoff_catalogue": [h.to_dict() for h in self.handoff_catalogue],
                "baseline_stats": [k.to_dict() for k in self.baseline_stats],
                "data_tables": [t.to_dict() for t in self.data_tables],
                "process_detail": [p.to_dict() for p in self.process_detail]}


@dataclass
class PainPoint:                          # Report 02
    id: str
    title: str
    impact_rank: int = 1
    from_finding: str = ""                # F1|F2|F3
    description: str = ""
    root_cause: str = ""
    failure_pattern: str = ""
    business_consequence: str = ""        # the "so what" — impact in business terms
    category: str = ""                    # grounded category label (e.g. "Data Governance")
    severity: str = ""                    # "high" | "medium" | "lower"; falls back to impact_rank
    opportunity_signal: str = ""          # OPP id, derived in code
    quantified: list[NumberRef] = field(default_factory=list)
    detail_table: "DataTable | None" = None   # optional per-PP evidence table (grounded)
    sources: list[SourceRef] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        d = asdict(self)
        d["quantified"] = [n.to_dict() for n in self.quantified]
        d["sources"] = [s.to_dict() for s in self.sources]
        d["detail_table"] = self.detail_table.to_dict() if self.detail_table else None
        return d


@dataclass
class EvidenceRow:                        # one row of the Report 02 evidence register (appendix)
    finding: str                          # the PP / finding id this evidence supports
    source: str = ""                      # business-friendly document name(s)
    evidence_type: str = ""               # e.g. "Structured data", "Policy document", "Working notes"
    data_point: str = ""                  # the key figure or quote
    confidence: str = ""                  # "Verified" | "Amber" | "Gap"

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass
class RiskItem:                           # one row of the Report 03 risk register
    risk: str
    likelihood: str = ""                  # "High" | "Medium" | "Low"
    impact: str = ""                      # "High" | "Medium" | "Low"
    mitigation: str = ""
    owner: str = ""                       # a grounded ROLE (never an invented person)

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass
class TraceRow:                           # one row of the Report 03 traceability matrix (appendix)
    pain_point: str = ""
    summary: str = ""
    severity: str = ""
    recommendation: str = ""
    opportunity: str = ""
    expected_outcome: str = ""
    horizon: str = ""

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass
class BusinessImpact:                      # Report 04
    narrative: str = ""
    quantified: list[NumberRef] = field(default_factory=list)
    derivation: str = ""

    def to_dict(self) -> dict[str, Any]:
        return {"narrative": self.narrative,
                "quantified": [n.to_dict() for n in self.quantified],
                "derivation": self.derivation}


@dataclass
class Opportunity:                         # Report 04 (centrepiece) + 03 matrix
    id: str
    title: str                             # CLIENT title (no never-say words)
    pattern: OppPattern = OppPattern.HITL
    overview: str = ""
    addresses_pain_point: str = ""         # derived in code
    before_process: list[ProcessStep] = field(default_factory=list)
    after_process: list[ProcessStep] = field(default_factory=list)
    business_impact: "BusinessImpact" = field(default_factory=BusinessImpact)
    implementation_approach: str = ""
    required_integrations: list[str] = field(default_factory=list)
    success_metrics: list[str] = field(default_factory=list)
    dependencies: list[str] = field(default_factory=list)
    prerequisite_for: list[str] = field(default_factory=list)  # derived
    risks: list[str] = field(default_factory=list)
    # consultant-grade depth (mirrors the prior-engagement bar):
    personas: list[str] = field(default_factory=list)          # who this serves
    expected_behaviour: str = ""                               # how the solution should behave
    escalation: str = ""                                       # what happens when it can't resolve
    knowledge_sources: list[str] = field(default_factory=list) # which sources/systems feed it
    document_formats: list[str] = field(default_factory=list)  # the data/doc formats it consumes
    # prioritisation rationale across the three standard dimensions (rating + one-line reason)
    data_readiness: str = ""          # "high|medium|low — reason"
    technical_complexity: str = ""    # "high|medium|low — reason"
    operational_readiness: str = ""   # "high|medium|low — reason"
    value_rating: str = "medium"
    feasibility_rating: str = "medium"
    value_score: int = 3
    feasibility_score: int = 3
    matrix_quadrant: MatrixQuadrant = MatrixQuadrant.CONSIDER
    sources: list[SourceRef] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        return {"id": self.id, "title": self.title, "pattern": self.pattern.value,
                "overview": self.overview, "addresses_pain_point": self.addresses_pain_point,
                "before_process": [s.to_dict() for s in self.before_process],
                "after_process": [s.to_dict() for s in self.after_process],
                "business_impact": self.business_impact.to_dict(),
                "implementation_approach": self.implementation_approach,
                "required_integrations": self.required_integrations,
                "success_metrics": self.success_metrics,
                "dependencies": self.dependencies, "prerequisite_for": self.prerequisite_for,
                "risks": self.risks, "personas": self.personas,
                "expected_behaviour": self.expected_behaviour, "escalation": self.escalation,
                "knowledge_sources": self.knowledge_sources,
                "document_formats": self.document_formats,
                "data_readiness": self.data_readiness,
                "technical_complexity": self.technical_complexity,
                "operational_readiness": self.operational_readiness,
                "value_rating": self.value_rating,
                "feasibility_rating": self.feasibility_rating,
                "value_score": self.value_score, "feasibility_score": self.feasibility_score,
                "matrix_quadrant": self.matrix_quadrant.value,
                "sources": [s.to_dict() for s in self.sources]}


@dataclass
class MetricItem:                          # one row of the success-metrics framework
    name: str
    definition: str = ""
    target: str = ""

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass
class RoadmapItem:                         # Report 05
    title: str
    rationale: str = ""
    opportunity_id: str | None = None
    depends_on: list[str] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass
class RoadmapHorizon:
    horizon: str                           # H1|H2|H3
    window: str = ""
    theme: str = ""
    items: list[RoadmapItem] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        d = asdict(self)
        d["items"] = [i.to_dict() for i in self.items]
        return d


@dataclass
class SourceDoc:                           # Report 06 — the ONLY place doc names appear in a table
    doc_id: str
    business_name: str
    doc_type: str
    what_we_read: str = ""
    supported_findings: list[str] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass
class ExecutiveSummary:                    # the landing-page framing for the whole suite
    headline: str = ""                     # 1-2 sentence framing of the engagement and what was found
    situation: str = ""                    # short prose: the current-state in a nutshell
    opportunity: str = ""                  # short prose: where the value is
    # "at a glance" KPI tiles are DERIVED in code from grounded numbers (build), not model-set,
    # so they can never carry a fabricated figure.


@dataclass
class SynthesisContent:                    # everything reports 00-06 render
    current_state: CurrentState = field(default_factory=CurrentState)
    pain_points: list[PainPoint] = field(default_factory=list)
    cross_process_patterns: list[dict[str, Any]] = field(default_factory=list)
    opportunities: list[Opportunity] = field(default_factory=list)
    sequencing_rationale: str = ""
    strategic_readiness: str = ""
    dependency_notes: str = ""
    roadmap: list[RoadmapHorizon] = field(default_factory=list)
    strategy_profile: dict[str, Any] = field(default_factory=dict)
    metrics_framework: list[MetricItem] = field(default_factory=list)   # how success is measured
    source_index: list[SourceDoc] = field(default_factory=list)
    executive_summary: ExecutiveSummary = field(default_factory=ExecutiveSummary)  # Report 00
    target_state: str = ""                 # forward-looking "where this should converge" narrative
    # deeper grounded appendices (all optional — omit cleanly when empty)
    evidence_register: list[EvidenceRow] = field(default_factory=list)     # Report 02 appendix
    risk_register: list[RiskItem] = field(default_factory=list)            # Report 03 risk register
    traceability: list[TraceRow] = field(default_factory=list)             # Report 03 appendix
    # code-owned chart series, derived from grounded numbers in build (never model-set). Each entry:
    # {"key","title","unit","segments":[{"label","value"}]}. Renderer draws these as donut/bar.
    charts: list[dict[str, Any]] = field(default_factory=list)
    # deep-live-pipeline (feature 003): the grounded fact-store the fan-out expanded from, the locked
    # strategy profile, and the clearly-labelled planning assumptions. All optional — the fixture and
    # the legacy single-emit path leave them empty and render unchanged.
    fact_store: "FactStore | None" = None
    strategy: "StrategyProfile | None" = None
    planning_assumptions: list[PlanningAssumption] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        return {"current_state": self.current_state.to_dict(),
                "pain_points": [p.to_dict() for p in self.pain_points],
                "cross_process_patterns": self.cross_process_patterns,
                "opportunities": [o.to_dict() for o in self.opportunities],
                "sequencing_rationale": self.sequencing_rationale,
                "strategic_readiness": self.strategic_readiness,
                "dependency_notes": self.dependency_notes,
                "roadmap": [h.to_dict() for h in self.roadmap],
                "strategy_profile": self.strategy_profile,
                "metrics_framework": [m.to_dict() for m in self.metrics_framework],
                "source_index": [s.to_dict() for s in self.source_index],
                "executive_summary": asdict(self.executive_summary),
                "target_state": self.target_state,
                "evidence_register": [e.to_dict() for e in self.evidence_register],
                "risk_register": [r.to_dict() for r in self.risk_register],
                "traceability": [t.to_dict() for t in self.traceability],
                "charts": self.charts,
                "fact_store": self.fact_store.to_dict() if self.fact_store else None,
                "strategy": self.strategy.to_dict() if self.strategy else None,
                "planning_assumptions": [p.to_dict() for p in self.planning_assumptions]}


@dataclass
class DiscoveryResult:
    """The full payload the report is rendered from."""
    domain: str
    domain_label: str
    documents: list[Document] = field(default_factory=list)
    entities: list[Entity] = field(default_factory=list)
    findings: list[Finding] = field(default_factory=list)
    recommendations: list[Recommendation] = field(default_factory=list)
    effort_comparison: dict[str, Any] = field(default_factory=dict)
    process_summary: str = ""
    synthesis: SynthesisContent | None = None
    # the raw emit_findings payload, kept for the internal audit trace (never client-facing)
    raw_payload: dict | None = None

    def to_dict(self) -> dict[str, Any]:
        return {
            "domain": self.domain,
            "domain_label": self.domain_label,
            "documents": [d.to_dict() for d in self.documents],
            "entities": [e.to_dict() for e in self.entities],
            "findings": [f.to_dict() for f in self.findings],
            "recommendations": [r.to_dict() for r in self.recommendations],
            "effort_comparison": self.effort_comparison,
            "process_summary": self.process_summary,
            **({"synthesis": self.synthesis.to_dict()} if self.synthesis else {}),
        }
