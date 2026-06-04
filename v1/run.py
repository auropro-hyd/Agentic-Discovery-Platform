#!/usr/bin/env python3
"""AuroPro automated discovery prototype — CLI entrypoint.

Two run paths (both call the SAME generic tools on the SAME data, so numbers are identical):
  --agent     The agent freely calls tools to DISCOVER the findings (the "show").
  --scripted  Fixed tool trajectory + one synthesis call (the "tell"). Deterministic.

Default: try the agent, fall back to scripted on any agent-path failure.

Usage:
  python run.py --domain o2c                 # agent, fall back to scripted (interactive resolve)
  python run.py --domain o2c --scripted      # deterministic scripted path only
  python run.py --domain o2c --agent         # agent only (no fallback) — for testing consistency
  python run.py --domain o2c --auto-resolve  # non-interactive SME resolution
  python run.py --domain o2c --golden        # replay cached run (offline, demo-safe)
  python run.py --domain o2c --save-golden   # save this run's cache as the golden fallback

Determinism: temperature 0 + full-history cached LLM calls + deterministic tools.
"""
from __future__ import annotations

import argparse
import json
import os
import shutil
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT))

from discovery import agent_loop, assemble, docnames, env, loader, refresh, registry, report, resolve, scripted, tools, verify  # noqa: E402
from discovery.llm import LLMClient, LLMError  # noqa: E402
from discovery.reportsuite import build  # noqa: E402
from discovery.reportsuite.render import render_suite  # noqa: E402

env.load_env()  # pull v1/.env into os.environ (creds), if present

INPUTS = ROOT / "inputs"
OUT = ROOT / "out"
GOLDEN = ROOT / "golden"


def main(argv=None) -> int:
    os.environ.setdefault("PYTHONHASHSEED", "0")
    ap = argparse.ArgumentParser(description="AuroPro automated discovery prototype")
    ap.add_argument("--domain", required=True)
    mode = ap.add_mutually_exclusive_group()
    mode.add_argument("--agent", action="store_true", help="agent only, no scripted fallback")
    mode.add_argument("--scripted", action="store_true", help="deterministic scripted path only")
    ap.add_argument("--provider", choices=["anthropic", "azure"],
                    help="override DISCOVERY_PROVIDER for this run")
    ap.add_argument("--auto-resolve", action="store_true")
    ap.add_argument("--golden", action="store_true")
    ap.add_argument("--save-golden", action="store_true")
    ap.add_argument("--use-fixture", action="store_true",
                    help="use a domain's pre-built grounded fixture instead of generating the "
                         "report content live (only where a fixture exists, e.g. o2c). Default: "
                         "generate everything live for any domain.")
    ap.add_argument("--no-verify", action="store_true",
                    help="skip the adversarial verification pass over findings")
    ap.add_argument("--refresh", action="store_true",
                    help="diff this run against the previous one for the domain (new/resolved/changed)")
    ap.add_argument("--fresh", action="store_true",
                    help="force a genuinely live run: bypass the LLM read-cache so every call hits "
                         "the provider (slow, costs credits). Results are still cached for replay. "
                         "Mutually exclusive with --golden.")
    args = ap.parse_args(argv)
    if args.provider:
        os.environ["DISCOVERY_PROVIDER"] = args.provider
    if args.fresh and args.golden:
        print("error: --fresh and --golden are mutually exclusive (fresh needs the network).")
        return 2

    domain_dir = INPUTS / args.domain
    if not domain_dir.is_dir():
        print(f"error: no inputs/{args.domain} folder.")
        return 2
    if args.golden:
        _activate_golden_cache(args.domain)
        os.environ["DISCOVERY_OFFLINE"] = "1"
    if args.fresh:
        os.environ["DISCOVERY_NO_CACHE"] = "1"
        print("  (fresh run: bypassing the LLM cache — this will take minutes and spend credits)")

    print(f"Reading the {args.domain} landscape...")
    manifest = loader.load_manifest(domain_dir) or {}
    domain_label = str(manifest.get("domain_label") or args.domain.replace("_", " ").title())
    reg = registry.setup_domain(domain_dir, freeze=True)
    documents = loader.load_domain(domain_dir)   # for the report's "inputs read" section
    narrative_text = _narrative_block(reg["doc_ids"])
    print(f"  {len(reg['csv_ids'])} data files, {len(reg['doc_ids'])} documents.")

    llm = LLMClient()

    # ---- discover findings (agent or scripted, with failover) -------------
    payload, path_used = _discover(llm, args, reg, narrative_text, domain_label)
    if payload is None:
        return 1
    print(f"  discovery complete via the {path_used} path; "
          f"{len(payload['findings'])} findings.")

    # ---- discovery refresh: diff this run against the previous one (before overwriting) ----
    refresh_diff = None
    if args.refresh:
        prior_path = OUT / f"discovery-{args.domain}.json"
        if prior_path.exists():
            prior = json.loads(prior_path.read_text()).get("internal_trace", {})
            refresh_diff = refresh.diff_runs(prior, payload)
            print(f"  {refresh.summary_line(refresh_diff)}")
        else:
            print("  refresh: no previous run found — this is the baseline.")

    # ---- adversarial verification (challenge each finding's reasoning) -----
    if not args.no_verify:
        verify.verify_findings(llm, payload, model=None)
        s = verify.verification_summary(payload)
        print(f"  verification: {s['supported']} supported, {s['challenged']} challenged, "
              f"{s['unverified']} unverified")

    # ---- human-in-the-loop SME resolution (optional, on findings) ---------
    result = assemble.to_result(payload, args.domain, domain_label, documents,
                                manifest.get("effort_comparison", {}))
    if not args.golden and not args.auto_resolve and sys.stdin.isatty():
        resolve.resolve_interactive(result.findings)
    elif args.auto_resolve:
        resolve.resolve_auto(result.findings, loader.load_resolutions(domain_dir))

    # ---- client name (generic, client-agnostic engine) — resolve BEFORE building content ----
    #   - detect the org name from the documents (nothing hardcoded);
    #   - an explicit manifest "client" overrides the detection;
    #   - manifest "suppress_client": true => don't name the org on screen (demo): scrub the
    #     detected name from doc-name citations and guard the reports against leaking it.
    # Must run before build_synthesis so the source-doc index / citations honour the noise words.
    detected = docnames.detect_client([tools.DOC_TEXT.get(d, "") for d in reg["doc_ids"]]) or ""
    suppress = bool(manifest.get("suppress_client"))
    if "client" in manifest:
        client = (manifest.get("client") or "").strip()
    elif suppress:
        client = ""
    else:
        client = detected
    # Expand a multi-word detected name into the full phrase PLUS each significant token so a bare
    # token ("Acme" from "Acme Manufacturing") can't leak in prose. Fixed at the SOURCE so BOTH the
    # print render and the SPA sync (which read suppress_names) scrub every variant. Conservative:
    # the full phrase always stays first; we only ADD tokens.
    suppress_names = docnames.expand_suppress_names(detected) if (suppress and detected) else []
    docnames.set_noise_words(suppress_names)
    print(f"  client: {client or '(none — neutral)'}"
          + (f"  [suppressed on screen: {detected}]" if suppress_names else ""))
    # Loud warning for the dangerous case the review surfaced: suppression was REQUESTED but the
    # detector found no name to suppress (it needs >= 3 mentions in >= 2 docs). The org name may
    # still appear once or twice in the LLM-written synthesis prose — so silence here would be a
    # silent confidentiality leak. Flag it so the operator knows protection did NOT engage.
    if suppress and not detected:
        print("  ! WARNING: suppress_client is set but no client name was auto-detected to scrub. "
              "Set an explicit manifest 'client' name, or verify the reports name no organisation.")

    # ---- build the 6-report suite content -----------------------------------------
    # LIVE BY DEFAULT for every domain — the report content is generated from this run's findings.
    # A pre-built fixture is used ONLY when explicitly requested (--use-fixture) AND one exists for
    # the domain; if live fails, we fall back to the fixture only where one exists, else fail
    # honestly (never reuse one domain's fixture for another).
    print("Assembling the report suite...")
    has_fixture = args.domain in build.FIXTURE_DOMAINS
    use_fixture = args.use_fixture and has_fixture
    if args.use_fixture and not has_fixture:
        print(f"  (no fixture exists for '{args.domain}'; generating live instead)")
    reg["manifest"] = manifest          # the deep fan-out reads the StrategyProfile from here
    try:
        result.synthesis = build.build_synthesis(
            payload, domain=args.domain, live=not use_fixture, llm=llm,
            doc_keys=reg["csv_ids"] + reg["doc_ids"], model=None, suppress_names=suppress_names,
            reg=reg)
    except Exception as e:
        if has_fixture and not use_fixture:
            print(f"! live synthesis failed ({type(e).__name__}: {e}); "
                  f"falling back to the grounded {args.domain} fixture.")
            result.synthesis = build.build_synthesis(payload, domain=args.domain, live=False)
        else:
            print(f"! synthesis failed for '{args.domain}' and there is no fixture for this "
                  f"domain to fall back to ({type(e).__name__}: {e}).")
            print("  Re-run with a working model. NOT rendering wrong-domain content.")
            return 1

    # ---- render -----------------------------------------------------------
    OUT.mkdir(exist_ok=True)
    suite_dir = OUT / args.domain  # the 6-report client suite (the deliverable)
    index = render_suite(result.synthesis, {"client": client, "domain_label": domain_label},
                         suite_dir, suppress_names=suppress_names)
    # internal JSON: client view + synthesis + the raw tool-level trace (audit, never client-facing)
    internal = {**result.to_dict(), "internal_trace": result.raw_payload or {}}
    if refresh_diff is not None:
        internal["refresh_diff"] = refresh_diff
    # Confidentiality hand-off for downstream client-facing consumers (e.g. the explorer SPA):
    # the names that must NOT be shown on screen for this run, plus the neutral label to use
    # instead. The print suite already scrubs these at render; this lets the SPA's sync step do the
    # same so the suppressed name never even ships to a static host. (Internal trace keeps the
    # real text — this block only declares what to scrub for the client-facing view.)
    internal["_confidential"] = {
        "suppress_requested": suppress,
        "suppress_names": suppress_names,
        "client_display": client or "the organisation",
    }
    (OUT / f"discovery-{args.domain}.json").write_text(
        json.dumps(internal, indent=2, sort_keys=True, ensure_ascii=False), encoding="utf-8")
    print(f"\nDone. Open the suite: {index.relative_to(ROOT)}")
    print(f"  (internal audit trace: {(OUT / f'discovery-{args.domain}.json').relative_to(ROOT)})")

    if args.save_golden:
        _save_golden_cache(args.domain)
        print(f"  saved golden run for '{args.domain}'.")
    return 0


# The scripted discovery plan is a hand-pinned O2C-only trajectory (like the fixture). It must
# NOT run for another domain — it would produce O2C-specific tool calls / garbage.
SCRIPTED_DOMAINS = {"o2c"}


def _discover(llm, args, reg, narrative_text, domain_label="business process"):
    """Returns (payload, path_label) or (None, None) on hard failure."""
    scripted_ok = args.domain in SCRIPTED_DOMAINS
    if args.scripted:
        if not scripted_ok:
            print(f"! --scripted is only available for {sorted(SCRIPTED_DOMAINS)}; "
                  f"'{args.domain}' must use the agent path.")
            return None, None
        try:
            return scripted.scripted_plan(llm, narrative_text), "scripted"
        except LLMError as e:
            print(f"! scripted path failed: {e}")
            return None, None
    # agent path
    try:
        print("The platform is reading your landscape...\n")
        feed = lambda line: print(f"   · {line}", flush=True)
        return agent_loop.run_discovery(llm, reg["csv_ids"], reg["doc_ids"], narrative_text,
                                        on_activity=feed, domain_label=domain_label), "agent"
    except (agent_loop.AgentBudgetExceeded, agent_loop.GroundingError, LLMError) as e:
        if args.agent:
            print(f"! agent path failed and --agent disables fallback: {e}")
            return None, None
        # only fall back to the scripted plan where it's valid (O2C); otherwise fail honestly
        if scripted_ok:
            print(f"! agent path failed ({type(e).__name__}); falling back to the O2C scripted plan.")
            try:
                return scripted.scripted_plan(llm, narrative_text), "scripted (fallback)"
            except LLMError as e2:
                print(f"! scripted fallback also failed: {e2}")
                return None, None
        print(f"! agent path failed for '{args.domain}' ({type(e).__name__}); no domain-specific "
              f"fallback exists. Re-run; not producing wrong-domain content.")
        return None, None


def _narrative_block(doc_ids: list[str]) -> str:
    from discovery import tools
    parts = []
    for d in doc_ids:
        text = tools.DOC_TEXT.get(d, "")
        if len(text) > 6000:
            text = text[:6000] + "\n...(truncated)"
        parts.append(f"=== {d} ===\n{text}")
    return "\n\n".join(parts)


def _save_golden_cache(domain: str) -> None:
    dest = GOLDEN / domain
    if dest.exists():
        shutil.rmtree(dest)
    shutil.copytree(ROOT / ".cache", dest)


def _activate_golden_cache(domain: str) -> None:
    src = GOLDEN / domain
    if not src.is_dir():
        print(f"error: no golden run saved for '{domain}'. Run live with --save-golden first.")
        sys.exit(2)
    cache = ROOT / ".cache"
    cache.mkdir(exist_ok=True)
    for f in src.glob("*.json"):
        shutil.copy(f, cache / f.name)


if __name__ == "__main__":
    raise SystemExit(main())
