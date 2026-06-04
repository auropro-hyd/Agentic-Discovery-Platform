// Copy the discovery synthesis JSON from the Python engine's output (v1/out/discovery-*.json)
// into the SPA's bundled static assets (src/data/). The SPA ships those copies so the built
// dist/ is fully self-contained (static-hostable, file://-openable) with no Python at view time.
//
// Run automatically before `dev` and `build` (see package.json). Idempotent.
import { readdir, mkdir, readFile, writeFile, stat } from "node:fs/promises";
import { fileURLToPath } from "node:url";
import { dirname, join, basename } from "node:path";

const here = dirname(fileURLToPath(import.meta.url));
const SRC = join(here, "..", "..", "v1", "out"); // ../../v1/out
const DEST = join(here, "..", "src", "data");

async function main() {
  let entries;
  try {
    entries = await readdir(SRC);
  } catch {
    console.error(`sync-data: cannot read ${SRC} — run the Python engine first (python run.py --domain o2c).`);
    process.exit(1);
  }
  const jsons = entries.filter((f) => /^discovery-.+\.json$/.test(f));
  if (jsons.length === 0) {
    console.error(`sync-data: no discovery-*.json in ${SRC}. Generate a suite first.`);
    process.exit(1);
  }
  await mkdir(DEST, { recursive: true });
  for (const f of jsons) {
    try {
      await syncOne(f);
    } catch (e) {
      // Per-file failures must name the file and STOP the build — a silent skip here could leave a
      // stale or unscrubbed file in src/data/. Confidentiality > convenience.
      console.error(`sync-data: FAILED on ${f}: ${e instanceof Error ? e.message : e}`);
      process.exit(1);
    }
  }
  console.log(`sync-data: ${jsons.length} domain file(s) synced.`);
}

async function syncOne(f) {
  const from = join(SRC, f);
  const to = join(DEST, f);
  const doc = JSON.parse(await readFile(from, "utf8"));

  // CONFIDENTIALITY CONTRACT (fail loud, never silently). The engine writes a _confidential block;
  // a missing/malformed one is NOT treated as "nothing to scrub" — that was a silent-leak hole.
  const conf = doc._confidential;
  if (!conf || !Array.isArray(conf.suppress_names) || typeof conf.client_display !== "string") {
    throw new Error(
      `missing/malformed _confidential block (${JSON.stringify(conf)}). Re-run the engine; a ` +
        `missing block could ship an unscrubbed client name.`,
    );
  }
  // Suppression was requested but the engine detected no name to scrub: the org may still appear in
  // the prose, so refuse rather than ship a possibly-named view. (Set an explicit manifest 'client'.)
  if (conf.suppress_requested && conf.suppress_names.length === 0) {
    throw new Error(
      `suppress_client was requested but no name was detected to scrub. Set a manifest 'client' ` +
        `name so the SPA can scrub it, or confirm the reports name no organisation.`,
    );
  }

  // scrub the synthesis AND the domain_label (both client-facing); drop internal_trace entirely.
  // Carry the engine's neutral client_display label into the shipped doc (the SPA reads it as the
  // client name). It's already neutral, but run it through scrub for safety; we deliberately DO NOT
  // ship the raw suppress_names list — only this one sanitized label.
  const clean = {
    domain: doc.domain,
    domain_label: scrub(doc.domain_label, conf.suppress_names, conf.client_display),
    client_display: scrub(conf.client_display, conf.suppress_names, conf.client_display),
    synthesis: scrub(doc.synthesis, conf.suppress_names, conf.client_display),
  };

  // DEFENSE IN DEPTH (token-aware): verify no suppressed name survived anywhere in the client-facing
  // output. We check each full suppress_names entry AND each whitespace-split token of length >= 3
  // within it (case-insensitive, word-boundary) — so even a single-entry multi-word name can't slip
  // a bare token (e.g. "Opella Europe" leaving "Europe"). Abort on any hit: a failed build beats a leak.
  const serialized = JSON.stringify(clean);
  const checks = new Set();
  for (const name of conf.suppress_names) {
    if (!name) continue;
    checks.add(name);
    for (const tok of String(name).split(/\s+/)) {
      if (tok.length >= 3) checks.add(tok);
    }
  }
  for (const needle of checks) {
    if (new RegExp(`\\b${escapeRe(needle)}\\b`, "i").test(serialized)) {
      throw new Error(`suppressed name "${needle}" still present after scrub. Aborting to avoid a leak.`);
    }
  }

  await writeFile(to, serialized, "utf8");
  const { size } = await stat(to);
  const note = conf.suppress_names.length ? ` [scrubbed: ${conf.suppress_names.join(", ")}]` : "";
  console.log(`sync-data: ${basename(from)} -> src/data/ (${(size / 1024).toFixed(0)} KB)${note}`);
}

// A raw SHOUTY_SNAKE enum value a model copied into prose (NOT_FULFILLED, ON_HOLD). Two+
// underscore-joined all-caps segments — narrow enough to never touch a real acronym. Mirrors the
// print suite's _humanize_enums so the SPA reads the same clean prose.
const SNAKE_ENUM = /\b[A-Z][A-Z0-9]+(?:_[A-Z0-9]+)+\b/g;

// An identifier-shaped slug: lowercase alnum segments joined by hyphens/underscores, no spaces
// (e.g. "order-management-sop"). doc_id values are slugs and are used as keys to resolve
// source_index, so injecting a space (the prose label "the organisation") would silently break the
// lookup. We detect slugs and neutralise names with a hyphen-safe token instead.
const SLUG_SHAPE = /^[a-z0-9]+(?:[-_][a-z0-9]+)+$/;

/** Recursively clean every string in the client-facing synthesis subtree:
 *  (1) replace each suppressed name (whole-word) with the neutral label; (2) humanise raw enum
 *  values (NOT_FULFILLED -> "not fulfilled"). Both are cosmetic — they change names/casing, never
 *  numbers — and mirror exactly what the print renderer does.
 *
 *  SLUG SAFETY: for identifier-shaped slugs (and any value under a "doc_id" key) we must not inject
 *  a space. A name embedded in a slug like "...-opella-europe" is itself confidential, so rather
 *  than leave it raw OR mangle it with "the organisation", we replace each suppressed name (and its
 *  hyphenated form) with the neutral lowercase token "client" — keeping it a valid slug and leaking
 *  nothing. The doc_id stays consistently neutralised on both the value and any reference to it. */
function scrub(node, names, replacement) {
  const cleanNames = (names || []).filter(Boolean);
  // Slug patterns: match the name with spaces OR hyphens between its tokens, replace with "client".
  const slugPatterns = cleanNames.map(
    (n) => new RegExp(escapeRe(n).replace(/\s+/g, "[\\s-]+"), "gi"),
  );
  const repl = replacement || "the organisation";

  const cleanString = (s, isSlug) => {
    let out = s;
    if (isSlug) {
      for (const p of slugPatterns) out = out.replace(p, "client");
    } else {
      // Prose path. But a slug fragment can be EMBEDDED in prose too (the LLM writes a raw doc_id
      // like "o2c-process-raci-opella-europe" inside a sentence). Replacing the name with the
      // spaced label there would mangle the slug ("...-the organisation-europe"). So when the name
      // is flanked by a hyphen (a slug token), use the hyphen-safe "client"; otherwise the label.
      for (const n of cleanNames) {
        // hyphen-flanked occurrence inside a slug fragment -> "client"
        out = out.replace(new RegExp(`(?<=-)${escapeRe(n)}(?=-)`, "gi"), "client");
        out = out.replace(new RegExp(`(?<=-)${escapeRe(n)}(?=\\b)`, "gi"), "client");
        out = out.replace(new RegExp(`(?<=\\b)${escapeRe(n)}(?=-)`, "gi"), "client");
        // remaining standalone occurrences -> the neutral prose label
        out = out.replace(new RegExp(`\\b${escapeRe(n)}\\b('s)?`, "gi"), repl);
      }
    }
    out = out.replace(SNAKE_ENUM, (m) => m.replace(/_/g, " ").toLowerCase());
    return out;
  };

  // `key` is the object key this value sits under (when applicable); "doc_id" forces slug handling.
  const walk = (v, key) => {
    if (typeof v === "string") return cleanString(v, key === "doc_id" || SLUG_SHAPE.test(v));
    if (Array.isArray(v)) return v.map((el) => walk(el));
    if (v && typeof v === "object") {
      const o = {};
      for (const [k, val] of Object.entries(v)) o[k] = walk(val, k);
      return o;
    }
    return v;
  };
  return walk(node);
}

function escapeRe(s) {
  return s.replace(/[.*+?^${}()|[\]\\]/g, "\\$&");
}

main();
