# Feature Specification: Report Visual System — distinctive, chart-rich, print-grade

**Feature Branch**: `feat/better-results` (continues the current branch)

**Created**: 2026-06-03

**Status**: Draft — awaiting visual-identity sign-off

**Input**: "Make the discovery reports more flavourful and visually appealing while still being
similarly or more informative. Refined corporate but distinctive — better than the generic
'AI-generated report' look. Add a roadmap timeline, a channel donut + more charts, a before/after
visual, and design-system polish."

---

## Context

The discovery suite (7 reports, HTML + a print-quality PDF) is correct and information-dense, but
visually it reads like a generic AI-generated report: monotone grey text blocks, one accent blue,
charts only in a couple of places, and some reports (esp. Roadmap) are nearly all text. This
feature gives the suite a **distinctive, refined-corporate visual identity** and adds grounded
visuals where they increase comprehension — without changing a single number or weakening any
grounding/factual guard.

Hard boundary (Constitution I & VI): every chart value is a grounded figure; charts render only
when their data exists; everything is pure inline SVG/CSS (offline-safe). No fabrication, ever.

---

## Proposed Visual Identity (REQUIRES SIGN-OFF before build)

A deliberate move away from the "default Tailwind/AI" look toward an **editorial-consulting** style
— authoritative, calm, and unmistakably AuroPro.

**1. Palette — "Deep Teal & Graphite" (anchored to the existing AuroPro cover)**
- Primary ink: graphite `#1a2230`; muted `#5b6776`
- Brand anchor: deep teal `#0f7c8c` (from the cover) becomes the PRIMARY accent — replaces the
  generic blue `#1f6feb` as the dominant colour, giving instant brand identity.
- Secondary accent: a warm signal `#c8772e` (amber-bronze) used SPARINGLY for "do first" / highest
  impact emphasis only — one warm note against the cool palette is what reads as "designed."
- Chart series ramp: teal-family `#0f7c8c → #2a93a3 → #5fb0bc → #9fccd3 → #cfe6ea` (cool, cohesive).
- Surfaces: panel `#ffffff`, page `#f6f8f9`, hairlines `#e3e8ee`. Readiness badges keep
  green/amber/red (semantic, unchanged).

**2. Typography**
- Display (h1/h2 + cover + big stat numbers): a serif or high-contrast display face for an
  editorial, non-techy feel — **Georgia/"Iowan"/"Charter" serif stack** (system-available,
  offline-safe; no web-font fetch). This single change most differentiates us from AI-default
  sans-serif reports.
- Body + tables + chart labels: the existing system sans (clean, legible).
- Numbers use tabular figures.

**3. Motifs (the "flavour")**
- A thin **teal rule + section number chip** on every h2 (e.g. a small teal "1.3" tile) — gives a
  designed, navigable rhythm instead of plain underlined headings.
- The **cover's diagonal motif** echoed subtly: a small diagonal corner accent on the exec-summary
  hero and section dividers.
- KPI tiles: larger serif numbers, a small unit/label, a thin teal top-rule (kept) + a faint
  category icon (inline SVG glyph) per tile.
- Generous whitespace rhythm and consistent vertical spacing (an 8px base scale).

**4. Charts — consistent house style**
All charts share: teal series ramp, thin axis hairlines, tabular value labels, a one-line
takeaway caption above (the "so what"), and `break-inside:avoid` for print.

---

## User Scenarios & Testing

### User Story 1 - Roadmap timeline (Priority: P1)

The Transformation Roadmap (Report 05) is today an almost-empty page of text bullets under H1/H2/H3.
A reader should SEE the three horizons as a timeline with the opportunities placed on it.

**Why this priority**: Biggest visual gap (mostly empty page) and highest comprehension gain — a
sequenced plan is inherently visual.

**Independent Test**: Render Report 05 for O2C and P2P; a horizontal 3-horizon timeline/swimlane
SVG appears with each horizon band (H1/H2/H3, with its window label) and the opportunities placed
in the correct band; the existing rationale bullets remain beneath. No numbers invented (positions
come from horizon membership + dependency order already in the data).

**Acceptance Scenarios**:
1. **Given** a synthesis with a 3-horizon roadmap, **When** Report 05 renders, **Then** a timeline
   SVG shows three labelled bands with each roadmap item in its horizon, opportunities visually
   tagged, and dependency order respected (a dependent item never sits left of its prerequisite).
2. **Given** a roadmap with empty horizons, **When** it renders, **Then** the band shows but with
   no fabricated items.

---

### User Story 2 - More grounded charts (donut + channel/value) (Priority: P1)

Surface the grounded breakdowns the data already contains as charts, not just prose: e.g. order
**value by channel** (donut) and the existing unfulfilled-by-channel bar, plus any other
multi-category grounded series `derive_charts` can build.

**Why this priority**: Turns dense numbers into instant comparisons; the donut helper already
exists but is unused.

**Independent Test**: For O2C, Report 02 (or 06) shows a donut of a grounded value split where the
data supports it; every segment value equals a verified finding number; total reconciles. For P2P
(no such breakdown) the donut is absent — no fabrication.

**Acceptance Scenarios**:
1. **Given** findings with a grounded multi-category value/count breakdown, **When** the report
   renders, **Then** a donut (shares) or bar (counts) appears with grounded segment values and a
   takeaway caption.
2. **Given** no such breakdown, **When** the report renders, **Then** no chart is emitted (Constitution I & VI).

---

### User Story 3 - Before/After transformation visual (Priority: P2)

Report 04's per-opportunity "Before → After" is plain text columns. Make it a clear visual
transformation: two columns with a connecting arrow, before = muted/grey, after = teal, numbered
step chips, so the change is legible at a glance.

**Why this priority**: The opportunity portfolio is the centrepiece; the before/after is its core
storytelling device and currently reads flat.

**Independent Test**: Render Report 04; each opportunity shows a before/after panel with a visual
divider/arrow, colour-coded sides, and step chips; all step text unchanged (no new content).

**Acceptance Scenarios**:
1. **Given** an opportunity with before_process and after_process steps, **When** Report 04 renders,
   **Then** the two are shown as a visually distinct, colour-coded before→after with a connector.

---

### User Story 4 - Design-system polish (Priority: P2)

Apply the identity across the whole suite: teal primary accent, serif display type, section-number
chips on headings, KPI/icon treatment, diagonal cover motif echoes, spacing rhythm.

**Why this priority**: This is what makes it "not look like every other AI report." Pervasive but
lower-risk (CSS-led).

**Independent Test**: Visual review of all 7 reports (HTML + PDF, both domains) shows the new
palette/type/motifs consistently; no generic-blue default remains; the cover, TOC, page chrome
intact.

**Acceptance Scenarios**:
1. **Given** the suite renders, **When** reviewed as PDF, **Then** headings carry section-number
   chips + teal rules, display text is serif, the primary accent is teal, and the layout reads as a
   designed editorial-consulting document.

---

### Edge Cases
- A report/section with no chartable data → the visual is omitted, prose stays (no empty chart box).
- Suppressed client name → cover/headers still must not leak it (existing guard).
- Long labels in timeline/donut/before-after → clipped with ellipsis, never overflow.
- Print pagination → all new visuals carry `break-inside:avoid`; pages must still fill (no return
  of the sparse-whitespace regression).
- A roadmap with !=3 horizons, or an opportunity with no before/after steps → degrade gracefully.

## Requirements

### Functional Requirements
- **FR-001**: System MUST render a roadmap timeline SVG on Report 05 from the existing roadmap
  horizons/items, placing opportunities in their horizon and respecting dependency order.
- **FR-002**: System MUST render grounded donut/bar charts (incl. a value-by-category donut where
  the data supports it) using only verified finding numbers; segments MUST reconcile to their total.
- **FR-003**: System MUST render Report 04 before→after as a colour-coded visual with a connector
  and step chips, using the existing step text verbatim.
- **FR-004**: System MUST apply the approved visual identity (palette, serif display type,
  section-number chips, KPI/icon treatment, motifs) across all 7 reports and the cover/TOC/chrome.
- **FR-005**: System MUST omit any visual whose grounded data is absent (no placeholders, no
  fabricated values) — per Constitution I & VI.
- **FR-006**: All visuals MUST be pure inline SVG/CSS (no external fonts/libraries/network) and
  carry print `break-inside:avoid`; the PDF MUST keep the full-bleed cover, TOC, and page chrome,
  and pages MUST fill (no sparse-whitespace regression).
- **FR-007**: System MUST keep 100% statement+branch coverage and pyrefly-clean product code; the
  grounding gate and `assert_factual` MUST still pass on both domains, live and fixture.

### Key Entities
- **ChartSeries** (`SynthesisContent.charts`, code-owned): `{key, kind: donut|bar, unit, title,
  segments:[{label,value}]}` — derived from grounded findings in `build.derive_charts`.
- **RoadmapHorizon / RoadmapItem** (existing): drive the timeline; positions from horizon + deps.
- **Opportunity.before_process / after_process** (existing): drive the before/after visual.
- **Design tokens** (CSS `:root`): palette + type stack + spacing scale — single source of truth.

## Success Criteria

### Measurable Outcomes
- **SC-001**: All 7 reports render for BOTH domains (o2c, p2p), HTML and PDF, with the new identity;
  reviewed visually page-by-page.
- **SC-002**: Report 05 shows a roadmap timeline; Report 04 shows a before→after visual; at least
  one additional grounded chart (donut/bar) appears for O2C; P2P omits charts it has no data for.
- **SC-003**: 100% statement+branch coverage maintained; pyrefly 0 errors; grounding +
  factual-report-01 guards pass on both domains.
- **SC-004**: Every chart/KPI value independently re-validated against raw inputs — exact.
- **SC-005**: No external network/font/library dependency introduced; PDF still has full-bleed
  cover + TOC + page chrome and no sparse-whitespace pages.
- **SC-006**: Side-by-side, a reviewer judges the output visually distinct from a generic
  AI-generated report (qualitative sign-off by the user).

## Assumptions
- The serif display face uses a system-available stack (Georgia/Charter/Iowan) — no web-font fetch,
  preserving offline-safety.
- Visual identity is subject to user sign-off before implementation (this spec proposes it).
- Scope is the report rendering layer (`discovery/reportsuite/`, models for chart data,
  `build.derive_charts`); the discovery/synthesis logic and the numbers are unchanged.
- The roadmap-timeline positions encode horizon + dependency order only; no new quantitative claim.
- Out of scope: an interactive web UI (a later phase); new deliverable types; any change to what
  numbers are computed.
