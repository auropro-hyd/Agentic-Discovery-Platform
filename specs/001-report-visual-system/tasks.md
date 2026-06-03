# Tasks: Report Visual System

**Spec**: ./spec.md | **Plan**: ./plan.md | **Branch**: feat/better-results

Conventions: each task ends green (pytest 100% + pyrefly 0). `[P]` = can parallelize. Validate
visuals by rendering to PNG/PDF and LOOKING, not by reading markup. Iterate against the golden
replay (no spend). Commit per phase.

## Phase 0 — Design tokens (CSS identity foundation)
- **T001** In `assets.py` `:root`: add the "Deep Teal & Graphite" tokens — `--accent:#0f7c8c`
  (primary, replacing blue), `--accent-soft` teal tint, `--warm:#c8772e` (sparing), chart series
  ramp vars, spacing scale vars. Repoint existing `--accent` usages to teal.
- **T002** Add the serif display stack (`--display: Georgia, "Charter", "Iowan Old Style", serif`)
  and apply to h1/h2/h3, `.cover .ctitle`, `.kpi-v`, big stat numbers. Body/tables stay sans.
- **T003** Visual check (golden replay → screenshot index + 01 + 04): palette is teal, display is
  serif, nothing regressed. Commit "Phase 0: design tokens".

## Phase 1 — Heading rhythm + KPI icons
- **T004** Add a section-number chip to h2 headings: a small teal tile with the "1.3"-style number
  + thin rule. Implement as a render helper that wraps numbered section headings (keep plain h2
  where no number). `[P]` with T005.
- **T005** `[P]` KPI tiles: serif numbers (done via T002), add a small inline-SVG category glyph per
  tile + the teal top-rule; ensure 5-across in print holds.
- **T006** Subtle diagonal motif echo on the exec-summary hero / section dividers (CSS only).
- **T007** Tests: assert section-number chip markup renders on a numbered heading; KPI icon present.
  Visual check + commit "Phase 1: heading rhythm + KPI icons".

## Phase 2 — Roadmap timeline (P1)
- **T008** `roadmap_timeline_svg(roadmap, opportunities)` in render.py: 3 horizon bands (H1/H2/H3
  with window labels), each roadmap item placed in its band, opportunity items tagged, dependency
  order respected (dependent never left of prerequisite). Pure SVG, teal house-style,
  break-inside:avoid. Returns "" if roadmap empty.
- **T009** Wire the timeline into r05 above the existing rationale bullets.
- **T010** Tests: empty roadmap → ""; 3-horizon roadmap → 3 bands + items in correct band; the
  rendered r05 HTML contains the timeline. Visual check (r05 both domains).
- **T011** Commit "Phase 2: roadmap timeline".

## Phase 3 — Grounded charts (P1)
- **T012** `build.derive_charts`: add a value-by-category donut series where grounded (e.g. EDI vs
  other channels by € value, from findings' computed_values). Defensive: include only if all
  segment values are grounded and reconcile; else omit. `[P]` with T013.
- **T013** `[P]` Chart house-style: ensure donut + bar share the teal ramp, tabular labels, and a
  one-line takeaway caption above each.
- **T014** Wire `render_charts` (donut + bar) into r02 and/or r06 appropriately.
- **T015** Tests: derive_charts emits the donut series when data present, omits when absent; donut
  renders with grounded segments reconciling to total; P2P omits. Visual check.
- **T016** Commit "Phase 3: grounded charts (donut + house style)".

## Phase 4 — Before/After visual (P2)
- **T017** Before/After visual in r04: two colour-coded columns (before = muted, after = teal) with
  a connecting arrow + numbered step chips, using existing step text verbatim. Replace the plain
  `.ba-grid` text columns; keep failure-point chips.
- **T018** Tests: r04 renders the before/after visual with both sides + connector; step text
  unchanged. Visual check (r04 both domains).
- **T019** Commit "Phase 4: before/after visual".

## Phase 5 — Full validation + ship
- **T020** Render BOTH domains (o2c, p2p), HTML + merged PDF; review every page visually (cover,
  TOC, all 7 reports) — confirm identity applied, charts present where grounded, pages fill, no
  sparse whitespace, chrome intact.
- **T021** `uv run coverage run -m pytest && uv run coverage report` → 100%; `uv run pyrefly check
  discovery run.py scripts` → 0 errors; grounding + assert_factual pass; re-validate every
  chart/KPI value from raw inputs (exact).
- **T022** Regenerate committed suites + PDFs for both domains. Commit "Phase 5: validated visual
  system" + push. Update PR #2 description. (Optional: one live o2c run to re-confirm end-to-end.)

## Coverage / grounding guardrails (apply to every task)
- New render functions get empty + populated + edge-case unit tests (hold 100% branch coverage).
- No chart/visual may introduce a number not already grounded; omit rather than fabricate.
- Visual sign-off is by looking at rendered output, both domains, HTML and PDF.
