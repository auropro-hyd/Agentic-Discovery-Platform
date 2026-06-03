# Contributing

## Setup

```bash
cd prototype
uv sync                       # env + deps (runtime + dev: pytest, pyrefly)
cp .env.example .env          # add ANTHROPIC_API_KEY (or the Azure vars)
uv run python scripts/doctor.py   # verify provider connectivity
pre-commit install            # (from repo root) enable hooks
```

## Workflow

`main` is protected — **no direct pushes**. All changes go through a PR:

1. Branch: `feat/…`, `fix/…`, or `chore/…`
2. Make the change; keep client-facing output free of jargon and ungrounded numbers
   (the grounding gate + no-leak guard enforce this).
3. Before pushing:
   ```bash
   cd prototype
   uv run pytest
   uv run pyrefly check discovery run.py scripts
   ```
4. Open a PR. CI (tests + type check) must pass and a CODEOWNER must approve before merge.

## Conventions

- Commits: short imperative subject (`fix: …`, `feat: …`, `chore: …`).
- Type-check the **product code** (`discovery/`, `run.py`, `scripts/`); test fixtures are
  intentionally loosely typed and excluded from the pyrefly hook.
- Don't commit secrets (`.env`) or the LLM cache (`prototype/.cache/`).

## Where things live

| Path | What |
|---|---|
| `prototype/` | the discovery engine + 6-report suite (the product) |
| `prototype/docs/` | internal design specs + verified numbers |
| `research/` | market/competitor + UI research |
| `shared_context/` | local-only received material (gitignored) |
