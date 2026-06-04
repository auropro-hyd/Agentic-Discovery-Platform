# ──────────────────────────────────────────────────────────────────────────────
# Agentic Discovery Platform — one-command setup & run (Mac / Linux).
#
#   make            # list targets
#   make setup      # Python env (v1/) + explorer deps
#   make run        # OFFLINE demo: golden replay → built explorer → opens it (no key, no cost)
#
# This is a thin wrapper over the cross-platform runner `tasks.py` — ONE source of
# truth, so `make <t>` (here) and `python tasks.py <t>` (Windows) do the same thing.
# Windows users: run `python tasks.py setup` / `python tasks.py run` directly (make
# isn't native on Windows). See the README.
# ──────────────────────────────────────────────────────────────────────────────

SHELL := /bin/bash

# Repo root = this Makefile's dir, resolved via the shell so a path with spaces
# (".../Agentic Discovery Platform") survives. Pick python3, else python.
ROOT := $(shell cd "$(dir $(lastword $(MAKEFILE_LIST)))" && pwd)
PY   := $(shell command -v python3 || command -v python)

# Domain for the convenience targets (override: `make run DOMAIN=p2p`).
DOMAIN ?= o2c

# Every target just forwards to tasks.py with the chosen domain. The runner handles
# the uv/npm invocations, the stale-VIRTUAL_ENV fix, prereq checks, and browser-open.
TASK = "$(PY)" "$(ROOT)/tasks.py"

.DEFAULT_GOAL := help
.PHONY: help setup run live console report ui open doctor test clean distclean

help:
	@if [ -z "$(PY)" ]; then \
	  echo "✗ No Python found on PATH (need python3 or python). Install Python 3.11+."; exit 1; fi
	@$(TASK) help

setup:     ; @$(TASK) setup     --domain $(DOMAIN)
run:       ; @$(TASK) run       --domain $(DOMAIN)
live:      ; @$(TASK) live      --domain $(DOMAIN)
console:   ; @$(TASK) console   --domain $(DOMAIN)
report:    ; @$(TASK) report    --domain $(DOMAIN)
ui:        ; @$(TASK) ui        --domain $(DOMAIN)
open:      ; @$(TASK) open      --domain $(DOMAIN)
doctor:    ; @$(TASK) doctor    --domain $(DOMAIN)
test:      ; @$(TASK) test      --domain $(DOMAIN)
clean:     ; @$(TASK) clean     --domain $(DOMAIN)
distclean: ; @$(TASK) distclean --domain $(DOMAIN)
