# DESIGN_SPEC_report_suite.md

**Build-ready spec — Order-to-Cash 6-Report Client Suite**
Tech-lead merge of 3 designs + 3 critiques. Conflicts resolved decisively; every valid critique fix folded in. Authoritative for the build.

---

## 0. Decisions that override the source designs (read first)

These resolve direct conflicts between the three designs and the three critiques. Where a design and its critique disagree, the critique wins unless noted.

| # | Decision | Why (which critique) |
|---|---|---|
| **D0** | **The renderer is the bulk of the work, not the schema.** `report.py` is rewritten into a 6-report suite. The synthesis schema is ~20% of the job. | Synthesis-critique B1 |
| **D1** | **Synthesis content for the Friday demo is a hand-curated static fixture** `inputs/o2c/synthesis_o2c.json`, grounded by hand against F1/F2/F3. The live second agent turn (`synthesis.py`) is BUILT and TESTED but is NOT on the demo path. `run.py --live-synth` opts into it; default and `--golden` use the fixture. | Renderer-critique FM-13, Synthesis-critique B14 — removes prompt-tuning long pole, re-golden risk (B13), and fabrication-rejection risk (B5/B6/B7) from the critical path. |
| **D2** | **TSA / "6 of 14 connections" is NOT grounded** (verified: absent from `discovery-o2c.json`; F3 = 1,196 / €12,362,494 / 4,471 only; `edi-integration-register` is never a finding source). **Resolution: Option B.** Drop every *quantified* TSA claim. Opp3 sequencing rests ONLY on the F1 clean-customer-master dependency. The TSA *transfer* appears in Roadmap H1 as a **qualitative initiative with no number** (allowed for roadmap items), phrased "transition the EDI connections still operated under the transitional service arrangement" — no count. A `--reground-tsa` path (re-run discovery to emit the 14/6 split from the EDI register into F3.computed_values) is documented as post-Friday. | Renderer-critique FM-1 (CRITICAL), confirmed by inspection. |
| **D3** | **The legacy findings section is REMOVED from the stakeholder report.** Findings-with-provenance surface only through Report 02 (pain points). The raw findings live only in the internal JSON. | Synthesis-critique B3 (option b) |
| **D4** | **`run.py` writes TWO things:** (a) the scrubbed stakeholder suite to `out/o2c/*.html|md`; (b) `out/discovery-o2c.json` containing **both** `result.to_dict()` AND a new top-level `"internal_trace"` key holding the **raw `emit_findings` payload** (with `computed_values`, `from_tool`, `narrative_values`, `sources[].locator`). | Synthesis-critique B4 + Scrub-critique FM-1 — without this the scrub **deletes** the only copy of `from_tool` (it survives today only inside the `(computed by …)` leak). Load-bearing. |
| **D5** | **The demo opens `out/o2c/index.html`**, never `out/report-o2c.html`. `run.py` prints this path. The old combined report is retired (kept on disk only as internal reference, not shown). | Renderer-critique FM-11, Scrub FM-8 |
| **D6** | **Client-facing opportunity titles avoid never-say words.** Opp2 client title = **"EDI Order Exception Handling"** (NOT "Pipeline"). Opp3 client title = **"AI Credit Decisioning"** (the word "Agent" appears only in the *pattern label* "AI Agent", which the demo guide explicitly permits as a named solution pattern). Internal ids/patterns unchanged. | Synthesis-critique B17 |
| **D7** | **Numbers are grounded structurally, not by scanning prose.** Every client-facing number is rendered through a `Metric` object whose `value` is checked against the allow-list; prose may contain digits but only ones already on the allow-list (string-token check). The allow-list includes computed values, narrative-quote numbers, AND legitimate derived ratios (n/m·100 for allow-list pairs). | Synthesis-critique B5/B6/B7, Renderer FM-2 — the bare-digit ban (original §4) is **rejected** as self-contradictory. |
| **D8** | **Two LLM-output trees are kept separate.** The synthesis tool emits doc **keys** (enum); the renderer maps key → friendly name. No field in the synthesis schema can hold a tool name, filename, column, or locator. | All three designs agree. |
| **D9** | **Report 01 factual-only is enforced by a validator**, not just the prompt: `assert_factual()` bans a diagnostic wordlist over all `current_state.*` strings, and the Report 01 renderer has no access to `severity`/`confidence`/badges. | Synthesis-critique B9, Renderer FM-10, Scrub FM-4 |

---

## 1. Extended `models.py` dataclasses

Add below the existing dataclasses. Reuses existing `SourceRef`, `Enum`, `asdict`, `field`. **`SourceRef` is never rendered raw** — always through `cite()` / `provenance` (§4).

```python
from enum import Enum
from dataclasses import dataclass, field, asdict
from typing import Any

# ---- enums ----
class OppPattern(str, Enum):
    HITL = "hitl_workflow"
    AUTOMATION = "automation"
    AI_AGENT = "ai_agent"

class MatrixQuadrant(str, Enum):
    DO_FIRST = "do_first"; PLAN_FOR = "plan_for"
    CONSIDER = "consider"; DEPRIORITISE = "deprioritise"

# ---- the only carrier of a number on the client side ----
@dataclass
class NumberRef:
    """One quantitative claim. `value` MUST trace to the findings' allow-list (§3).
    `text` is the readable form; the renderer formats via fmt_value() for headlines."""
    value: float
    unit: str          # count|eur|percent|ratio|accounts|orders|escalations
    label: str = ""    # e.g. "Carrefour France credit-limit gap"
    text: str = ""     # e.g. "5,667 of 8,420 orders (67%)"
    sources: list["SourceRef"] = field(default_factory=list)
    def to_dict(self) -> dict[str, Any]:
        d = asdict(self); d["sources"] = [s.to_dict() for s in self.sources]; return d

@dataclass
class ProcessStep:
    seq: int
    name: str
    actor: str = ""
    system: str = ""          # business system NAME (e.g. "SAP S/4HANA") — allowed; NOT a csv id
    description: str = ""
    failure_points: list[str] = field(default_factory=list)  # empty for AFTER + Report 01
    metrics: list[NumberRef] = field(default_factory=list)
    sources: list["SourceRef"] = field(default_factory=list)
    def to_dict(self) -> dict[str, Any]:
        d = asdict(self)
        d["metrics"] = [m.to_dict() for m in self.metrics]
        d["sources"] = [s.to_dict() for s in self.sources]; return d

@dataclass
class RaciRow:
    activity: str; responsible: str = ""; accountable: str = ""
    consulted: str = ""; informed: str = ""
    sources: list["SourceRef"] = field(default_factory=list)
    def to_dict(self) -> dict[str, Any]:
        d = asdict(self); d["sources"] = [s.to_dict() for s in self.sources]; return d

@dataclass
class InventoryItem:                      # process_inventory + system_inventory
    name: str; purpose: str = ""          # process: purpose ; system: role
    system_of_record_for: str = ""
    sources: list["SourceRef"] = field(default_factory=list)
    def to_dict(self) -> dict[str, Any]:
        d = asdict(self); d["sources"] = [s.to_dict() for s in self.sources]; return d

@dataclass
class Handoff:
    from_step: str; to_step: str; mechanism: str = ""
    sources: list["SourceRef"] = field(default_factory=list)
    def to_dict(self) -> dict[str, Any]:
        d = asdict(self); d["sources"] = [s.to_dict() for s in self.sources]; return d

@dataclass
class CurrentState:                       # Report 01 — NO severity/confidence field exists here
    domain_overview: str = ""
    process_summary: str = ""
    process_flow: list[ProcessStep] = field(default_factory=list)
    process_inventory: list[InventoryItem] = field(default_factory=list)
    ownership_map: list[RaciRow] = field(default_factory=list)
    system_inventory: list[InventoryItem] = field(default_factory=list)
    handoff_catalogue: list[Handoff] = field(default_factory=list)
    def to_dict(self) -> dict[str, Any]:
        return {"domain_overview": self.domain_overview,
                "process_summary": self.process_summary,
                "process_flow": [s.to_dict() for s in self.process_flow],
                "process_inventory": [i.to_dict() for i in self.process_inventory],
                "ownership_map": [r.to_dict() for r in self.ownership_map],
                "system_inventory": [i.to_dict() for i in self.system_inventory],
                "handoff_catalogue": [h.to_dict() for h in self.handoff_catalogue]}

@dataclass
class PainPoint:                          # Report 02
    id: str                               # PP1..PP3
    title: str
    impact_rank: int
    from_finding: str                     # F1|F2|F3
    description: str = ""
    root_cause: str = ""
    failure_pattern: str = ""
    opportunity_signal: str = ""          # OPP1|OPP2|OPP3 (derived in code, see §3 B10)
    quantified: list[NumberRef] = field(default_factory=list)
    sources: list["SourceRef"] = field(default_factory=list)
    def to_dict(self) -> dict[str, Any]:
        d = asdict(self)
        d["quantified"] = [n.to_dict() for n in self.quantified]
        d["sources"] = [s.to_dict() for s in self.sources]; return d

@dataclass
class BusinessImpact:                      # Report 04
    narrative: str = ""
    quantified: list[NumberRef] = field(default_factory=list)
    derivation: str = ""                   # words chaining ONLY allow-list numbers
    def to_dict(self) -> dict[str, Any]:
        return {"narrative": self.narrative,
                "quantified": [n.to_dict() for n in self.quantified],
                "derivation": self.derivation}

@dataclass
class Opportunity:                         # Report 04 (centrepiece) + 03 matrix
    id: str                                # OPP1..OPP3
    title: str                             # CLIENT title (D6: no never-say words)
    pattern: OppPattern
    overview: str = ""
    addresses_pain_point: str = ""         # PP1..PP3 (derived in code from fixed map, §3)
    before_process: list[ProcessStep] = field(default_factory=list)
    after_process: list[ProcessStep] = field(default_factory=list)
    business_impact: BusinessImpact = field(default_factory=BusinessImpact)
    implementation_approach: str = ""
    required_integrations: list[str] = field(default_factory=list)  # system NAMES
    success_metrics: list[str] = field(default_factory=list)
    dependencies: list[str] = field(default_factory=list)            # OPP ids
    prerequisite_for: list[str] = field(default_factory=list)        # reverse link (FM-12); derived
    risks: list[str] = field(default_factory=list)
    value_rating: str = "medium"           # high|medium|low
    feasibility_rating: str = "medium"
    value_score: int = 3                   # 1..5 for the 2x2 plot
    feasibility_score: int = 3
    matrix_quadrant: MatrixQuadrant = MatrixQuadrant.CONSIDER
    sources: list["SourceRef"] = field(default_factory=list)
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
                "risks": self.risks, "value_rating": self.value_rating,
                "feasibility_rating": self.feasibility_rating,
                "value_score": self.value_score, "feasibility_score": self.feasibility_score,
                "matrix_quadrant": self.matrix_quadrant.value,
                "sources": [s.to_dict() for s in self.sources]}

@dataclass
class RoadmapItem:                         # Report 05
    title: str; rationale: str = ""
    opportunity_id: str | None = None      # OPP1..3 or None for non-opp items (D2 TSA, middleware…)
    depends_on: list[str] = field(default_factory=list)
    def to_dict(self) -> dict[str, Any]: return asdict(self)

@dataclass
class RoadmapHorizon:
    horizon: str                           # H1|H2|H3
    window: str                            # "0-6 months"...
    theme: str = ""
    items: list[RoadmapItem] = field(default_factory=list)
    def to_dict(self) -> dict[str, Any]:
        d = asdict(self); d["items"] = [i.to_dict() for i in self.items]; return d

@dataclass
class SourceDoc:                           # Report 06 — the ONE place doc_ids may appear on screen
    doc_id: str
    business_name: str
    doc_type: str
    what_we_read: str = ""                 # hand/curated business paraphrase — NEVER the raw quote
    supported_findings: list[str] = field(default_factory=list)
    def to_dict(self) -> dict[str, Any]: return asdict(self)

@dataclass
class SynthesisContent:                    # everything reports 01-05 render
    current_state: CurrentState = field(default_factory=CurrentState)
    pain_points: list[PainPoint] = field(default_factory=list)
    cross_process_patterns: list[dict[str, Any]] = field(default_factory=list)  # FM-8 renamed
    opportunities: list[Opportunity] = field(default_factory=list)
    sequencing_rationale: str = ""
    strategic_readiness: str = ""
    dependency_notes: str = ""
    roadmap: list[RoadmapHorizon] = field(default_factory=list)
    strategy_profile: dict[str, Any] = field(default_factory=dict)
    source_index: list[SourceDoc] = field(default_factory=list)   # built deterministically (§6 B8)
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
                "source_index": [s.to_dict() for s in self.source_index]}
```

**Extend `DiscoveryResult`** (backward compatible — old combined renderer still works):

```python
@dataclass
class DiscoveryResult:
    ...                                    # existing fields unchanged
    process_summary: str = ""
    synthesis: SynthesisContent | None = None     # NEW
    raw_payload: dict | None = None               # NEW — the emit_findings payload (D4)
    def to_dict(self) -> dict[str, Any]:
        d = { ...existing... }
        if self.synthesis is not None:
            d["synthesis"] = self.synthesis.to_dict()
        return d                            # NOTE: raw_payload is NOT inside to_dict; run.py writes
                                            # it separately under "internal_trace" (D4)
```

---

## 2. Synthesis turn — JSON schema + prompts + grounding validator

Lives in **new `discovery/synthesis.py`**. Reuses `agent_loop._close`, `GroundingError`, `messages_with_tools` (NOT `complete_json` — see B15: we need schema enforcement + the established re-prompt loop). **The demo path does not call this** (D1); it is built, tested, and `--live-synth`-gated.

### 2a. The emit tool (`emit_synthesis`)

`doc_keys = sorted(registry.DOC_META)` at runtime (D8). `opportunity_id` is **optional, plain string enum** — no `null` in the enum (B12). Reusable `SOURCE`/`NUMBER_REF`/`PROCESS_STEP` sub-schemas as in the original §1, with these binding corrections:

```python
def synthesis_emit_tool(doc_keys: list[str]) -> dict:
    DOC_ENUM = {"type": "string", "enum": sorted(doc_keys)}
    NUMBER_REF = {"type": "object", "additionalProperties": False,
        "properties": {"value": {"type": "number"},
                       "unit": {"type": "string",
                                "enum": ["count","eur","percent","ratio","accounts",
                                         "orders","escalations"]},
                       "label": {"type": "string"},
                       "text": {"type": "string"}},   # "5,667 of 8,420 orders (67%)"
        "required": ["value","unit","text"]}
    SOURCE = {"type": "object", "additionalProperties": False,
        "properties": {"doc_key": DOC_ENUM,
                       "as_business_phrase": {"type": "string"}},
        "required": ["doc_key"]}
    PROCESS_STEP = {"type": "object", "additionalProperties": False,
        "properties": {"seq": {"type":"integer","minimum":1}, "name":{"type":"string"},
                       "actor":{"type":"string"}, "system":{"type":"string"},
                       "description":{"type":"string"},
                       "failure_points":{"type":"array","items":{"type":"string"}},
                       "metrics":{"type":"array","items":NUMBER_REF},
                       "sources":{"type":"array","items":SOURCE}},
        "required": ["seq","name","actor","description"]}
    OPPORTUNITY = {"type":"object","additionalProperties":False,"properties":{
        "id":{"type":"string","enum":["OPP1","OPP2","OPP3"]},
        "title":{"type":"string"}, "pattern":{"type":"string",
            "enum":["hitl_workflow","automation","ai_agent"]},
        "overview":{"type":"string"},
        "before_process":{"type":"array","minItems":2,"items":PROCESS_STEP},
        "after_process":{"type":"array","minItems":2,"items":PROCESS_STEP},
        "business_impact":{"type":"object","additionalProperties":False,"properties":{
            "narrative":{"type":"string"},
            "quantified":{"type":"array","items":NUMBER_REF},
            "derivation":{"type":"string"}}, "required":["narrative","quantified"]},
        "implementation_approach":{"type":"string"},
        "required_integrations":{"type":"array","items":{"type":"string"}},
        "success_metrics":{"type":"array","items":{"type":"string"}},
        "dependencies":{"type":"array","items":{"type":"string","enum":["OPP1","OPP2","OPP3"]}},
        "risks":{"type":"array","items":{"type":"string"}},
        "value_rating":{"type":"string","enum":["high","medium","low"]},
        "feasibility_rating":{"type":"string","enum":["high","medium","low"]},
        "value_score":{"type":"integer","minimum":1,"maximum":5},
        "feasibility_score":{"type":"integer","minimum":1,"maximum":5},
        "matrix_quadrant":{"type":"string",
            "enum":["do_first","plan_for","consider","deprioritise"]},
        "sources":{"type":"array","minItems":1,"items":SOURCE}},
      # NOTE: addresses_pain_point is NOT model-set — derived in code (B10).
      "required":["id","title","pattern","overview","before_process","after_process",
                  "business_impact","implementation_approach","value_rating",
                  "feasibility_rating","value_score","feasibility_score",
                  "matrix_quadrant","dependencies","sources"]}
    PAIN_POINT = {"type":"object","additionalProperties":False,"properties":{
        "id":{"type":"string","enum":["PP1","PP2","PP3"]}, "title":{"type":"string"},
        "impact_rank":{"type":"integer","minimum":1,"maximum":3},
        "from_finding":{"type":"string","enum":["F1","F2","F3"]},
        "description":{"type":"string"}, "root_cause":{"type":"string"},
        "failure_pattern":{"type":"string"},
        "quantified":{"type":"array","items":NUMBER_REF},
        "sources":{"type":"array","minItems":2,"items":SOURCE}},
      # opportunity_signal derived in code (B10).
      "required":["id","title","impact_rank","from_finding","description",
                  "root_cause","failure_pattern","sources"]}
    ROADMAP_ITEM = {"type":"object","additionalProperties":False,"properties":{
        "title":{"type":"string"}, "rationale":{"type":"string"},
        "opportunity_id":{"type":"string","enum":["OPP1","OPP2","OPP3"]},  # OPTIONAL (B12)
        "depends_on":{"type":"array","items":{"type":"string"}}},
      "required":["title","rationale"]}                                     # opportunity_id absent = non-opp
    return {"name":"emit_synthesis",
      "description":("Call EXACTLY ONCE. Client-facing content for reports 01-05 for a "
        "non-technical Head of Strategy. BUSINESS LANGUAGE ONLY. Every number lives in a "
        "NumberRef.value matching a verified finding number. Cite source DOCUMENTS by key; "
        "never write a filename, column, or tool/operation name anywhere."),
      "input_schema":{"type":"object","additionalProperties":False,"properties":{
        "current_state":{"type":"object","additionalProperties":False,"properties":{
            "domain_overview":{"type":"string"}, "process_summary":{"type":"string"},
            "process_flow":{"type":"array","minItems":3,"items":PROCESS_STEP},
            "process_inventory":{"type":"array","items":{"type":"object",
                "additionalProperties":False,"properties":{"name":{"type":"string"},
                "purpose":{"type":"string"},"sources":{"type":"array","items":SOURCE}},
                "required":["name","purpose"]}},
            "ownership_map":{"type":"array","items":{"type":"object",
                "additionalProperties":False,"properties":{"activity":{"type":"string"},
                "responsible":{"type":"string"},"accountable":{"type":"string"},
                "consulted":{"type":"string"},"informed":{"type":"string"},
                "sources":{"type":"array","items":SOURCE}},
                "required":["activity","responsible","accountable"]}},
            "system_inventory":{"type":"array","items":{"type":"object",
                "additionalProperties":False,"properties":{"name":{"type":"string"},
                "role":{"type":"string"},"system_of_record_for":{"type":"string"},
                "sources":{"type":"array","items":SOURCE}}, "required":["name","role"]}},
            "handoff_catalogue":{"type":"array","items":{"type":"object",
                "additionalProperties":False,"properties":{"from_step":{"type":"string"},
                "to_step":{"type":"string"},"mechanism":{"type":"string"},
                "sources":{"type":"array","items":SOURCE}},
                "required":["from_step","to_step","mechanism"]}}},
          "required":["domain_overview","process_summary","process_flow","process_inventory",
                      "ownership_map","system_inventory","handoff_catalogue"]},
        "pain_points":{"type":"array","minItems":3,"maxItems":3,"items":PAIN_POINT},
        "cross_process_patterns":{"type":"array","items":{"type":"object",
            "additionalProperties":False,"properties":{"pattern":{"type":"string"},
            "spans_pain_points":{"type":"array","items":{"type":"string","enum":["PP1","PP2","PP3"]}},
            "description":{"type":"string"}}, "required":["pattern","description"]}},
        "opportunities":{"type":"array","minItems":3,"maxItems":3,"items":OPPORTUNITY},
        "transformation":{"type":"object","additionalProperties":False,"properties":{
            "sequencing_rationale":{"type":"string"}, "strategic_readiness":{"type":"string"},
            "dependency_notes":{"type":"string"}},
          "required":["sequencing_rationale","strategic_readiness"]},
        "roadmap":{"type":"array","minItems":3,"maxItems":3,"items":{"type":"object",
            "additionalProperties":False,"properties":{
            "horizon":{"type":"string","enum":["H1","H2","H3"]},
            "window":{"type":"string","enum":["0-6 months","6-18 months","18+ months"]},
            "theme":{"type":"string"},
            "items":{"type":"array","minItems":1,"items":ROADMAP_ITEM}},
          "required":["horizon","window","theme","items"]}},
        "strategy_profile":{"type":"object","additionalProperties":False,"properties":{
            "posture":{"type":"string","enum":["consolidate_modernize"]},
            "notes":{"type":"string"}}, "required":["posture"]}},
        "required":["current_state","pain_points","opportunities","transformation",
                    "roadmap","strategy_profile"]}}
```

### 2b. The grounding validator (`synthesis.validate_synthesis`)

Resolves B5/B6/B7/FM-2 (allow-list completeness + structural number check, NOT prose-digit ban), B9/FM-10 (Report 01 factual lint), B10 (PP↔OPP inverse), B11 (full dependency invariant), FM-8 (cross-process not cross-domain), B16 (unknown doc key = hard fail).

```python
import re
from .agent_loop import GroundingError, _close

# Structural numbers that are NEVER findings-derived and must be whitelisted out (FM-2):
_STRUCTURAL = {0,1,2,3,4,5,6,18}          # report indices, horizon months, 2x2, scores 1-5, 3 opps
_DIAGNOSTIC = re.compile(
    r"\b(breach|violation|uncontrolled|critical|severe|urgent|red flag|amber|"
    r"broken|failure risk|conflict|gap|problem|risk)\b", re.I)   # Report 01 only

def allowed_numbers(raw_payload: dict) -> set[float]:
    """B5/B7: computed_values + numeric narrative_values + numbers parsed out of the
    findings' OWN verified quotes (sources[].quote, narrative_values[].quote) + legitimate
    derived ratios n/m*100 for allow-list pairs. Stores BOTH eur scales (12.36 and 12,360,000)."""
    nums: set[float] = set()
    def add(v):
        try: f = float(v)
        except (TypeError, ValueError): return
        nums.add(round(f, 4))
        if 0 < f < 1000: nums.add(round(f * 1_000_000, 4))   # 12.36 -> 12,360,000 (FM-3/B7)
        if f >= 1_000_000: nums.add(round(f / 1_000_000, 4)) # and the reverse
    for f in raw_payload["findings"]:
        for cv in f.get("computed_values", []): add(cv.get("value"))
        for nv in f.get("narrative_values", []):
            add(nv.get("value"))
            for tok in re.findall(r"\d[\d,]*\.?\d*", nv.get("quote","")): add(tok.replace(",",""))
        for s in f.get("sources", []):
            for tok in re.findall(r"\d[\d,]*\.?\d*", s.get("quote","")): add(tok.replace(",",""))
    # legitimate ratios: 267/318*100, 5667/8420*100, 1196/(1196+4471)*100 ...
    base = sorted(n for n in nums if n >= 1)
    for a in base:
        for b in base:
            if b and a < b: add(round(a / b * 100, 1))
    return nums

def _check_number(value, allow: set[float]):
    if round(float(value), 4) in _STRUCTURAL: return
    if not _close(value, allow):
        raise GroundingError(f"synthesis number {value} not traceable to verified findings")

def assert_factual(text: str):
    if _DIAGNOSTIC.search(text or ""):
        raise GroundingError(f"Report-01 (current_state) prose contains diagnostic language: "
                             f"{_DIAGNOSTIC.findall(text)[:3]}")

def validate_synthesis(payload: dict, allow: set[float], doc_keys: set[str]) -> dict:
    # (1) every NumberRef.value traces; (2) every doc_key is real (B16);
    # (3) prose digit tokens must be on the allow-list (D7 — NOT a blanket ban)
    def prose_ok(s: str):
        for tok in re.findall(r"\d[\d,]*\.?\d*", s or ""):
            v = float(tok.replace(",",""))
            if round(v,4) in _STRUCTURAL: continue
            if not _close(v, allow):
                raise GroundingError(f"prose has untraceable number {tok!r}")
    def walk(o):
        if isinstance(o, dict):
            if {"value","unit","text"} <= set(o): _check_number(o["value"], allow)
            if "doc_key" in o and o["doc_key"] not in doc_keys:
                raise GroundingError(f"unknown doc_key {o['doc_key']!r}")
            for v in o.values(): walk(v)
        elif isinstance(o, list):
            for x in o: walk(x)
        elif isinstance(o, str):
            prose_ok(o)
    walk(payload)
    # (4) Report 01 factual lint (B9/FM-10) over current_state strings only
    def lint01(o):
        if isinstance(o, dict):
            for k,v in o.items():
                if isinstance(v,str): assert_factual(v)
                else: lint01(v)
        elif isinstance(o, list):
            for x in o: lint01(x)
    lint01(payload["current_state"])
    # (5) dependency invariant — FULL (B11)
    deps = {o["id"]: set(o.get("dependencies",[])) for o in payload["opportunities"]}
    if deps.get("OPP1"): raise GroundingError("OPP1 must have no dependencies")
    if deps.get("OPP2") & {"OPP1","OPP3"}: raise GroundingError("OPP2 must be independent")
    if deps.get("OPP3") != {"OPP1"}: raise GroundingError("OPP3 must depend on exactly OPP1")
    # (6) roadmap sequencing must not contradict deps (B11)
    h1 = {it.get("opportunity_id") for h in payload["roadmap"] if h["horizon"]=="H1" for it in h["items"]}
    h2 = {it.get("opportunity_id") for h in payload["roadmap"] if h["horizon"]=="H2" for it in h["items"]}
    if not ({"OPP1","OPP2"} <= h1): raise GroundingError("H1 must contain OPP1 and OPP2")
    if "OPP3" not in h2: raise GroundingError("OPP3 must be in H2")
    return payload
```

**B10 PP↔OPP map is fixed in code, not model-set:** `PP_TO_OPP = {"PP1":"OPP1","PP2":"OPP3","PP3":"OPP2"}` (from the brief's crossover); `OPP_TO_PP` is its inverse. `assemble.to_synthesis` sets `PainPoint.opportunity_signal` and `Opportunity.addresses_pain_point`/`prerequisite_for` from these constants — the model never sets either direction.

### 2c. System prompt (synthesis turn)

```
You are a transformation strategist writing a briefing for a non-technical Head of Strategy at a
consumer-healthcare company recently carved out from a parent group. You are turning three
already-verified findings into client-facing content for an Order-to-Cash assessment.

ABSOLUTE RULES (checked automatically — violations are rejected):
1. BUSINESS LANGUAGE ONLY. NEVER use: pipeline, agent (except the named pattern "AI Agent"),
   block, knowledge graph, evidence synthesis, gap detected/resolved, node, edge, join, diff,
   group_by, aggregate, filter, query, tool, CSV, column, row, locator. Never write a filename.
   Refer to inputs as business documents ("your ERP and CRM customer exports", "your order-flow
   records", "the credit policy"). Cite a source by choosing its key in `sources`; the report
   prints the proper business name. Never type a key or filename into prose.
2. NO NEW NUMBERS. Every figure goes in a NumberRef.value and must equal one of the VERIFIED
   NUMBERS you are given (format readably in `text`). Never invent, estimate, sum, average, or
   round a new number. Do NOT state ROI, FTE, hours-saved, or time-to-resolve figures — they have
   no source; keep those impacts qualitative.
3. FACTUAL CURRENT STATE (report 01). Describe how the process runs. State facts only — NO
   evaluative words (breach, risk, violation, gap, conflict, uncontrolled, critical, broken,
   failure). "EDI carries 5,667 of 8,420 orders" — not "EDI is an uncontrolled blind spot."
   Where a step has no documented owner, write "Not assigned". Judgement belongs in pain points
   and opportunities, never report 01.
4. Every pain point and opportunity cites the source documents its evidence rests on (by key).
5. Output ONLY by calling emit_synthesis exactly once.
You are not discovering anything new. Explain the settled findings and chart what to do.
```

### 2d. User prompt (synthesis turn)

Interpolates `friendly_doc_index` (key → friendly name list), `verified_numbers_json` (flat `{value,unit,label,finding}` list), and `findings_business_json` (id/title/description/business_consequence with tool names stripped, `sources` as doc_keys). Contains the verbatim F1/F2/F3 business restatements, the **WHAT TO WRITE** block (current state / 3 pain points / 3 opportunities with before+after / transformation / roadmap), the **PAIN→OPP map** `PP1(F1)→OPP1, PP2(F2)→OPP3, PP3(F3)→OPP2`, the **opportunity briefs** (OPP1 hitl reconciliation, prerequisite for OPP3; OPP2 automation, independent; OPP3 ai_agent, depends on OPP1), and the **roadmap shape**: H1 = OPP1 + OPP2 + EDI-connection transition (qualitative, no count per D2); H2 = OPP3 + EDI middleware assessment; H3 = app rationalisation (CRM consolidation, EDI modernisation, ERP credit module); `strategy_profile.posture = "consolidate_modernize"`. (Full text in original SYNTHESIS-SCHEMA §6, amended for D2/D6.)

### 2e. Loop + fallback

`messages_with_tools` with `tool_choice` forcing `emit_synthesis`; emit-once; on `GroundingError`, re-prompt once with the error appended (mirrors `run_discovery`); on second failure, **fall back to the static fixture** `synthesis_o2c.json` (B14). The fixture is also the default demo path (D1).

---

## 3. Grounding-validator summary (the "numbers must trace" guarantee)

1. **Allow-list source** = `raw_payload` findings: `computed_values` ∪ numeric `narrative_values` ∪ digits parsed from verified `*.quote` strings ∪ legitimate `n/m·100` ratios ∪ dual EUR scaling (`12.36` ↔ `12,360,000`). (B5/B7/FM-3)
2. **Every `NumberRef.value`** must `_close()`-match the allow-list (existing tol=0.5), except structural numbers `{0,1,2,3,4,5,6,18}`. (FM-2)
3. **Prose digits** are permitted but each token must also be on the allow-list (string-token check) — the blanket bare-digit ban is **rejected** (B6). (D7)
4. **Report 01** strings additionally pass `assert_factual()` (no diagnostic words). (B9/FM-10)
5. **Dependency invariant** fully enforced: OPP1 none, OPP2 independent, OPP3 == {OPP1}; H1⊇{OPP1,OPP2}, OPP3∈H2. (B11)
6. **PP↔OPP** is code-fixed, never model-set. (B10)
7. **Unknown doc_key** = hard fail (no silent filename echo). (B16)

---

## 4. The leak fix — friendly-name map + business-language layer (the chokepoint)

### 4a. `discovery/docnames.py` (single source of truth, keyed on extensionless stem)

The agent emits **extensionless** ids (`sap-s4-customer-master-export`); loader uses full filenames. `_stem()` strips ONLY known extensions (`.csv/.pdf/.txt/.json/.md`) — not any dot (FM-6). `friendly()` **hard-fails on unknown id during the O2C demo path** (FM-6/FM-10/Scrub-FM-10); a soft `.title()` fallback exists only for non-demo robustness and is asserted-against in the run. **All 12 docs present** (FM-6 — including AR notes + onboarding guide). Map content = the SCRUB Deliverable-1 table (`friendly`, `business_phrase`, `system`, `kind`). `business_phrase_list()` joins with the ERP+CRM collapse to "your ERP and CRM customer exports".

### 4b. The single citation chokepoint (`assemble.py`)

```python
from . import docnames
def cite(refs: list[SourceRef]) -> str:
    """Business citation. friendly_name only — never doc_id, locator, or tool. The leak fix."""
    return docnames.business_phrase_list([r.doc_id for r in refs]) or ""
```

### 4c. Complete jargon → business-language replacement table (every leak)

| # | File:line (current) | Exact leaking string | Replacement |
|---|---|---|---|
| **L1** | `assemble.py:32` | `... (computed by {cv['from_tool']})` | **Drop the `(computed by …)` suffix entirely.** Raw value+`from_tool` go to `internal_trace` JSON only (D4). |
| **L2** | `assemble.py:35` | `(“{quote}” — {nv['doc_id']})` | Keep quote; replace `— {doc_id}` with `— {docnames.friendly(doc_id)}`. |
| **L3** | `report.py:113` | `` `{s.doc_id}` + " ({s.locator})" `` | **`cite(f.sources)`** — friendly phrase, no locator, no backticks. (B2 — the #1 on-screen leak) |
| **L4** | `report.py:89` | `_Based on:_ {', '.join(s.doc_id ...)}` | `cite(rec.sources)` |
| **L5** | `report.py:37` | `\| {d.doc_id} \| {d.category.value} \| {d.summary} \|` | `\| {docnames.friendly(d.doc_id)} \| {docnames._meta(d.doc_id)['kind']} \| {d.summary} \|` — fixes the Inputs-table `.csv/.pdf` leak (Scrub-FM-3, MISSED by other designs). |
| **L6** | `report.py:47` | `## 2. Findings — contradictions & gaps` | Section **removed** in suite (D3). Report 02 heading: **"Pain Points & Opportunities"**. |
| **L7** | `report.py:60` | `**Evidence:**` | **"Where this comes from:"** |
| **L8** | `report.py:52-53` | `_SEV_BADGE` 🔴/🟡 + `_CONF_BADGE` 🔴 Gap | **No badges in Report 01** (renderer has no severity access). In 02/04, impact = "High/Medium" text, never red/amber emoji; confidence relabel: gap→"needs confirmation", amber→"single-source", verified→"confirmed across your documents". |
| **L9** | `report.py:27` | "Generated by the AuroPro automated discovery **prototype** on **synthetic data**." | "Produced by the AuroPro discovery platform from your operational documents." (drops BOTH "prototype" and "synthetic data" — Scrub-FM-8) |
| **L10** | `report.py:25` | `# Discovery Report` | "Order-to-Cash Discovery — Current State & Opportunity Assessment" |
| — | (internal) `models.py:42` `SourceRef.locator`; `computed_values[].from_tool` | **Keep** — feeds `internal_trace`. Never rendered. |

### 4d. Belt-and-braces guard `assert_no_leaks(md)` (run before writing .md/.html ONLY)

Corrects FM-7/FM-4 (whole-word tool tokens only; do NOT ban ordinary English `describe`/`column`/`aggregate`/`node`/`edge`; catch the `.csv/.pdf` leak):

```python
import re
_TOOL_TOKENS = (r"join_diff", r"group_by", r"filter_count", r"find_mentions",
                r"n_mismatch", r"sum_delta", r"key=", r"locator", r"from_tool")
_PARENS = re.compile(r"\((?:computed by|describe|aggregate)[^)]*\)", re.I)  # tool senses only
_FILES  = re.compile(r"\.(csv|pdf|txt|json)\b", re.I)                       # Scrub-FM-3
_PHRASES = re.compile(r"\b(knowledge graph|evidence synthesis|gap detected|gap resolved|"
                      r"nodes and edges)\b", re.I)                          # phrase-anchored (FM-7)
def assert_no_leaks(md: str) -> None:
    bad = _PARENS.findall(md) + _FILES.findall(md) + _PHRASES.findall(md)
    for t in _TOOL_TOKENS:
        if re.search(rf"(?<![A-Za-z]){t}", md): bad.append(t)
    if bad:
        raise AssertionError(f"stakeholder report leaked internal terms: {sorted(set(bad))}")
```

Run `assert_no_leaks` per report before write; **never** before the JSON write. Test it against the *real* current `report-o2c.md` once before wiring (Scrub-FM-7) to confirm zero false positives on legit content.

### 4e. Per-finding business provenance phrasing (rendered by `cite`)

- **F1:** "from your ERP and CRM customer exports (SAP S/4HANA and SAP CRM), read against your Credit Management Policy" (sources confirmed: `sap-s4…`, `sap-crm…`, `credit-management-policy…`).
- **F2:** "from your 2025 order-flow data and customer-service escalation log, read against your Order Management SOP and Order-to-Cash RACI."
- **F3:** "from your 2025 order-flow data and your customer-service team's EDI working notes." (sources confirmed: `order-flow…`, `order-management-sop…`, `edi-dispute-resolution-cs-working-notes`.)

Number phrasing carries NO mechanism: "267 of 318 shared accounts carry a different credit limit between your ERP and your CRM." Quote phrasing attributes to the friendly name: *"Your Credit Management Policy is explicit: 'SAP S/4HANA is the sole authoritative source…'."*

---

## 5. Report 01 factual-only rule (binding)

1. **Structural impossibility:** `CurrentState`/`ProcessStep`/`RaciRow`/`InventoryItem`/`Handoff` carry **no** `severity`/`confidence` field. The Report 01 renderer never imports `_SEV_BADGE`/`_CONF_BADGE` and never references `Finding.severity`. (D9, B18)
2. **Validator lint:** `assert_factual()` rejects diagnostic words across all `current_state.*` strings (§2b). (B9/FM-10)
3. **Prompt:** rule 3 forbids evaluative vocabulary in `current_state`; failure-points belong to Report 04's before-process, never Report 01. (FM-10)
4. **No red/amber anywhere in 01;** unowned steps render literally "Not assigned" (the EDI ownership fact stated neutrally, no "gap"). (Brief)
5. **`assert_no_leaks` + a Report-01-only `assert_factual` pass** run on the rendered 01 markdown before write.

---

## 6. The 6-report renderer (Python) + HTML/CSS skeleton

New package **`discovery/reportsuite/`**. The renderer reads ONLY `SynthesisContent` + `SourceDoc[]` (sanitized view) — tool names/locators are unreachable by type. Report 06 is generated **deterministically** from `registry.DOC_META` + per-finding sources (no LLM — B8). The 2x2 and before/after are **pure CSS** (offline-safe).

```
discovery/reportsuite/
  __init__.py
  build.py        # build_synthesis_from_payload(raw_payload, fixture|live) -> SynthesisContent
                  #   + build_source_index(DOC_META, findings) -> list[SourceDoc] (B8)
                  #   + number-integrity via §2b allow-list (Metrics, not prose — FM-2)
  render.py       # render_suite(synthesis, meta, outdir): r01..r06 + index.html
  assets.py       # CSS, JS string constants
```

```python
# reportsuite/render.py
def render_suite(s: SynthesisContent, meta: dict, outdir: Path) -> None:
    reports = [("01-current-state","Current State Assessment", r01),
               ("02-pain-points","Pain Points & Opportunities", r02),
               ("03-recommendation","Transformation Recommendation", r03),
               ("04-opportunity-portfolio","AI Opportunity Portfolio", r04),  # centrepiece
               ("05-roadmap","Transformation Roadmap", r05),
               ("06-supporting-artefacts","Supporting Artefacts", r06)]
    nav = [(slug, title) for slug, title, _ in reports]
    (outdir/"assets").mkdir(parents=True, exist_ok=True)
    (outdir/"assets"/"report.css").write_text(CSS); (outdir/"assets"/"report.js").write_text(JS)
    for slug, title, fn in reports:
        md = fn(s, meta)
        assert_no_leaks(md)                                  # per-report guard (4d)
        if slug == "01-current-state": assert_factual_md(md) # 01 only (§5)
        (outdir/f"{slug}.md").write_text(md, encoding="utf-8")
        (outdir/f"{slug}.html").write_text(html_page(title, md_to_html(md), nav, slug, meta),
                                           encoding="utf-8")
    (outdir/"index.html").write_text(shell_page(nav, meta), encoding="utf-8")
```

**Per-report content:**
- **r01** Domain Overview, Process Inventory, Process Flow table (Step|Performed by|System|Notes — neutral notes only), Ownership Map RACI table ("Not assigned" where unowned), System Inventory (system-of-record for credit terms = SAP S/4HANA), Handoff Catalogue. NO badges, NO diagnostic words.
- **r02** Pain Point Register ranked by `impact_rank`; per PP: description, root cause, failure pattern, quantified metrics via `Metric.cite()`, `cite(sources)`, Opportunity Signal → "addressed by {OPP}" (from fixed map). Cross-**process** patterns (FM-8). Impact shown as High/Medium text (no emoji).
- **r03** Value/Feasibility **2x2** (CSS grid `.matrix`, opps placed by `value_score`/`feasibility_score`; `.quad.do_first` blue tint = emphasis not alarm), Opportunity Ratings table (derived from `Opportunity` fields — FM-7), Sequencing Rationale (OPP1→OPP3 in business language), Dependencies note, Strategic Readiness.
- **r04 (centrepiece)** per opportunity: Overview; **Before** process (steps + actors + systems + failure points as muted `.failpoint` annotations) and **After** process side-by-side (`.ba-grid`); Business Impact (`narrative` + `Metric.cite()` + `derivation`); Implementation Approach; Required Integrations (system names); Success Metrics; Dependencies ("Requires OPP1 first" / "None — independent" + OPP1 shows **"Prerequisite for OPP3"** per FM-12); Risks. Opp3 impact = "applies to the EDI channel carrying 67% of orders" — NOT a fabricated real-time throughput number (FM-12).
- **r05** 3 horizons (H1/H2/H3) with `RoadmapItem`s; non-opp items (TSA transition without a count per D2, EDI middleware assessment, CRM consolidation, EDI modernisation, ERP credit module) carry `opportunity_id=None`; `strategy_profile` posture banner.
- **r06** Source Document Index table (Document | Type | What it is | Findings it supported = F1/F2/F3) — **the only place doc filenames appear**, never a tool, never a raw quote (FM-5; `what_we_read` is a curated paraphrase). Plus diagram/context-map/data-flow/event-catalogue/exception-register placeholders + a line: "A full technical trace of every figure is available to your data team on request" (points to `internal_trace` in the JSON).

**HTML/CSS skeleton:** fixed dark left sidebar nav + content pane; restrained corporate palette; single calm accent `#1f6feb` used for emphasis only (no red/amber status colours anywhere); `.ba-grid` 2-col before/after; `.matrix` 2x2 CSS grid; `.failpoint`/`.prov` muted; print + mobile media queries. Use the SCRUB/RENDERER `report.css` verbatim with these corrections: **fix the `html_page` nav bug** — `zip([t for _,t in nav], nav)` shadows `n` and scrambles links; replace with `for (slug, title) in nav: f'...href="{slug}.html">{title}</a>'` (FM-14). For Friday ship **6 standalone HTML files + simple nav links**; the iframe `?embed=1` shell is post-Friday polish (FM-13).

**Number formatting (`fmt_value`):** ONE canonical display per metric (FM-3/FM-15): headlines compact (`€600,000`, `€30.7M`, `€12.36M`, `67%`, `267 of 318`); full figure only in `derivation`. The synthesis layer references the `Metric`, never re-types the number.

---

## 7. Ordered build task list (mapped to files)

Ship as **two PRs** so a synthesis bug can't block the leak fix (Scrub-FM-9).

### PR-A — Leak fix + audit-trail (small, ships independently, de-risks constraint #1)
1. **`discovery/docnames.py`** (new): SCRUB Deliverable-1 map for all 12 docs; `_stem` (known-ext only), `friendly` (hard-fail unknown on demo path), `business_phrase`, `business_phrase_list` (ERP+CRM collapse), `_meta`. *(§4a)*
2. **`discovery/assemble.py`**: delete the `(computed by …)` fold (L1); friendly-name the quote attribution (L2); add `cite()`. **Keep** `recommendations=[]` for now (the suite no longer uses it). *(§4b/4c)*
3. **`discovery/report.py`**: `cite` for `_cite`/`_Based on:` (L3/L4); Inputs table → friendly + `kind` (L5); title/subtitle (L9/L10); add `assert_no_leaks` and call it before .md/.html write only. Test against current `report-o2c.md` first (FM-7).
4. **`discovery/models.py`**: add `raw_payload` field to `DiscoveryResult`.
5. **`run.py`**: set `result.raw_payload = payload`; write `out/discovery-o2c.json` = `{**result.to_dict(), "internal_trace": payload}` (D4 — the load-bearing FM-1 fix). Verify `internal_trace.findings[*].computed_values[*].from_tool` is present on disk.
6. **`tests/test_no_leak.py`** (new): rendered md passes `assert_no_leaks`; `internal_trace` retains `from_tool`/`locator`.

### PR-B — The 6-report suite (the real deliverable)
7. **`discovery/models.py`**: add all §1 dataclasses + `synthesis`/`process_summary` fields on `DiscoveryResult`.
8. **`inputs/o2c/synthesis_o2c.json`** (new): hand-curated, hand-grounded fixture (3 pain points, 3 full opportunities with before/after, current state, roadmap). **This is the demo content** (D1). Validate it through `validate_synthesis` so the fixture itself is proven grounded.
9. **`discovery/synthesis.py`** (new): `synthesis_emit_tool`, `allowed_numbers`, `validate_synthesis`, `assert_factual`, `run_synthesis` (live, `messages_with_tools` + 1 re-prompt + fixture fallback), `PP_TO_OPP`. *(§2)* Built + unit-tested; NOT on default path.
10. **`discovery/reportsuite/build.py`** (new): `build_synthesis_from_payload` (fixture default; live if `--live-synth`); `build_source_index` from `DOC_META` + findings (B8); derive `addresses_pain_point`/`opportunity_signal`/`prerequisite_for`/`matrix_quadrant` from code constants.
11. **`discovery/reportsuite/render.py`** + **`assets.py`** (new): r01–r06, `html_page` (nav bug fixed FM-14), `shell_page`, `md_to_html`, CSS/JS. *(§6)*
12. **`run.py`**: after discovery → `build_synthesis_from_payload` → `render_suite(..., out/"o2c")`; print **`out/o2c/index.html`** as the deliverable (D5); add `--live-synth` flag (default fixture).
13. **`tests/test_suite.py`** (new): all 6 HTML files pass `assert_no_leaks`; Report 01 passes `assert_factual`; OPP3 deps == {OPP1}, H1⊇{OPP1,OPP2}, OPP3∈H2; every `Metric.value` on the allow-list; no TSA count anywhere (D2).
14. **`discovery/stages.py`**: re-enable `classify` on the agent path (kills "unknown" doc types/summaries in the Inputs table) before assemble. *(B/FM-9)*

**Demo path (Friday):** `python run.py --domain o2c --golden` → fixture synthesis → 6 reports → opens `out/o2c/index.html`. No LLM at render time, byte-deterministic, zero fabrication-rejection risk. Live discovery half is unchanged and still the "show." `--live-synth` + re-`--save-golden` is the post-Friday path.
