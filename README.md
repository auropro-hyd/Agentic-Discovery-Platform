# Agentic Discovery Platform

> An AuroPro consulting accelerator. Point an LLM agent at an enterprise's messy business
> documents; it **discovers** the contradictions, undocumented processes, and control gaps — then
> produces a client-ready report suite. Runs on **any domain** with zero config.

<sub>Internal / proprietary · `v1/` = the engine · `research/` = market & UI analysis</sub>

---

## How it works

```mermaid
flowchart TB
    D["📂 Business documents<br/><small>SOPs · policies · RACIs · system exports · working notes</small>"]

    subgraph DISCOVER["① Discover — live agent loop"]
      direction TB
      A["Read &amp; classify each document"]
      T{{"Generic tools<br/><small>describe · group_by · join_diff<br/>filter_count · find_mentions</small>"}}
      X["Cross-reference<br/><small>documented process vs. actual data</small>"]
      A --> T
      T -- "code computes the numbers" --> X
      X -- "more evidence needed" --> T
      X --> F["Findings<br/><small>contradictions · gaps · unowned processes</small>"]
    end

    subgraph REVIEW["② Verify"]
      G{"Grounding gate<br/><small>every number traces to a tool result</small>"}
      H["👤 SME review (HITL)<br/><small>accept · override · route</small>"]
      G -- "ungrounded → rejected" --> A
      G -- "grounded" --> H
    end

    subgraph DELIVER["③ Deliver"]
      S["Synthesis<br/><small>pain points · opportunities · roadmap</small>"]
      C["Confidence + provenance tiering<br/><small>cite source docs, business language only</small>"]
      R["📑 6-report client suite<br/><small>HTML + Markdown</small>"]
      S --> C --> R
    end

    D --> A
    F --> G
    H --> S

    %% high-contrast: dark text on light fills (readable in light & dark themes)
    classDef src     fill:#dbe4f3,stroke:#33425b,stroke-width:1.5px,color:#11161f;
    classDef agent   fill:#cfe0ff,stroke:#1f4fa3,stroke-width:1.5px,color:#0a1f44;
    classDef gate    fill:#ffe6b3,stroke:#9a6a00,stroke-width:1.5px,color:#3d2a00;
    classDef human   fill:#e8d8ff,stroke:#6a3bb0,stroke-width:1.5px,color:#2a124d;
    classDef out     fill:#c9efd6,stroke:#1b7a45,stroke-width:1.5px,color:#0a2f1a;

    class D src;
    class A,T,X,F agent;
    class G gate;
    class H human;
    class S,C,R out;
```

**The agent reasons; code does the math.** It loops over deterministic tools to compute over the
data, so every figure is exact and traceable — never an LLM guess. The grounding gate bounces any
ungrounded number back to the agent; an SME reviews findings before they become a deliverable.

---

## The output: a 6-report suite

| # | Report | Role |
|---|--------|------|
| 01 | Current State Assessment | Factual baseline + process-flow diagram (no judgements) |
| 02 | Pain Points & Opportunities | Issues ranked by impact, each → an opportunity |
| 03 | Transformation Recommendation | Value vs. feasibility 2×2 + sequencing |
| 04 | **AI Opportunity Portfolio** | **Centrepiece** — before/after per opportunity |
| 05 | Transformation Roadmap | Three horizons |
| 06 | Supporting Artefacts | System/data-flow map + source-document index (audit trail) |

---

## Design decisions (the why, in one line each)

- **Code does the math, the agent reasons** → numbers are exact & consistent across runs, never hallucinated.
- **Grounding gate** → a finding's every number must trace to a tool result, or it's rejected.
- **No platform jargon in client output** → a leak guard fails the build if tool names/filenames slip in.
- **Confidence by provenance, not self-report** → findings cite the documents they rest on.
- **Live by default, any domain** → report content is generated per run; an O2C fixture exists only as a demo-safe fallback.
- **Client-agnostic** → no org name unless detected from the docs; a run can suppress it.
- **Human-in-the-loop SME review** → the trust step and the basis of the "less stakeholder time" story.

Full rationale: [`v1/docs/`](v1/docs/) · competitive positioning: [`research/`](research/).

---

## Quickstart

First time on this repo? Two commands from the root — **no API key, no cost**.

**Prerequisites:** [`uv`](https://docs.astral.sh/uv/getting-started/installation/) (Python env manager)
and [Node.js 20+](https://nodejs.org) (`npm`). The setup step tells you if either is missing.

**macOS / Linux:**
```bash
make setup      # Python env (v1/) + explorer deps
make run        # OFFLINE demo: golden replay → builds the explorer → opens the report suite
```

**Windows** (`make` isn't native — use the cross-platform runner; identical behaviour):
```powershell
python tasks.py setup
python tasks.py run
```

`run` is a deterministic **golden replay** (the saved run, rendered offline), so it needs no
credentials and can't hit the "no cached response" wall. Run `make` (or `python tasks.py`) with no
target to list every task.

Want a **live** run (real agent, spends credits)? Add a key first:

```bash
# put ANTHROPIC_API_KEY=… (or the AZURE_OPENAI_* vars) in v1/.env — setup seeds it from the template
make doctor     # (or: python tasks.py doctor)  — verify the provider is reachable (one tiny call)
make live       # the real pipeline — minutes, costs credits
```

> A live run **preflights your credentials**: if `v1/.env` has no real key (or still has the
> `.env.example` placeholder), it stops immediately with a one-line fix instead of a traceback or a
> misleading "use the golden run" message. With no key, use `make run` for the full offline demo.

**Interactive Console** — the 6-stage operator flow with both servers running and the explorer
embedded (`make console` / `python tasks.py console`). It starts the backend (`:8742`) and the
explorer dev server together, **opens the app in your browser**, and keeps both running until you
Ctrl-C (which stops both). No key needed — if no report data exists yet it renders the offline
golden suite first; a live run is then a choice inside the Console UI.

Run on any domain by dropping its documents in `v1/inputs/<domain>/`, then
`make run DOMAIN=<slug>` (or `python tasks.py run --domain <slug>`).

<details><summary>Manual equivalent (no make / no tasks.py)</summary>

```bash
cd v1
uv sync                                   # env + deps
cp .env.example .env                      # add ANTHROPIC_API_KEY (or Azure vars) for live runs
uv run python run.py --domain o2c --golden --auto-resolve   # offline demo → opens out/o2c/index.html
uv run python scripts/doctor.py           # (live only) check connectivity
uv run python run.py --domain o2c --auto-resolve            # live run (needs a key)
```
</details>

## Develop

```bash
uv run pytest                                   # tests
uv run pyrefly check discovery run.py scripts   # type-check product code
pre-commit install                              # enable hooks
```

`main` is protected — changes go through a PR with passing CI. See [CONTRIBUTING.md](CONTRIBUTING.md).

## Layout

```
v1/      discovery engine + 6-report suite, tests, scripts, design docs
research/        market/competitor dossiers + UI/UX research (+ screenshots)
shared_context/  received engagement material (local only, gitignored)
```
