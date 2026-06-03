# UI / UX Research & Design Decisions — Autonomous Discovery Platform

**Date:** 2026-06-02
**Purpose:** A standing reference for how users interact with the platform, the design decisions
already made (and *why*), competitor UI patterns worth borrowing, and a recommended target UI.
Anyone picking this up later should be able to understand the UX rationale without re-deriving it.

> Current state: the prototype is **CLI-driven** with a **static HTML report suite** as the output.
> There is no interactive web app yet. This doc covers (1) who uses it and how, (2) the design
> decisions baked into the current output, (3) competitor UI patterns, (4) a target UI proposal.

---

## 1. Who uses it, and how (the user model)

There are **two distinct user roles**, and the UX is deliberately split between them.

### Role A — the AuroPro SME / discovery specialist (the operator)
The person who *runs* the platform. Today this is the CLI. Their job-to-be-done:
1. Point the platform at an engagement's documents (`inputs/<domain>/`).
2. Watch the discovery run — the agent reads the docs and surfaces findings.
3. **Review and resolve** flagged findings (the human-in-the-loop step) — accept, override, or
   route for clarification. This is the trust gate and the basis of the "~80% less stakeholder
   time" story.
4. Generate the client report suite and hand it over.

**Current operator UX (CLI):**
```
python run.py --domain o2c                  # live: agent explores, prints a business-readable feed
python run.py --domain o2c --golden         # replay a saved run instantly (demo-safe)
python run.py --domain o2c --live-synth     # generate report content live (any domain)
python run.py --domain p2p --live-synth     # a brand-new domain, zero config
```
While it runs, the operator sees a **business-language activity feed** (deliberately *not* tool
jargon):
```
The platform is reading your landscape...
   · Reading purchase-order-export…
   · Cross-checking the ERP export against the CRM export on customer id…
   · Breaking down the order records by channel…
   · Searching the procurement policy for: 50,000, second approval, Maverick spend…
   · Pulling the findings together…
```
This feed is a UX decision in itself (see §2.4): the ~60–90s live run becomes *watchable* and reads
as genuine investigation rather than a frozen terminal.

### Role B — the client stakeholder (Head of Strategy / transformation lead) (the reader)
They **never operate the platform**. They receive the **6-report HTML suite** and read it. Their
job-to-be-done: understand current state, see the quantified pain points and opportunities, and
decide whether to commit to a pilot/engagement. They care about decisions and credibility, not how
the agent works — hence the strict "no platform jargon" language rule.

### The hand-off flow (end to end)
```
SME runs discovery ──▶ agent surfaces findings ──▶ SME reviews/resolves (HITL)
        │                                                       │
        ▼                                                       ▼
  activity feed (operator)                         6-report suite generated
                                                              │
                                                              ▼
                                            client opens out/<domain>/index.html
                                            (sidebar nav across the 6 reports)
```

---

## 2. Design decisions already made (and why)

These are deliberate and should be preserved in any future UI.

### 2.1 Two surfaces, two languages
- **Operator surface** can show mechanism (which file, which computation) — it's internal.
- **Client surface** must use **business language only**. Banned on-screen: pipeline, agent (except
  the named "AI Agent" solution pattern), block, knowledge graph, join/group_by/aggregate, column
  names, filenames, locators. Enforced by an `assert_no_leaks()` guard that **fails the build** if
  any leak reaches a client report. *Why:* the audience notices jargon subconsciously and it breaks
  the "this understands my business" effect.

### 2.2 The 6-report suite (client-facing information architecture)
A left **sidebar nav** + content pane; six standalone, linkable reports:
| # | Report | Role |
|---|---|---|
| 01 | Current State Assessment | Factual baseline — **no** red/amber flags, no diagnostic words (enforced) |
| 02 | Pain Points & Opportunities | Ranked issues, each mapped to an opportunity |
| 03 | Transformation Recommendation | **Value vs. Feasibility 2×2 matrix** + sequencing |
| 04 | **AI Opportunity Portfolio** | **The centrepiece** — per opportunity: Before/After process side-by-side, business impact, integrations, dependencies, risks |
| 05 | Transformation Roadmap | 3 horizons (0–6 / 6–18 / 18+ months) |
| 06 | Supporting Artefacts | Source-document index = the **audit trail** (the only place doc names are tabulated) |

*Why a suite, not one doc:* mirrors how consultancies package deliverables; lets the client navigate
to what they care about; makes the Opportunity Portfolio feel like the product.

### 2.3 Confidence & provenance, shown the right way
- **Provenance** is shown in business language: "Where this comes from: your ERP and CRM customer
  exports, read against your Credit Management Policy." Never a tool name or filename.
- **Numbers are grounded** — every figure traces to data the tools actually computed; a grounding
  gate rejects any number that doesn't. The full technical trace lives in an internal JSON, and
  Report 06 notes it's "available to your data team on request."
- **Report 01 carries no status colours** — current state is stated as fact; judgement lives in
  Pain Points / Opportunities. *Why:* a current-state doc full of red flags reads as an accusation;
  separating fact from judgement is more credible.

### 2.4 The live activity feed (operator drama)
The live run prints a business-readable line per tool call. *Why:* a ~78s live agent run is a long
silent wait otherwise; the feed turns it into a visible "watch it investigate" moment — the core of
the demo's "three months in twelve minutes" story. A `--golden` replay renders instantly as a
safety net if the live call stalls on stage.

### 2.5 Visual language (current CSS)
- Dark slate left sidebar (`#0f1b2d`), light content pane, **one calm accent** (`#1f6feb`).
- **No red/amber/green status colours anywhere** — deliberately avoids an "alarm dashboard" feel;
  emphasis is done with the single blue accent and weight, not alarm colours.
- Before/After rendered as a **2-column grid** (`.ba-grid`): grey left border = before, blue left
  border = after; failure points are muted amber inline chips.
- Value/Feasibility **2×2 as a CSS grid**; "Do First" quadrant gets a soft blue tint (emphasis, not
  alarm). Print + mobile media queries included.
- Self-contained HTML + one CSS file, no external/CDN dependencies → opens offline on a laptop in
  any browser (demo-safe).

### 2.6 Client name handling (recent decision)
Reports infer the client/organisation name from the documents when it recurs confidently; otherwise
they show **no name** and read cleanly (sidebar shows the engagement, e.g. "Order-to-Cash
Discovery") rather than a placeholder. A manifest field can override. *Why:* never show a wrong or
awkward placeholder name to a client.

---

## 3. Competitor UI patterns worth borrowing

(Cross-reference the market dossiers in `research/` for the full competitive picture. This section
is specifically about *interface* patterns.)

| Pattern | Who does it well | Why borrow it |
|---|---|---|
| **Process map as the hero visual** | Celonis, SAP Signavio | A visual as-is process graph is instantly legible to ops audiences. ✅ **BUILT (2026-06-02):** a self-contained inline-SVG process-flow diagram (connected step nodes with actor+system, wrapping arrows) now renders at the top of Report 01 and in Supporting Artefacts — closing this gap vs Celonis/Signavio. See `screenshots/o2c-01-current-state.png`. |
| **Value/effort 2×2 prioritisation** | LeanIX, most EA tools, strategy decks | Universally understood by execs. We already render this (Report 03) — keep it prominent. |
| **Fact Sheet / object drill-down** | SAP LeanIX | Click an application/process → a structured detail card. Maps to our opportunity cards; a future UI could make each finding/opportunity a drill-down. |
| **Cited answer with source links** | Glean | Every answer references its source docs, builds trust. We do this in prose ("Where this comes from…"); a UI could make sources clickable to the exact document/row. |
| **Confidence/severity tiering** | Cyera, security posture tools | Visible confidence badges. We deliberately keep these *off* the client current-state report but use them in the operator view — keep that split. |
| **Roadmap as a horizon timeline / Gantt** | LeanIX roadmaps, PPM tools | Our roadmap is a 3-horizon list; a light timeline visual would read better for execs. |
| **Live "agent working" trace** | newer agentic tools (e.g. agent UIs) | Showing the agent's steps builds trust in autonomy. Our CLI activity feed is the seed of this — a web version (a streaming step list) is high-value for the demo. |

**Anti-patterns to avoid (from competitor criticism — see gap dossiers):**
- **Dashboard overload / "sea of red"** — common complaint about APM & process-mining dashboards.
  Our calm, no-alarm-colour, narrative-led suite is a deliberate counter-position.
- **Black-box outputs** — buyers distrust numbers with no derivation. Our provenance/grounding is a
  differentiator; surface it, don't hide it.
- **Setup-heavy, data-engineering-first UX** — process mining needs clean event logs first; we
  should keep "point it at messy docs and go" as the headline UX.

---

## 4. Recommended target UI (forward-looking)

A thin web app over the existing engine. Priority order reflects demo value vs. build cost.

### 4.1 MVP web UI (highest demo value)
1. **Upload / select documents** — drag a folder of docs; show them as readable cards (using the
   derived friendly names, never raw filenames).
2. **Live discovery view** — stream the business-language activity feed (§2.4) as the agent runs;
   a progress sense without exposing tool internals. This is the "watch it work" moment.
3. **Findings review (the SME copilot)** — each finding as a card: title, plain-language
   description, the numbers (with provenance), 2–3 candidate resolutions, and Accept / Override /
   Route actions. This makes the human-in-the-loop tangible (today it's a CLI prompt).
4. **Report suite viewer** — the existing 6-report HTML, embedded with the sidebar nav. Already
   built; just host it.

### 4.2 Phase 2
- **Clickable provenance** — click a number → highlight the source row/quote in the document.
- **Process flow diagram** — auto-rendered from the current-state process steps (hero visual).
- **Roadmap timeline** — horizon Gantt.
- **Two-tray copilot** — separate "blocking gaps" vs "strategic tensions" review queues (matches
  the original platform design).

### 4.3 Explicitly out of scope (keep the UX honest)
- No editable dashboards / BI-style slice-and-dice — that's the process-mining/APM lane and not our
  wedge. We are a *discovery accelerator that produces a defensible deliverable*, not a monitoring
  tool. Keep the UX deliverable-centric.

### 4.4 Design principles to carry into any UI
1. Operator surface may show mechanism; **client surface never does** (jargon guard stays).
2. Calm, narrative, no alarm-colour dashboards.
3. Every number clickable to its source (provenance as a first-class, visible feature).
4. The agent's investigation is **shown** (trust through transparency of process, not of jargon).
5. Works offline, self-contained (demo resilience).

---

## 5. Current-state visual reference

The shipped report suite renders as: a fixed dark sidebar (engagement / client name + 6 numbered
nav links) beside a white content pane. Report 04 shows each opportunity as a card with a
two-column Before/After process grid; Report 03 shows the 2×2 matrix as a tinted grid of quadrant
boxes with opportunity chips. To view: open `prototype/out/<domain>/index.html` in a browser.

**Screenshots** (captured 2026-06-02 via headless Chrome, in `research/screenshots/`):
- `o2c-01-current-state.png` — factual baseline, process-flow table, no status colours
- `o2c-03-recommendation.png` — the Value/Feasibility 2×2 matrix + opportunity ratings
- `o2c-04-opportunity-portfolio.png` — **the centrepiece**: opportunity cards with Before/After
  two-column layout, blue metric chips (e.g. €600,000), pattern badges (HITL Workflow / Automation
  Pipeline / AI Agent), business-language provenance lines
- `o2c-06-supporting-artefacts.png` — source-document index (the audit trail)

To regenerate screenshots:
```
"/Applications/Google Chrome.app/Contents/MacOS/Google Chrome" --headless --disable-gpu \
  --window-size=1280,1600 --screenshot=research/screenshots/o2c-04.png \
  "file://$PWD/prototype/out/o2c/04-opportunity-portfolio.html"
```
The CSS lives in `prototype/discovery/reportsuite/assets.py`.

---

*Related research:* see the market/competitor dossiers in this `research/` folder for capability,
pricing, and gap analysis that informs the competitive-UI section above.
