import { useSearchParams } from "react-router-dom";
import { useDomainData } from "../lib/useDomainData";
import type { PainPoint } from "../lib/types";
import { SeverityOrder } from "../lib/types";
import { PainPointCard } from "../cards/PainPointCard";
import { EmptyState } from "../primitives/EmptyState";

/* Pain-point list with a shareable filter+sort toolbar (state in the URL via useSearchParams).
 * Count-agnostic (o2c has 6 PPs, p2p has 3) and arithmetic-free per the page grounding rules. */

const SEV_FILTERS: Array<{ key: string; label: string }> = [
  { key: "all", label: "All" },
  { key: "high", label: "High" },
  { key: "medium", label: "Medium" },
  { key: "lower", label: "Lower" },
];

export default function PainPointList() {
  const { store } = useDomainData();
  const [params, setParams] = useSearchParams();

  const sev = params.get("sev") ?? "all";
  const sort = params.get("sort") ?? "impact";

  const all = store.synthesis.pain_points;

  const filtered =
    sev === "all" ? all : all.filter((pp) => pp.severity === sev);

  const sorted = [...filtered].sort((a, b) => {
    if (sort === "severity") {
      const ra = SeverityOrder[a.severity] ?? 99;
      const rb = SeverityOrder[b.severity] ?? 99;
      return ra < rb ? -1 : ra > rb ? 1 : 0;
    }
    // default: by impact_rank ascending (1 = most impactful)
    const ra = a.impact_rank ?? 99;
    const rb = b.impact_rank ?? 99;
    return ra < rb ? -1 : ra > rb ? 1 : 0;
  });

  function setParam(key: string, value: string) {
    const next = new URLSearchParams(params);
    next.set(key, value);
    setParams(next);
  }

  return (
    <div>
      <header className="page-head">
        <div className="eyebrow">{store.domainLabel} · Pain points</div>
        <h1>Pain points</h1>
        <p className="lede">
          Validated process pain points surfaced during discovery, ranked by impact. Filter
          by severity or re-sort — the view is shareable via the URL.
        </p>
      </header>

      <div className="toolbar">
        <label>Severity</label>
        {SEV_FILTERS.map((f) => (
          <button
            key={f.key}
            type="button"
            className={sev === f.key ? "chip active" : "chip"}
            onClick={() => setParam("sev", f.key)}
          >
            {f.label}
          </button>
        ))}

        <label htmlFor="pp-sort">Sort</label>
        <select
          id="pp-sort"
          value={sort}
          onChange={(e) => setParam("sort", e.target.value)}
        >
          <option value="impact">Impact rank</option>
          <option value="severity">Severity</option>
        </select>

        <span className="count">
          Showing {sorted.length} of {all.length}
        </span>
      </div>

      {sorted.length === 0 ? (
        <EmptyState>No pain points match this filter.</EmptyState>
      ) : (
        <div className="grid cols-2">
          {sorted.map((pp: PainPoint) => (
            <PainPointCard key={pp.id} domain={store.domain} pp={pp} />
          ))}
        </div>
      )}
    </div>
  );
}
