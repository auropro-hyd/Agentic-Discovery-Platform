# Discovery Explorer

An interactive, client-facing web companion to the AuroPro discovery report suite — the
**explorable** version of the static print/PDF deliverable. Same grounded data, same navy/blue
identity, but you can cross-link pain points ↔ opportunities, filter and sort the opportunity
portfolio, browse the evidence and fact store, read the planning-assumptions ledger, and search
the whole suite.

It is a **React + Vite + TypeScript** single-page app. It ships as static files (no server at view
time): the built `dist/` opens from any static host or directly from `file://`, with deep-linkable
hash URLs (`#/o2c/opportunities/OPP1`).

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
   inside `src/pages/**`. Displayed values come verbatim from the JSON; charts draw only
   pre-aggregated `synthesis.charts[]` segments.
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
