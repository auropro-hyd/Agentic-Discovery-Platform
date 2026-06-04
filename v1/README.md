# Automated Discovery Prototype

A lean, CLI-first prototype of the AuroPro automated discovery pipeline for the Opella demo.

It ingests a folder of synthetic business documents, extracts a lightweight knowledge
model, cross-references claims across documents to surface **contradictions and gaps**,
lets an **SME resolve** each flagged item against the source documents, and emits a
**discovery report** (Markdown + HTML).

The design priority is **the output and consistency**, not the architecture. It is a
linear, manual pipeline — no orchestrator. Cost is not a constraint; time and a
consistent, trustworthy output are.

## Why it is built this way (decisions)

- **Not autonomous.** Findings are flagged for a human SME, who resolves them against
  source documents. This human-in-the-loop step is the trust mechanism and the basis of
  the "~80% less stakeholder effort" story.
- **Provenance first.** Every finding and recommendation cites the source document(s) it
  came from. Confidence is grounded in *evidence*, not the model's self-reported certainty.
- **Deterministic + golden fallback.** Runs live at temperature 0 with pinned prompts and
  on-disk caching. A pre-baked "golden" run can render instantly if a live call wobbles.
- **Domain-agnostic.** O2C and Demand Planning are just different `inputs/<domain>/`
  folders plus a small domain config.

## Pipeline

```
inputs/<domain>/*        classify → extract → cross-reference → flag → resolve → report
                         (1)        (2)        (3)               (4)    (5)       (6)
out/report.md + out/report.html
```

## Layout

```
v1/
  discovery/            # the package (pipeline stages, models, llm client, report suite)
  inputs/<domain>/      # input docs for a domain (gitignored — local synthetic/client data)
  golden/<domain>/      # pre-baked golden run for the safe offline replay (gitignored)
  out/                  # generated reports (gitignored)
  .cache/               # per-call LLM response cache, deterministic replay (gitignored)
  tests/                # Gate-A tools, agent-loop, suite, leak tests + smoke_test.py
  scripts/              # operator utilities — doctor.py (provider/credential connectivity check)
  run.py                # CLI entrypoint
  docs/                 # internal design record:
                        #   DESIGN_SPEC_o2c_discovery.md  — discovery engine spec
                        #   DESIGN_SPEC_report_suite.md   — 6-report suite spec
                        #   INPUT_CONTRACT.md             — expected shape of input docs
                        #   VERIFIED_NUMBERS.md           — independently verified O2C figures
```

## Setup

**Easiest — from the repo root** (drives this engine + the explorer; no key needed for the demo):

```bash
make setup && make run                 # macOS / Linux
python tasks.py setup && python tasks.py run   # Windows (or anywhere; identical behaviour)
```

`run` is an offline **golden replay** — no credentials, no cost. See the root [README](../README.md#quickstart).

**Engine only (uv-based, from `v1/`):**

```bash
cd v1
uv sync                 # creates .venv and installs deps + dev tools (pytest, pyrefly)
cp .env.example .env    # only needed for LIVE runs — add your ANTHROPIC_API_KEY (or the Azure vars)
uv run python scripts/doctor.py          # (live only) verify provider connectivity
```

## Usage

**Offline demo (no key, no cost) — start here:**

```bash
uv run python run.py --domain o2c --golden --auto-resolve   # replay the saved run offline → out/o2c/
```

**Live runs (generate everything live — need credentials in `v1/.env`):**

```bash
uv run python run.py --domain o2c                  # live run (interactive SME resolve)
uv run python run.py --domain o2c --auto-resolve   # non-interactive
uv run python run.py --domain o2c --use-fixture    # pre-built O2C fixture — the full reference-depth suite
uv run python run.py --domain o2c --refresh        # diff against the previous run (new/resolved/changed)
uv run python run.py --domain o2c --no-verify      # skip the adversarial verification pass
uv run python run.py --domain p2p --auto-resolve   # any other domain — generated live
```

> **Live runs preflight your credentials.** If `v1/.env` has no real key (or still has the
> `.env.example` `sk-ant-...` placeholder), the run stops immediately with a one-line fix and a
> pointer to `--golden` — instead of a traceback or a misleading "no cached response" message.
> The on-disk `.cache/` is gitignored, so a fresh clone has nothing to replay *live*; the committed
> `golden/` is what `--golden` replays.

> **Reference-depth O2C suite.** `--use-fixture` renders the hand-grounded O2C fixture — the full
> reference-grade suite (per-report cover + own TOC, the channel-mix / lead-time / credit-band /
> collections / EDI-connection / top-account tables, the five pain-point detail tables, the evidence
> register, success-metrics, risk register and traceability matrix). Every figure traces to the raw
> CSVs / source documents and passes the grounding gate. The live path emits the core suite today;
> mining the corpus into these structured sections from the live agent is a planned follow-up, so
> richer depth flows automatically for any domain.

Findings are variable in number and ranked by impact; each is adversarially **verified** (a
challenged finding is flagged for review, not dropped); the agent can **conformance-check** a
documented rule against the data; every report number **links to its source**; and `--refresh`
diffs a re-run against the prior one. New domain: drop docs in `inputs/<domain>/` and run.

## Dev

```bash
uv run pytest                                   # tests
uv run coverage run -m pytest && uv run coverage report   # tests + coverage (active pipeline = 100%)
uv run pyrefly check discovery run.py scripts   # type-check product code
pre-commit install                              # (run from repo root) enable the hooks
```

The active discovery pipeline is held at **100% statement + branch coverage** (enforced in CI via
`fail_under = 100` in `.coveragerc`). The scope deliberately omits the real HTTP LLM client and the
legacy scripted/linear modules — those are exercised by the live run, not offline unit tests.

The output suite opens at `out/<domain>/index.html`.
