# ──────────────────────────────────────────────────────────────────────────────
# Agentic Discovery Platform — one-command setup & run for first-timers.
#
#   git clone … && cd Agentic-Discovery-Platform
#   make            # prints this help
#   make setup      # install everything: Python env (v1) + explorer node_modules
#   make run        # OFFLINE demo: golden replay → built explorer → opens it
#
# The default `run` needs NO API key and spends NO credits (golden replay). Add a
# key only for `make live`. See `make help` for the full list.
#
# Why a Makefile: the engine lives in v1/ (uv-managed Python) and the UI in
# explorer/ (npm). This drives both from the repo root so nobody has to remember
# the cd's, the flags, or which env to activate.
# ──────────────────────────────────────────────────────────────────────────────

# Run every recipe line in one shell so `&&`/multi-line logic behaves, and fail loudly.
.ONESHELL:
SHELL := /bin/bash
.SHELLFLAGS := -eu -o pipefail -c

# Absolute repo root — the directory this Makefile lives in. Resolved via the shell
# (not make's $(dir)/$(abspath), which collapse spaces) so a path like
# ".../Agentic Discovery Platform" survives intact.
ROOT := $(shell cd "$(dir $(lastword $(MAKEFILE_LIST)))" && pwd)
V1   := $(ROOT)/v1
UI   := $(ROOT)/explorer

# Which domain the convenience targets operate on (override: `make run DOMAIN=p2p`).
DOMAIN ?= o2c

# uv reads an inherited VIRTUAL_ENV and warns/misbehaves if it points elsewhere
# (this is exactly the "VIRTUAL_ENV does not match .venv" warning from a fresh
# clone where a different project's venv is still active). Pin uv to v1/ and drop
# the stray VIRTUAL_ENV so it always targets v1/.venv.
# NB: $(V1) is quoted everywhere — the repo path can contain spaces.
UV := cd "$(V1)" && env -u VIRTUAL_ENV uv

.DEFAULT_GOAL := help

# ── Help ──────────────────────────────────────────────────────────────────────
.PHONY: help
help:
	@echo ""
	@echo "  Agentic Discovery Platform — make targets"
	@echo "  ─────────────────────────────────────────"
	@echo "  make setup     Install everything (Python env in v1/ + explorer deps)."
	@echo "  make run       OFFLINE demo: golden replay + build UI + open it. No API key, no cost."
	@echo "  make live      LIVE run: real agent pipeline (needs ANTHROPIC_API_KEY; spends credits)."
	@echo "  make console   Start the Discovery Console (backend + UI dev server) for the live flow."
	@echo ""
	@echo "  make report    (Re)generate the golden report suite for a domain → v1/out/<domain>/."
	@echo "  make ui        Build the explorer SPA into explorer/dist/."
	@echo "  make open      Open the most recently built report suite in your browser."
	@echo "  make doctor    Check that your API provider/credentials are wired (one tiny call)."
	@echo "  make test      Run the Python test suite + type-check."
	@echo "  make clean     Remove generated build output (dist/, __pycache__) — keeps env + golden."
	@echo "  make distclean Also remove the venvs and node_modules (full reset)."
	@echo ""
	@echo "  Vars:  DOMAIN=o2c|p2p   (default: $(DOMAIN))"
	@echo "  First time?  →  make setup && make run"
	@echo ""

# ── Prerequisite checks (clear message instead of a cryptic 'command not found') ─
.PHONY: check-uv check-node
check-uv:
	@command -v uv >/dev/null 2>&1 || { \
	  echo "✗ 'uv' is not installed (the Python package/venv manager)."; \
	  echo "  Install it:  curl -LsSf https://astral.sh/uv/install.sh | sh"; \
	  echo "  then restart your shell and re-run 'make setup'."; \
	  exit 1; }

check-node:
	@command -v npm >/dev/null 2>&1 || { \
	  echo "✗ 'npm' is not installed (needed to build the explorer UI)."; \
	  echo "  Install Node.js 20+ from https://nodejs.org  (or: brew install node)"; \
	  exit 1; }

# ── Setup ───────────────────────────────────────────────────────────────────────
.PHONY: setup setup-py setup-ui
setup: setup-py setup-ui
	@echo ""
	@echo "✓ Setup complete. Next:  make run   (offline demo — no API key needed)"

setup-py: check-uv
	@echo "→ Python: creating v1/.venv and installing deps (this can take a minute)…"
	$(UV) sync
	@# Seed .env from the template so `make live`/`make doctor` have somewhere to put a key.
	@if [ ! -f "$(V1)/.env" ]; then \
	  cp "$(V1)/.env.example" "$(V1)/.env"; \
	  echo "→ Created v1/.env from the template. Add your ANTHROPIC_API_KEY there for live runs."; \
	fi
	@echo "✓ Python environment ready."

setup-ui: check-node
	@echo "→ Explorer: installing node_modules…"
	@cd "$(UI)" && npm install
	@echo "✓ Explorer dependencies ready."

# ── The default first-timer path: offline, deterministic, free ───────────────────
.PHONY: run
run: report ui
	@echo ""
	@echo "✓ Offline demo ready for '$(DOMAIN)'."
	@echo "  • Report suite:  v1/out/$(DOMAIN)/index.html"
	@echo "  • Explorer SPA:  explorer/dist/index.html"
	@$(MAKE) --no-print-directory open

# Golden replay = the saved run, rendered offline. No network, no key, no cost — this
# is why it's the default and why it can't hit the "no cached response" wall.
.PHONY: report
report: check-uv
	@echo "→ Rendering the golden report suite for '$(DOMAIN)' (offline replay)…"
	$(UV) run python run.py --domain $(DOMAIN) --golden --auto-resolve

# Build the explorer SPA. Its prebuild step syncs the latest v1/out/discovery-*.json
# into the bundle, so the UI always reflects the report data just generated.
.PHONY: ui
ui: check-node
	@echo "→ Building the explorer SPA…"
	@cd "$(UI)" && npm run build
	@echo "✓ Explorer built → explorer/dist/"

# ── Live pipeline (real agent; needs credentials; spends credits) ────────────────
# Lightweight provider-aware credential check (no network call — that's `make doctor`).
# Accepts EITHER a real Anthropic key OR the full Azure var set, matching .env.example.
.PHONY: live
live: check-uv
	@env="$(V1)/.env"; \
	  has_anthropic=$$(grep -Eq '^[[:space:]]*ANTHROPIC_API_KEY=sk-[A-Za-z0-9_-]{20,}' "$$env" 2>/dev/null && echo 1 || echo 0); \
	  has_azure=$$(grep -Eq '^[[:space:]]*AZURE_OPENAI_API_KEY=.+' "$$env" 2>/dev/null \
	             && grep -Eq '^[[:space:]]*AZURE_OPENAI_ENDPOINT=https' "$$env" 2>/dev/null && echo 1 || echo 0); \
	  if [ "$$has_anthropic" = 0 ] && [ "$$has_azure" = 0 ]; then \
	    echo "✗ No usable provider credentials in v1/.env."; \
	    echo "  A live run calls the agent and spends credits. Add ONE of:"; \
	    echo "    • ANTHROPIC_API_KEY=sk-…                    (default provider), or"; \
	    echo "    • the AZURE_OPENAI_* vars                   (Azure provider)."; \
	    echo "  Then verify with 'make doctor' and re-run 'make live'."; \
	    echo "  (For a free, no-key demo instead, run 'make run'.)"; \
	    exit 1; \
	  fi
	@echo "→ LIVE run for '$(DOMAIN)' — this takes minutes and spends API credits…"
	$(UV) run python run.py --domain $(DOMAIN) --fresh --auto-resolve

# ── Discovery Console (backend + UI dev server) for the interactive 6-stage flow ──
# Starts server.py (port 8742) in the background, then the Vite dev server in the
# foreground. Ctrl-C stops the dev server and tears the backend down with it.
.PHONY: console
console: check-uv check-node
	@echo "→ Starting Discovery Console backend on http://127.0.0.1:8742 …"
	@$(UV) run python server.py & echo $$! > /tmp/discovery-server.pid
	@trap 'kill $$(cat /tmp/discovery-server.pid) 2>/dev/null || true; rm -f /tmp/discovery-server.pid' EXIT INT TERM; \
	  echo "→ Starting the explorer dev server (Ctrl-C to stop both)…"; \
	  cd "$(UI)" && npm run dev

# ── Operator utilities ───────────────────────────────────────────────────────────
.PHONY: doctor open test
doctor: check-uv
	@echo "→ Checking provider connectivity (makes one tiny live call)…"
	$(UV) run python scripts/doctor.py

open:
	@f="$(V1)/out/$(DOMAIN)/index.html"; \
	if [ -f "$$f" ]; then \
	  ( command -v open >/dev/null 2>&1 && open "$$f" ) || \
	  ( command -v xdg-open >/dev/null 2>&1 && xdg-open "$$f" ) || \
	  echo "Open this in a browser: $$f"; \
	else \
	  echo "No report yet for '$(DOMAIN)'. Run 'make report' (or 'make run') first."; \
	fi

test: check-uv
	@echo "→ Running the Python test suite + type-check…"
	$(UV) run pytest
	$(UV) run pyrefly check discovery run.py scripts

# ── Cleanup ────────────────────────────────────────────────────────────────────
.PHONY: clean distclean
clean:
	@echo "→ Removing generated build output (keeps env, golden, and reports)…"
	@rm -rf "$(UI)/dist"
	@find "$(V1)" -type d -name __pycache__ -prune -exec rm -rf {} + 2>/dev/null || true
	@echo "✓ Clean."

distclean: clean
	@echo "→ Full reset: removing v1/.venv and explorer/node_modules…"
	@rm -rf "$(V1)/.venv" "$(UI)/node_modules"
	@echo "✓ Done. Re-run 'make setup' to rebuild."
