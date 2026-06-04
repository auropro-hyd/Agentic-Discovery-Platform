import { Link } from "react-router-dom";
import { useDomainData } from "../lib/useDomainData";
import { StatGrid, type StatItem } from "../primitives/StatGrid";
import { EmptyState, Section } from "../primitives/EmptyState";
import { QuadrantBoard } from "../charts/QuadrantBoard";
import { PainPointCard } from "../cards/PainPointCard";

/* Landing page for a domain. Everything rendered is verbatim from the engine JSON — no view math.
 * Count-agnostic: baseline_stats / opportunities / pain_points may be empty in some domains. */
export default function OverviewPage() {
  const { store } = useDomainData();
  const { synthesis, domain, domainLabel } = store;

  const summary = synthesis.executive_summary;
  const baselineStats = synthesis.current_state?.baseline_stats ?? [];
  const opportunities = synthesis.opportunities;
  const painPoints = synthesis.pain_points;

  const headline = summary?.headline || `${domainLabel} discovery`;

  // baseline_stats[].value is engine-pre-formatted (string like "67.3%", or a number) — render verbatim.
  const statItems: StatItem[] = baselineStats.map((stat) => ({
    value: stat.value ?? "—",
    label: stat.label,
    sublabel: stat.sublabel || undefined,
  }));

  const topPainPoints = painPoints.slice(0, 3);

  return (
    <div>
      <header className="page-head">
        <div className="eyebrow">{domainLabel} · Discovery overview</div>
        <h1>{headline}</h1>
        {summary?.situation && <p className="lede">{summary.situation}</p>}
      </header>

      <Section title="Baseline at a glance">
        {statItems.length ? (
          <StatGrid items={statItems} />
        ) : (
          <EmptyState>No baseline statistics recorded for this domain.</EmptyState>
        )}
      </Section>

      <Section title="The opportunity">
        <div className="panel">
          {summary?.opportunity ? (
            <p>{summary.opportunity}</p>
          ) : (
            <EmptyState>No opportunity statement recorded for this domain.</EmptyState>
          )}
        </div>
      </Section>

      <Section title="Portfolio at a glance">
        {opportunities.length ? (
          <>
            <QuadrantBoard domain={domain} opportunities={opportunities} />
            <div className="linkrail">
              <Link to={`/suite/${domain}/opportunities`}>View full portfolio →</Link>
            </div>
          </>
        ) : (
          <EmptyState>No opportunities recorded for this domain.</EmptyState>
        )}
      </Section>

      <Section title="Top pain points">
        {topPainPoints.length ? (
          <>
            <div className="grid cols-3">
              {topPainPoints.map((pp) => (
                <PainPointCard key={pp.id} domain={domain} pp={pp} />
              ))}
            </div>
            <div className="linkrail">
              <Link to={`/suite/${domain}/pain-points`}>View all pain points →</Link>
            </div>
          </>
        ) : (
          <EmptyState>No pain points recorded for this domain.</EmptyState>
        )}
      </Section>
    </div>
  );
}
