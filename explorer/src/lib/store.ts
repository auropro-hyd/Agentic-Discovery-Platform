import type {
  Synthesis,
  PainPoint,
  Opportunity,
  FactValue,
  FactQuant,
  Tier,
} from "./types";

/* The derived store for one domain. Built once per domain load. Holds:
 *  - id maps (painPointById / opportunityById) for O(1) cross-link resolution
 *  - oppByPainPoint: reverse index opportunity.addresses_pain_point -> opportunities[]
 *  - factByLabel: fact_store.quant indexed by lowercased label (for SourceCite provenance)
 *  - fact(): the SOLE mint of the FactValue brand (grounding chokepoint)
 */

const BRAND = "__fact" as const;

/** Mint a branded FactValue from data that came verbatim from the JSON. THE ONLY place a
 *  FactValue is created — so <GroundedNumber> can only ever show a JSON-sourced figure. */
export function fact(
  value: number | string,
  opts: { unit?: string; label?: string; sources?: string[]; tier?: Tier } = {},
): FactValue {
  return {
    [BRAND]: true,
    value,
    unit: opts.unit,
    label: opts.label,
    sources: opts.sources,
    tier: opts.tier,
  } as unknown as FactValue;
}

/** Mint a FactValue from a fact_store quant row (carries unit/sources/tier provenance). */
export function factFromQuant(q: FactQuant): FactValue {
  return fact(q.value, { unit: q.unit, label: q.label, sources: q.sources, tier: q.tier });
}

export interface DomainStore {
  domain: string;
  domainLabel: string;
  clientDisplay: string; // the client name to show on screen (neutral when suppressed)
  synthesis: Synthesis;
  painPointById: Map<string, PainPoint>;
  opportunityById: Map<string, Opportunity>;
  oppByPainPoint: Map<string, Opportunity[]>;
  factByLabel: Map<string, FactQuant>;
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
