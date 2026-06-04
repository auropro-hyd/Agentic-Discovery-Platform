import { Link, useSearchParams } from "react-router-dom";
import { useDomainData } from "../lib/useDomainData";
import { search } from "../lib/buildSearchIndex";
import type { DocRecord, RecordKind } from "../lib/buildSearchIndex";
import { PlanningBadge } from "../primitives/PlanningBadge";
import { EmptyState, Section } from "../primitives/EmptyState";

/* Cross-suite search results. Reads ?q= from the URL, runs the in-memory token-AND search over
 * the domain's flattened corpus, and groups hits by kind. Each hit deep-links to its detail route.
 * Planning assumptions carry the PlanningBadge so a forward-looking statement never reads as fact. */

const KIND_LABEL: Record<RecordKind, string> = {
  pain_point: "Pain points",
  opportunity: "Opportunities",
  assumption: "Planning assumptions",
  evidence: "Evidence",
  source: "Sources",
  quote: "Quotes",
  table: "Data tables",
  metric: "Metrics",
};

const KIND_ORDER: RecordKind[] = [
  "pain_point",
  "opportunity",
  "metric",
  "evidence",
  "source",
  "quote",
  "table",
  "assumption",
];

export default function SearchResultsPage() {
  const { store, searchIndex } = useDomainData();
  const [params] = useSearchParams();
  const q = (params.get("q") || "").trim();

  const results = search(searchIndex, q);

  const grouped = new Map<RecordKind, DocRecord[]>();
  for (const r of results) {
    const bucket = grouped.get(r.kind);
    if (bucket) bucket.push(r);
    else grouped.set(r.kind, [r]);
  }

  return (
    <div>
      <header className="page-head">
        <div className="eyebrow">Search</div>
        <h1>{q ? `Results for "${q}"` : "Search the discovery suite"}</h1>
        <p className="lede">
          Across pain points, opportunities, evidence, sources and metrics for the {store.domainLabel} suite.
        </p>
      </header>

      {!q ? (
        <EmptyState>Type a query to search across the {store.domainLabel} discovery suite.</EmptyState>
      ) : results.length === 0 ? (
        <EmptyState>{`No matches for "${q}".`}</EmptyState>
      ) : (
        <>
          <div className="toolbar">
            <span className="count">
              {results.length} {results.length === 1 ? "result" : "results"}
            </span>
          </div>

          {KIND_ORDER.filter((k) => grouped.has(k)).map((kind) => {
            const items = grouped.get(kind) ?? [];
            return (
              <Section key={kind} title={`${KIND_LABEL[kind]} (${items.length})`}>
                <div className="linkrail">
                  {items.map((r) => (
                    <Link key={`${r.kind}-${r.id}`} to={r.route}>
                      <span style={{ display: "flex", alignItems: "center", gap: 8, flexWrap: "wrap" }}>
                        <strong style={{ color: "var(--navy)" }}>{r.title}</strong>
                        {r.kind === "assumption" && <PlanningBadge />}
                      </span>
                      {r.snippet && (
                        <span className="small muted" style={{ display: "block", marginTop: 4 }}>
                          {r.snippet.slice(0, 160)}
                        </span>
                      )}
                    </Link>
                  ))}
                </div>
              </Section>
            );
          })}
        </>
      )}
    </div>
  );
}
