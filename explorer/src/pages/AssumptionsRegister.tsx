import { useDomainData } from "../lib/useDomainData";
import { Section, EmptyState } from "../primitives/EmptyState";
import { PlanningRow } from "../primitives/PlanningBadge";
import type { PlanningAssumption } from "../lib/types";

/* Known planning-assumption kinds, in a deliberate reading order, with presentation labels. */
const KIND_ORDER = ["date", "owner", "sla", "threshold", "cadence", "cost", "sequence"];
const KIND_LABEL: Record<string, string> = {
  date: "Dates",
  owner: "Owners",
  sla: "SLAs",
  threshold: "Thresholds",
  cadence: "Cadences",
  cost: "Cost",
  sequence: "Sequencing",
};

/** Title-case a kind we don't have an explicit label for (e.g. "Other"). */
function niceKind(kind: string): string {
  const k = (kind || "").toLowerCase();
  if (KIND_LABEL[k]) return KIND_LABEL[k];
  if (!k) return "Other";
  return k.charAt(0).toUpperCase() + k.slice(1);
}

export default function AssumptionsRegister() {
  const { store } = useDomainData();
  const assumptions = store.synthesis.planning_assumptions ?? [];

  // Group by lowercased kind, preserving JSON order within each group.
  const groups = new Map<string, PlanningAssumption[]>();
  for (const pa of assumptions) {
    const key = (pa.kind || "").toLowerCase();
    const bucket = groups.get(key);
    if (bucket) bucket.push(pa);
    else groups.set(key, [pa]);
  }

  // Known kinds first (in canonical order), then any extra kinds as they appeared.
  const orderedKeys: string[] = [];
  for (const k of KIND_ORDER) {
    if (groups.has(k)) orderedKeys.push(k);
  }
  for (const k of groups.keys()) {
    if (!orderedKeys.includes(k)) orderedKeys.push(k);
  }

  return (
    <div>
      <header className="page-head">
        <div className="eyebrow">{store.domainLabel} · Planning</div>
        <h1>Assumptions Register</h1>
        <p className="lede">
          These are forward-looking <strong>planning inputs</strong> — proposed dates, owners, SLAs,
          thresholds, cadences, costs and sequencing the engine put forward to make the roadmap
          actionable. They are clearly labelled and are <strong>not</strong> discovered facts; each
          carries the basis on which it was proposed and should be confirmed before commitment.
        </p>
        <span className="count">
          Showing {assumptions.length} planning {assumptions.length === 1 ? "assumption" : "assumptions"}
        </span>
      </header>

      {assumptions.length === 0 ? (
        <EmptyState>No planning assumptions were recorded for this domain.</EmptyState>
      ) : (
        orderedKeys.map((key) => {
          const rows = groups.get(key) ?? [];
          return (
            <Section key={key || "other"} title={niceKind(key)}>
              <div className="linkrail">
                {rows.map((pa, i) => (
                  <PlanningRow key={key + "-" + i} assumption={pa} />
                ))}
              </div>
            </Section>
          );
        })
      )}
    </div>
  );
}
