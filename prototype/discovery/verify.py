"""Adversarial verification of findings.

The grounding gate proves every NUMBER traces to the data. This step goes further: it challenges
each finding's REASONING — is the stated conclusion actually supported by the cited evidence, or is
it a plausible-but-unsupported inference (e.g. a causal claim from correlational data)? An
independent LLM call plays skeptic per finding and returns a verdict.

Design:
- Verdict is advisory metadata on the finding (`verification`), never a silent delete. A finding
  the verifier challenges is marked so the SME sees it; the SME still decides.
- Degrades gracefully: if offline / no creds, findings are marked "not verified" and pass through
  unchanged — verification is additive, never a hard blocker.
- The verifier sees ONLY the finding + its cited evidence (numbers and quotes already in the
  payload), so it cannot introduce new ungrounded claims.
"""
from __future__ import annotations

import json

from .llm import LLMError

VERIFY_SYSTEM = (
    "You are a skeptical reviewer checking a single discovery finding before it reaches a client. "
    "You are given the finding and ONLY the evidence it cites (computed numbers + document quotes). "
    "Judge whether the stated conclusion is genuinely SUPPORTED by that evidence, or whether it "
    "over-reaches — e.g. asserts a causal link from correlational data, generalises beyond what the "
    "numbers show, or states something the quotes do not actually say. Default to skepticism: if the "
    "evidence does not clearly support the conclusion, mark it unsupported. Reply with strict JSON "
    "only: {\"supported\": true|false, \"reason\": \"...\", \"suggested_fix\": \"...\"}. "
    "suggested_fix is how to reword the finding to match only what the evidence supports (empty if "
    "supported)."
)


def _finding_brief(f: dict) -> str:
    cv = "; ".join(f"{c.get('label')}={c.get('value')}" for c in f.get("computed_values", []))
    nv = "; ".join(f"{n.get('label')}: “{n.get('quote','')}”" for n in f.get("narrative_values", []))
    return (f"TITLE: {f.get('title')}\n"
            f"CLAIM: {f.get('description')}\n"
            f"BUSINESS CONSEQUENCE: {f.get('business_consequence')}\n"
            f"COMPUTED EVIDENCE: {cv or '(none)'}\n"
            f"DOCUMENT EVIDENCE: {nv or '(none)'}")


def verify_findings(llm, payload: dict, model=None) -> dict:
    """Annotate each finding with a `verification` verdict. Mutates and returns the payload.
    Never raises on verification failure — offline / errored verifications are marked, not fatal."""
    for f in payload.get("findings", []):
        try:
            verdict = llm.complete_json(VERIFY_SYSTEM,
                                        "Review this finding:\n\n" + _finding_brief(f), model=model)
            if not isinstance(verdict, dict):
                verdict = {"supported": None, "reason": "verifier returned non-JSON"}
            f["verification"] = {
                "supported": verdict.get("supported"),
                "reason": str(verdict.get("reason", ""))[:400],
                "suggested_fix": str(verdict.get("suggested_fix", ""))[:400],
            }
        except (LLMError, json.JSONDecodeError, KeyError) as e:
            # offline or verifier hiccup — additive step, so degrade to "not verified"
            f["verification"] = {"supported": None, "reason": f"not verified ({type(e).__name__})"}
    return payload


def verification_summary(payload: dict) -> dict:
    """Counts for logging: how many findings were challenged."""
    v = [f.get("verification", {}).get("supported") for f in payload.get("findings", [])]
    return {"total": len(v),
            "supported": sum(1 for x in v if x is True),
            "challenged": sum(1 for x in v if x is False),
            "unverified": sum(1 for x in v if x is None)}
