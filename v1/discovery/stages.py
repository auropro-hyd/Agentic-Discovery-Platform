"""The discovery pipeline stages.

Linear and explicit (no orchestrator). Each stage is a plain function taking the LLM
client and the working state, returning enriched state. Prompts are pinned here so that,
with temperature 0 + caching, output is consistent run to run.

Stages:
  1. classify        - assign a category to each document
  2. extract         - pull systems/processes/actors/handoffs (with source refs)
  3. cross_reference - compare claims across docs -> contradictions and gaps (findings)
  4. flag            - rank candidate resolutions + assign evidence-based confidence
  5. (resolve lives in resolve.py - it is interactive)
  6. synthesize      - process summary + transformation recommendations (with justification)
"""
from __future__ import annotations

import json
import textwrap

from .llm import LLMClient
from .models import (
    CandidateResolution,
    ConfidenceTier,
    DocCategory,
    Document,
    Entity,
    Finding,
    Recommendation,
    Severity,
    SourceRef,
)

# A shared instruction reused across stages. The provenance rule is the heart of trust.
SYSTEM = textwrap.dedent(
    """\
    You are an enterprise discovery analyst. You read business-process documentation and
    system exports for a company and reconstruct how a business process actually works,
    which systems and owners are involved, and where the documentation contradicts reality
    or leaves gaps.

    Rules you must always follow:
    - Ground every claim in the documents provided. Never invent systems, numbers, or
      events that are not supported by the text.
    - For every finding, cite the specific documents (by their id) that support it.
    - A finding must require evidence from at least two documents. If only one document
      mentions something, it is a single-source claim (lower confidence), not a finding.
    - Do not infer causal or statistical relationships (e.g. time lags) from narrative
      text. Only report quantitative relationships that are explicitly stated in a
      document. If a relationship is only implied, describe it as a structural dependency,
      not a measured fact.
    - Output strictly valid JSON when asked. No prose outside the JSON.
    """
)


def _docs_block(docs: list[Document]) -> str:
    """Render documents for a prompt: id, then text (trimmed)."""
    parts = []
    for d in docs:
        body = d.text.strip()
        if len(body) > 6000:
            body = body[:6000] + "\n...(truncated)"
        parts.append(f"=== DOCUMENT id={d.doc_id} ===\n{body}")
    return "\n\n".join(parts)


# ---- stage 1: classify ----------------------------------------------------
def classify(llm: LLMClient, docs: list[Document]) -> list[Document]:
    prompt = textwrap.dedent(
        f"""\
        Classify each document into exactly one category and give a one-line title and a
        one-sentence summary. Categories:
          structured        - SOPs, policies, RACI matrices, registers
          semi_structured    - meeting transcripts, review notes
          system_signal      - CSV exports, audit/event logs
          unstructured       - working notes, escalation logs, informal "how we do it"
          comparative        - inherited/legacy SOP from a parent org

        Return JSON: a list of objects with keys: doc_id, category, title, summary.

        {_docs_block(docs)}
        """
    )
    result = llm.complete_json(SYSTEM, prompt)
    by_id = {r["doc_id"]: r for r in result}  # type: ignore[index]
    for d in docs:
        r = by_id.get(d.doc_id, {})
        try:
            d.category = DocCategory(r.get("category", "unknown"))
        except ValueError:
            d.category = DocCategory.UNKNOWN
        d.title = r.get("title", d.doc_id)
        d.summary = r.get("summary", "")
    return docs


# ---- stage 2: extract -----------------------------------------------------
def extract(llm: LLMClient, docs: list[Document]) -> list[Entity]:
    prompt = textwrap.dedent(
        f"""\
        Extract the key elements of the business process across these documents. For each
        element give: name, kind (one of: system, process, actor, decision, handoff), the
        document ids it appears in, and any salient attributes (e.g. owner, channel,
        stated authority, numbers explicitly given in the text).

        Return JSON: a list of objects with keys:
          name, kind, sources (list of {{doc_id, locator, quote}}), attributes (object).

        {_docs_block(docs)}
        """
    )
    result = llm.complete_json(SYSTEM, prompt)
    entities: list[Entity] = []
    for e in result:  # type: ignore[union-attr]
        entities.append(
            Entity(
                name=e.get("name", ""),
                kind=e.get("kind", ""),
                sources=[_ref(s) for s in e.get("sources", [])],
                attributes=e.get("attributes", {}),
            )
        )
    return entities


# ---- stage 3 + 4: cross-reference -> flagged findings ---------------------
def cross_reference(llm: LLMClient, docs: list[Document], entities: list[Entity]) -> list[Finding]:
    entity_json = json.dumps([e.to_dict() for e in entities], ensure_ascii=False, indent=2)
    prompt = textwrap.dedent(
        f"""\
        Using the documents and the extracted elements, find CONTRADICTIONS and GAPS that
        only become visible by cross-referencing two or more documents.

        A contradiction = two documents assert incompatible things (e.g. a policy states X
        but a system log shows Y). A gap = something referenced but unverifiable, or a
        critical process with no documented owner / system of record.

        For each finding, also propose 2-3 candidate resolutions ranked by evidence
        strength (strong/moderate/weak) - what the most likely true answer is, each with
        its own source citations. This is what an SME will choose between.

        Assign severity:
          high  - missing system-of-record for a critical process, or a contradiction on a
                  business-critical fact
          amber - referenced-but-unverifiable, or a lower-impact inconsistency

        Assign confidence based ONLY on evidence:
          verified - corroborated across >=2 independent documents
          amber    - single strong source or partially corroborated
          gap      - asserted but unverifiable, or directly contradicted

        Return JSON: a list of findings with keys:
          id (F1, F2, ...), title, severity, description, business_consequence,
          confidence, sources (list of {{doc_id, locator, quote}}),
          candidates (list of {{id, summary, rationale, evidence_strength,
                                 sources:[{{doc_id, locator, quote}}]}}).

        Extracted elements:
        {entity_json}

        Documents:
        {_docs_block(docs)}
        """
    )
    result = llm.complete_json(SYSTEM, prompt)
    findings: list[Finding] = []
    for f in result:  # type: ignore[union-attr]
        findings.append(
            Finding(
                id=f.get("id", f"F{len(findings)+1}"),
                title=f.get("title", ""),
                severity=_enum(Severity, f.get("severity"), Severity.AMBER),
                description=f.get("description", ""),
                business_consequence=f.get("business_consequence", ""),
                confidence=_enum(ConfidenceTier, f.get("confidence"), ConfidenceTier.AMBER),
                sources=[_ref(s) for s in f.get("sources", [])],
                candidates=[
                    CandidateResolution(
                        id=c.get("id", f"candidate_{i+1}"),
                        summary=c.get("summary", ""),
                        rationale=c.get("rationale", ""),
                        evidence_strength=c.get("evidence_strength", ""),
                        sources=[_ref(s) for s in c.get("sources", [])],
                    )
                    for i, c in enumerate(f.get("candidates", []))
                ],
            )
        )
    return findings


# ---- stage 6: synthesize summary + recommendations ------------------------
def synthesize(llm: LLMClient, domain_label: str, docs: list[Document],
               entities: list[Entity], findings: list[Finding]) -> tuple[str, list[Recommendation]]:
    findings_json = json.dumps([f.to_dict() for f in findings], ensure_ascii=False, indent=2)
    entity_json = json.dumps([e.to_dict() for e in entities], ensure_ascii=False, indent=2)
    prompt = textwrap.dedent(
        f"""\
        Domain: {domain_label}

        Write (a) a concise business-process summary (how the process actually works across
        teams and systems, 1-2 paragraphs, plain business language), and (b) a transformation
        roadmap of recommendations addressing the findings.

        Each recommendation must include a JUSTIFICATION that references the findings or
        documents it is based on - this traceability is essential.

        Intervention types: modernize, automate, agent, hitl (human-in-the-loop workflow).
        Horizons: now (0-6m), next (6-18m), later (18m+).

        Return JSON with keys:
          process_summary (string),
          recommendations (list of {{title, horizon, intervention, justification,
                                      sources:[{{doc_id, locator, quote}}]}}).

        Findings:
        {findings_json}

        Extracted elements:
        {entity_json}
        """
    )
    result = llm.complete_json(SYSTEM, prompt)
    recs = [
        Recommendation(
            title=r.get("title", ""),
            horizon=r.get("horizon", "now"),
            intervention=r.get("intervention", ""),
            justification=r.get("justification", ""),
            sources=[_ref(s) for s in r.get("sources", [])],
        )
        for r in result.get("recommendations", [])  # type: ignore[union-attr]
    ]
    return result.get("process_summary", ""), recs  # type: ignore[union-attr]


# ---- helpers --------------------------------------------------------------
def _ref(s: dict) -> SourceRef:
    return SourceRef(
        doc_id=s.get("doc_id", ""),
        locator=s.get("locator", ""),
        quote=s.get("quote", ""),
    )


def _enum(enum_cls, value, default):
    try:
        return enum_cls(value)
    except (ValueError, TypeError):
        return default
