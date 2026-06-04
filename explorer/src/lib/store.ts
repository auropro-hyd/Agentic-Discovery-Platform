import type {
  Synthesis,
  PainPoint,
  Opportunity,
  FactQuant,
} from "./types";

// The FactValue brand-mints live in types.ts (so FACT_BRAND need never be exported). Re-export them
// here so existing import paths (e.g. EvidencePage imports factFromQuant from "../lib/store") keep working.
export { factFromQuant, factFromNumberRef } from "./types";

/* The derived store for one domain. Built once per domain load. Holds:
 *  - id maps (painPointById / opportunityById) for O(1) cross-link resolution
 *  - oppByPainPoint: reverse index opportunity.addresses_pain_point -> opportunities[]
 *  - factByLabel: fact_store.quant indexed by lowercased label (for SourceCite provenance)
 * The maps are typed ReadonlyMap to express "built once in buildStore, never mutated afterwards".
 */

export interface DomainStore {
  readonly domain: string;
  readonly domainLabel: string;
  readonly clientDisplay: string; // the client name to show on screen (neutral when suppressed)
  readonly synthesis: Synthesis;
  readonly painPointById: ReadonlyMap<string, PainPoint>;
  readonly opportunityById: ReadonlyMap<string, Opportunity>;
  readonly oppByPainPoint: ReadonlyMap<string, Opportunity[]>;
  readonly factByLabel: ReadonlyMap<string, FactQuant>;
}

export function buildStore(
  domain: string,
  domainLabel: string,
  clientDisplay: string,
  s: Synthesis,
): DomainStore {
  const painPointById = new Map<string, PainPoint>();
  for (const pp of s.pain_points) if (pp.id) painPointById.set(pp.id, pp);

  const opportunityById = new Map<string, Opportunity>();
  const oppByPainPoint = new Map<string, Opportunity[]>();
  for (const opp of s.opportunities) {
    if (opp.id) opportunityById.set(opp.id, opp);
    const target = (opp.addresses_pain_point || "").trim(); // OPP6 (o2c) has "" — guarded
    if (target) {
      const list = oppByPainPoint.get(target) ?? [];
      list.push(opp);
      oppByPainPoint.set(target, list);
    }
  }

  const factByLabel = new Map<string, FactQuant>();
  for (const q of s.fact_store?.quant ?? []) {
    const key = (q.label || "").trim().toLowerCase();
    if (key && !factByLabel.has(key)) factByLabel.set(key, q);
  }

  return {
    domain,
    domainLabel,
    clientDisplay,
    synthesis: s,
    painPointById,
    opportunityById,
    oppByPainPoint,
    factByLabel,
  };
}
