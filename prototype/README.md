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
prototype/
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

## Setup (uv-based)

```bash
cd prototype
uv sync                 # creates .venv and installs deps + dev tools (pytest, pyrefly)
cp .env.example .env    # then add your ANTHROPIC_API_KEY (or the Azure vars)
uv run python scripts/doctor.py          # verify provider connectivity
```

## Usage (once creds are set)

```bash
uv run python run.py --domain o2c                  # live run (generates everything live)
uv run python run.py --domain o2c --auto-resolve   # non-interactive
uv run python run.py --domain o2c --use-fixture    # use the pre-built O2C fixture (demo-safe)
uv run python run.py --domain o2c --golden         # replay a saved run offline
uv run python run.py --domain p2p --auto-resolve   # any other domain — generated live
```

## Dev

```bash
uv run pytest                                   # tests
uv run pyrefly check discovery run.py scripts   # type-check product code
pre-commit install                              # (run from repo root) enable the hooks
```

The output suite opens at `out/<domain>/index.html`.
