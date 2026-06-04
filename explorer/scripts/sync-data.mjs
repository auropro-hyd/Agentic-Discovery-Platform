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
    const from = join(SRC, f);
    const to = join(DEST, f);
    const doc = JSON.parse(await readFile(from, "utf8"));

    // CONFIDENTIALITY: scrub any names the run flagged as suppressed (e.g. a client name hidden
    // for a demo) from the client-facing view, mirroring the print suite. The internal_trace
    // (audit) is dropped entirely — the SPA never reads it and it carries the real name.
    const conf = doc._confidential ?? { suppress_names: [], client_display: doc.domain_label };
    const clean = {
      domain: doc.domain,
      domain_label: doc.domain_label,
      synthesis: scrub(doc.synthesis, conf.suppress_names ?? [], conf.client_display),
    };

    await writeFile(to, JSON.stringify(clean), "utf8");
    const { size } = await stat(to);
    const note = (conf.suppress_names ?? []).length ? ` [scrubbed: ${conf.suppress_names.join(", ")}]` : "";
    console.log(`sync-data: ${basename(from)} -> src/data/ (${(size / 1024).toFixed(0)} KB)${note}`);
  }
  console.log(`sync-data: ${jsons.length} domain file(s) synced.`);
}

// A raw SHOUTY_SNAKE enum value a model copied into prose (NOT_FULFILLED, ON_HOLD). Two+
// underscore-joined all-caps segments — narrow enough to never touch a real acronym. Mirrors the
// print suite's _humanize_enums so the SPA reads the same clean prose.
const SNAKE_ENUM = /\b[A-Z][A-Z0-9]+(?:_[A-Z0-9]+)+\b/g;

/** Recursively clean every string in the client-facing synthesis subtree:
 *  (1) replace each suppressed name (whole-word) with the neutral label; (2) humanise raw enum
 *  values (NOT_FULFILLED -> "not fulfilled"). Both are cosmetic — they change names/casing, never
 *  numbers — and mirror exactly what the print renderer does. */
function scrub(node, names, replacement) {
  const patterns = (names || [])
    .filter(Boolean)
    .map((n) => new RegExp(`\\b${escapeRe(n)}\\b('s)?`, "gi"));
  const repl = replacement || "the organisation";

  const cleanString = (s) => {
    let out = s;
    for (const p of patterns) out = out.replace(p, repl);
    out = out.replace(SNAKE_ENUM, (m) => m.replace(/_/g, " ").toLowerCase());
    return out;
  };

  const walk = (v) => {
    if (typeof v === "string") return cleanString(v);
    if (Array.isArray(v)) return v.map(walk);
    if (v && typeof v === "object") {
      const o = {};
      for (const [k, val] of Object.entries(v)) o[k] = walk(val);
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
