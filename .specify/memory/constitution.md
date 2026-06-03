# AuroPro Autonomous Discovery Platform Constitution

The engine lives in `v1/`. It reads a folder of enterprise documents, genuinely discovers
findings (contradictions, gaps, unowned processes), and produces a client-ready discovery report
suite. These principles are not aspirational — they describe how the codebase already works and
MUST keep working. Any change that violates one is wrong by definition.

## Core Principles

### I. Grounded, Never Fabricated (NON-NEGOTIABLE)
"Code does the math; the LLM does the reasoning." Every client-facing number MUST trace to a
verified finding computed by a deterministic tool from the real input data. No figure may be
invented, estimated, summed, averaged, or rounded into existence by the model — this includes
narrative numbers, chart values, KPI tiles, and metric targets (targets are DIRECTIONAL goals,
never invented percentages or timeframes). A synthesis-time grounding gate (`validate_synthesis`)
rejects any untraceable number, and figures are independently re-validated from the raw inputs.
A new visual or section that cannot be backed by a grounded number does not get a fabricated one —
it is omitted.

### II. Factual Current State
The current-state report states facts only — no evaluative or diagnostic language (no "risk",
"gap", "exposure", "breach", "critical", "conflict"). Diagnosis belongs in pain points and
opportunities. Enforced by `assert_factual`; where a step has no owner, it reads "Not assigned".

### III. Domain-Agnostic & Generic
The engine works on any client and any domain by dropping documents into `inputs/<domain>/` with
ZERO code changes. No hardcoded client names, no domain constants in the engine. A client name is
shown only when detected from the documents, and never when suppressed. A fixture or scripted path
for one domain MUST NOT render for another.

### IV. Deterministic & Replayable
LLM calls are temperature-pinned with full-history on-disk caching, so replays are byte-stable. A
saved "golden" run replays entirely offline for free (no spend) and is the basis for iterating on
rendering without re-paying for discovery. Tools are deterministic (Decimal/ROUND_HALF_EVEN,
sorted output).

### V. 100% Tested, Type-Clean (NON-NEGOTIABLE)
The active pipeline holds 100% statement AND branch coverage, enforced in CI via
`fail_under = 100`. Product code (`discovery/`, `run.py`, `scripts/`) is pyrefly-clean. Tests use
fake LLMs / pure tools (no live API) and drive the real contracts. A change ships only when the
full suite is green at 100% and pyrefly reports zero errors.

### VI. Offline-Safe, Self-Contained Rendering
The report suite is pure inline SVG + CSS — no external libraries, fonts, CDNs, or network calls.
It renders identically anywhere, online or off. Charts and visuals are code-owned and grounded;
they render only when their data exists and gracefully omit themselves otherwise.

## Additional Constraints

- Python 3.11+ managed by `uv`; the LLM provider is Anthropic (Opus class), with the real HTTP
  client out of unit-test scope (exercised by the live run).
- No secrets in git (`.env` is gitignored); the LLM response cache and venv are gitignored.
- The deliverable is the Discovery Report suite only (HTML + a print-quality PDF). Other consulting
  artifacts referenced by prior engagements are formatting references, not build targets.
- Open questions / unresolved gaps are NOT surfaced in the client report; the SME-resolution loop
  is operator-side so that what ships is already resolved and meaningful.

## Development Workflow & Quality Gates

- Spec-driven: substantial features get a spec -> plan -> tasks under `specs/<feature>/` before
  implementation.
- Build offline-first against the golden replay; spend on live runs only to validate, and
  re-validate every number independently from raw inputs.
- Every change: `uv run coverage run -m pytest && uv run coverage report` (100% gate) and
  `uv run pyrefly check discovery run.py scripts` (0 errors) must pass; pre-commit hooks enforce
  the type check and file hygiene.
- Validate visual/report changes by actually looking at the rendered output (HTML screenshots AND
  the PDF pages), not by reading markup.

## Governance

This constitution supersedes convenience. Any PR that weakens a grounding/factual/coverage guard
must justify it explicitly and is the rare exception, not the norm. Complexity must earn its place.
Runtime guidance for agents lives in the repo's CLAUDE/memory; this document governs what "correct"
means for the discovery engine.

**Version**: 1.0.0 | **Ratified**: 2026-06-03 | **Last Amended**: 2026-06-03
