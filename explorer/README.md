# Discovery Console & Explorer

A **React + Vite + TypeScript** app with two layers:

1. **Discovery Console** (the landing page, `#/`) — the operator flow that wraps the live pipeline
   in six stages: *upload → assessment → discovery copilot → analysis → preview → report
   generation*. It drives the real Python engine (`run.py`) via a small backend, shows a progress
   stepper + live activity feed, surfaces the discovery-copilot gaps for SME feedback, and embeds
   the report suite at the Preview stage. A **skip-to-compiled-reports** breakpoint jumps straight
   to the suite for a demo.
2. **Report Explorer** (`#/suite/<domain>/…`) — the explorable version of the static print/PDF
   deliverable: cross-link pain points ↔ opportunities, filter/sort the portfolio, browse the
   evidence and fact store, read the planning-assumptions ledger, and search the whole suite.

The Explorer ships as static files (no server at view time) — the built `dist/` opens from any
static host or `file://`, deep-linkable via hash URLs. The Console additionally needs the backend
running to drive a live/replay run.

## Backend (for the Console)

The Console talks to `v1/server.py` — a stdlib-only backend (no extra Python deps) that launches
`run.py` as a subprocess, parses its phase signals, and streams them to the browser over SSE.

```bash
cd v1 && uv run python server.py        # http://127.0.0.1:8742
```

Run modes from the Console: **Replay** (`--golden`, cached, ~30–60s, $0 — for the demo) or
**Live** (the real pipeline, minutes, costs API credits). The Explorer alone needs no backend.
Override the API base with `VITE_CONSOLE_API` at build time if hosting the backend elsewhere.

## Data

The SPA renders the synthesis JSON the Python engine produces (`v1/out/discovery-<domain>.json`).
`npm run sync:data` copies those files into `src/data/` so the build is self-contained. Both
`o2c` and `p2p` ship by default; adding a domain is just dropping a new `discovery-<slug>.json`
into `v1/out/` and re-running sync — `import.meta.glob` picks it up, no code change.

## Develop

```bash
cd explorer
npm install
npm run dev        # predev runs sync:data automatically; opens on localhost
```

## Build & ship

```bash
npm run build      # prebuild: sync:data + token-drift check; then tsc --noEmit + vite build
npm run preview    # serve the production build locally
```

The output is `dist/`. Host it anywhere static, or zip it and open `dist/index.html` from
`file://` for an air-gapped client.

## Grounding (why you can trust the numbers)

The SPA inherits the engine's sacred rule — **every client-facing number traces to the data; the
UI never fabricates or derives a figure**, and forward-looking content is shown as clearly-labelled
*planning assumptions*, never as discovered fact. This is enforced in code, not by convention:

1. **Branded `FactValue`** — `<GroundedNumber>` accepts only a `FactValue`, minted in exactly one
   place (`src/lib/store.ts`) straight from parsed JSON. Passing a computed number is a *compile*
   error.
2. **No view-layer arithmetic** — an ESLint rule bans `* / %` and `Number()/parseFloat/parseInt`
   inside `src/pages/**` (the rule covers `pages/` only; `src/charts/**` is intentionally exempt —
   it does pre-aggregated drawing geometry, never a displayed figure). Displayed values come
   verbatim from the JSON; charts render the verbatim segment value and draw only pre-aggregated
   `synthesis.charts[]` geometry. The Current-state page wires the chart subsystem
   (`DonutChart`/`BarChart`), guarded by `charts.length` — it lights up automatically once the
   engine bakes charts (`synthesis.charts[]` is empty in both shipped domains today).
3. **Planning isolation** — `planning_assumptions` render only through `<PlanningBadge>` /
   `<PlanningRow>` (the dashed-amber badge mirroring the print suite), and have their own
   first-class `/assumptions` ledger route.
4. **Validation** — one zod schema validates the JSON at load; a contract mismatch shows a
   "data contract changed" banner instead of a blank screen.

## Honest scope

Three features are intentionally constrained to what the data can back without inference:

- **Traceability** is a read-only matrix — its rows are narrative summaries with no machine ids,
  so cells are not deep-linked (linking would require fuzzy text matching = a mis-link risk).
- **Roadmap** items are not linked to specific opportunities — the source `opportunity_id` is not
  yet populated; `depends_on` shows as labelled notes.
- The **opportunity portfolio** uses a quadrant priority board (grouped by `matrix_quadrant`),
  not a value×feasibility scatter — the scores barely vary, so a scatter would imply false
  precision.

Each upgrades automatically if a future pipeline bake populates the missing ids/scores.
