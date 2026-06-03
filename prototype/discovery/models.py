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

    def to_dict(self) -> dict[str, Any]:
        return {"domain_overview": self.domain_overview,
                "process_summary": self.process_summary,
                "process_flow": [s.to_dict() for s in self.process_flow],
                "system_profiles": [p.to_dict() for p in self.system_profiles],
                "format_taxonomy": [f.to_dict() for f in self.format_taxonomy],
                "process_inventory": [i.to_dict() for i in self.process_inventory],
                "ownership_map": [r.to_dict() for r in self.ownership_map],
                "system_inventory": [i.to_dict() for i in self.system_inventory],
                "handoff_catalogue": [h.to_dict() for h in self.handoff_catalogue]}


@dataclass
class PainPoint:                          # Report 02
    id: str
    title: str
    impact_rank: int = 1
    from_finding: str = ""                # F1|F2|F3
    description: str = ""
    root_cause: str = ""
    failure_pattern: str = ""
    opportunity_signal: str = ""          # OPP id, derived in code
    quantified: list[NumberRef] = field(default_factory=list)
    sources: list[SourceRef] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        d = asdict(self)
        d["quantified"] = [n.to_dict() for n in self.quantified]
        d["sources"] = [s.to_dict() for s in self.sources]
        return d


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
                "target_state": self.target_state}


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
