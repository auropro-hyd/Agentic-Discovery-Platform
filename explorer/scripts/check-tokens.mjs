// Prebuild guard: warn (do not fail) if the SPA's design tokens have drifted from the print
// suite's CSS. The SPA lifts the navy/blue identity from v1/out/o2c/assets/report.css :root;
// if the print suite changes a brand colour, this nudges us to re-sync tokens.css.
import { readFile } from "node:fs/promises";
import { fileURLToPath } from "node:url";
import { dirname, join } from "node:path";

const here = dirname(fileURLToPath(import.meta.url));
const PRINT_CSS = join(here, "..", "..", "v1", "out", "o2c", "assets", "report.css");
const TOKENS = join(here, "..", "src", "styles", "tokens.css");

// the brand colours the two must agree on
const KEYS = ["--navy", "--blue"];

function grabVar(css, name) {
  const m = css.match(new RegExp(`${name}\\s*:\\s*([^;]+);`));
  return m ? m[1].trim().toLowerCase() : null;
}

try {
  const [print, tokens] = await Promise.all([readFile(PRINT_CSS, "utf8"), readFile(TOKENS, "utf8")]);
  const drift = KEYS.filter((k) => {
    const a = grabVar(print, k);
    const b = grabVar(tokens, k);
    return a && b && a !== b;
  });
  if (drift.length) {
    console.warn(`check-tokens: ⚠ brand colours drifted from the print suite (${drift.join(", ")}). Re-sync explorer/src/styles/tokens.css.`);
  } else {
    console.log("check-tokens: brand tokens match the print suite.");
  }
} catch {
  // print suite not present in this checkout — skip silently (the SPA still has its own tokens)
  console.log("check-tokens: print suite CSS not found; skipping drift check.");
}
