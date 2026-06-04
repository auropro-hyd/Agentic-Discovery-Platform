import { DiscoveryDoc } from "./synthesis.schema";
import type { DomainStore } from "./store";
import { buildStore } from "./store";
import { loaderFor } from "./domains";

export class LoadError extends Error {
  constructor(
    message: string,
    readonly detail?: string,
  ) {
    super(message);
    this.name = "LoadError";
  }
}

const cache = new Map<string, DomainStore>();

/** Dynamically import + zod-validate one domain's JSON, then build its derived store.
 *  Validation failure throws LoadError (caught by ErrorBoundary -> "data contract changed"
 *  banner) rather than rendering a blank screen. Memoised per slug. */
export async function loadDomain(slug: string): Promise<DomainStore> {
  const cached = cache.get(slug);
  if (cached) return cached;

  const loader = loaderFor(slug);
  if (!loader) throw new LoadError(`Unknown domain "${slug}".`);

  let raw: unknown;
  try {
    const mod = (await loader()) as { default?: unknown };
    raw = mod.default ?? mod;
  } catch (e) {
    throw new LoadError(`Could not load data for "${slug}".`, String(e));
  }

  const parsed = DiscoveryDoc.safeParse(raw);
  if (!parsed.success) {
    const first = parsed.error.issues[0];
    throw new LoadError(
      "The discovery data does not match the expected contract.",
      first ? `${first.path.join(".")}: ${first.message}` : parsed.error.message,
    );
  }

  const doc = parsed.data;
  const clientDisplay = doc.client_display || doc.domain_label || slug;
  const store = buildStore(slug, doc.domain_label || slug, clientDisplay, doc.synthesis);

  // dev-only fabrication scan: warn if an opportunity's business-impact narrative cites a number
  // that does not appear in fact_store.quant (catches fabrication during demo prep, not the client).
  if (import.meta.env.DEV) devFabricationScan(store);

  cache.set(slug, store);
  return store;
}

function devFabricationScan(store: DomainStore): void {
  const known = new Set<string>();
  for (const q of store.synthesis.fact_store?.quant ?? []) known.add(normNum(String(q.value)));
  for (const opp of store.synthesis.opportunities) {
    const text = opp.business_impact?.narrative ?? "";
    const nums = text.match(/\d[\d,.]*\d|\d/g) ?? [];
    for (const n of nums) {
      const norm = normNum(n);
      if (norm.length >= 3 && !known.has(norm)) {
        // small numbers (years, single digits) are noisy; only flag 3+ significant digits
        console.warn(
          `[grounding] ${opp.id} business_impact cites "${n}" not found verbatim in fact_store.quant — verify it is grounded.`,
        );
      }
    }
  }
}

function normNum(s: string): string {
  return s.replace(/[,\s]/g, "").replace(/\.0+$/, "");
}
