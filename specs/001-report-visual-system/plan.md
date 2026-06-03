# Implementation Plan: Report Visual System

**Branch**: `feat/better-results` | **Date**: 2026-06-03 | **Spec**: ./spec.md

## Summary

Give the 7-report discovery suite a distinctive editorial-consulting visual identity (approved) and
add grounded visuals where they aid comprehension: a roadmap timeline, a value-by-channel donut +
other grounded charts, and a visual before→after on the opportunity portfolio. Pure inline SVG/CSS,
offline-safe, every value grounded, 100% coverage held. Rendering layer only — no change to the
discovery/synthesis logic or the numbers.

## Technical Context

**Language/Version**: Python 3.11+ (3.14 venv), uv-managed.
**Primary Dependencies**: stdlib only for rendering (inline SVG strings + CSS); pypdf (dev) for PDF
merge; headless Chrome (operator) for PDF.
**Storage**: file-based — HTML suite under `v1/out/<domain>/`, golden cache under `v1/golden/`.
**Testing**: pytest + coverage (branch, fail_under=100); pyrefly type-check on product code.
**Target Platform**: any modern browser (screen) + headless-Chrome print (PDF); fully offline.
**Project Type**: single CLI project (the `v1/discovery` package).
**Performance Goals**: N/A (render is sub-second); determinism > speed.
**Constraints**: offline-safe (no network/web-fonts/libs); print pages must fill (no sparse
whitespace); grounding + factual guards must pass.
**Scale/Scope**: 7 reports × 2 validated domains; ~12 grounded figures per O2C run.

## Constitution Check

*GATE: passes — this feature is rendering-only and strengthens, never weakens, the guards.*

- **I. Grounded, never fabricated** — PASS. Chart/timeline/KPI values come only from grounded
  findings via `build.derive_charts` / existing `NumberRef`s. Visuals omit themselves when data is
  absent. No new numbers introduced. Re-validated from raw inputs at the end.
- **II. Factual current state** — PASS. No Report-01 prose changes; `assert_factual` still runs.
- **III. Domain-agnostic** — PASS. Charts are data-driven (label-matched), no domain constants; the
  identity is generic CSS. P2P omits charts it lacks data for.
- **IV. Deterministic & replayable** — PASS. SVG is deterministic; iterate against the golden
  replay (no spend). One optional live run only to re-confirm.
- **V. 100% tested, type-clean** — PASS (gate). New render functions get unit + render-branch tests
  to hold 100%; pyrefly clean.
- **VI. Offline-safe rendering** — PASS. System serif stack (no web-font fetch), inline SVG/CSS.

No violations → Complexity Tracking empty.

## Project Structure

### Documentation (this feature)
```text
specs/001-report-visual-system/
├── spec.md          # the what + visual identity (approved)
├── plan.md          # this file
└── tasks.md         # task list (next)
```

### Source Code (touched paths — rendering layer only)
```text
v1/discovery/
├── models.py                      # (already) SynthesisContent.charts; no new fields expected
└── reportsuite/
    ├── assets.py                  # CSS design tokens + identity (palette, serif type, motifs,
    │                              #   section-number chips, KPI icons, before/after, timeline,
    │                              #   chart house-style, print rules)
    ├── build.py                   # derive_charts: add value-by-category donut series (grounded)
    └── render.py                  # roadmap_timeline_svg, before/after visual, donut wiring,
    │                              #   section-number-chip helper, KPI icons; wire into r00..r06
v1/scripts/make_pdf.py             # unchanged (chrome already correct)
v1/tests/
├── test_render_branches.py        # unit tests for new SVG helpers (empty + populated + edges)
├── test_build.py                  # derive_charts new series (grounded + omitted)
└── test_suite.py                  # assert new visuals present in rendered HTML, both code paths
```

**Structure Decision**: Single project; all work in `v1/discovery/reportsuite/` (+ targeted tests).
The chart-data contract (`SynthesisContent.charts`) already exists from prior work; the donut just
needs an additional grounded series in `derive_charts`. No new model fields anticipated; if the
timeline needs a derived structure it stays code-owned in render (from existing roadmap data).

## Phased Approach

**Phase 0 — Design tokens (CSS foundation).** Establish the identity in `assets.py` `:root`:
teal-primary palette, serif display stack, spacing scale, chart series ramp, warm accent. Re-point
existing components (accent blue → teal). Verify nothing breaks visually (golden replay screenshot).

**Phase 1 — Section-number chips + heading rhythm + KPI icons.** Pervasive low-risk polish.

**Phase 2 — Roadmap timeline (P1).** `roadmap_timeline_svg(roadmap, opportunities)` — 3 horizon
bands, items placed, opportunity tags, dependency order respected. Wire into r05.

**Phase 3 — Grounded charts (P1).** Add value-by-category donut series to `derive_charts`; wire
`render_charts` donut + the existing bar into r02/r06; chart house-style + takeaway captions.

**Phase 4 — Before/After visual (P2).** Colour-coded before→after with connector + step chips in r04.

**Phase 5 — Validate.** Screenshot every report (both domains, HTML + PDF) and look; 100% coverage
+ pyrefly + grounding; re-validate numbers from raw; commit per phase; push.

Each phase: implement → `pytest`+coverage 100% → pyrefly → visual check → commit.
