import { Link, useParams } from "react-router-dom";
import { useDomainData } from "../lib/useDomainData";
import { SeverityBadge, CategoryBadge } from "../primitives/badges";
import { BackChip } from "../layout/Breadcrumb";
import { DataTable } from "../primitives/DataTable";
import { EmptyState, Section } from "../primitives/EmptyState";

/* Detail for a single pain point. Reads :ppId from the route, looks it up in store.painPointById,
 * and renders the engine's verbatim strings (description, root cause, failure pattern, business
 * consequence, the quantified evidence sentences, an optional detail table, and source quotes).
 * Cross-links to every opportunity that addresses this pain point via store.oppByPainPoint. No
 * client-side number computation — figures are shown exactly as the engine formatted them. */
export default function PainPointDetail() {
  const { store } = useDomainData();
  const { ppId } = useParams();
  const domain = store.domain;

  const pp = ppId ? store.painPointById.get(ppId) : undefined;

  if (!pp) {
    return (
      <div>
        <BackChip to={`/${domain}/pain-points`} label="All pain points" />
        <div className="empty">No such pain point in this domain.</div>
      </div>
    );
  }

  const quantified = pp.quantified ?? [];
  const sources = pp.sources ?? [];
  const addressedBy = store.oppByPainPoint.get(pp.id) ?? [];

  return (
    <div>
      <BackChip to={`/${domain}/pain-points`} label="All pain points" />

      <header className="page-head">
        <div className="eyebrow">Pain point</div>
        <h1>
          <span className="tiny muted" style={{ fontWeight: 800, color: "var(--blue)", marginRight: 10 }}>
            {pp.id}
          </span>
          {pp.title}
        </h1>
        <div className="taglist" style={{ marginTop: 8 }}>
          <SeverityBadge severity={pp.severity} />
          {pp.category && <CategoryBadge category={pp.category} />}
        </div>
        {pp.description && <p className="lede">{pp.description}</p>}
      </header>

      <Section title="Diagnosis">
        {pp.root_cause || pp.failure_pattern || pp.business_consequence ? (
          <dl className="kv">
            {pp.root_cause && (
              <>
                <dt>Root cause</dt>
                <dd>{pp.root_cause}</dd>
              </>
            )}
            {pp.failure_pattern && (
              <>
                <dt>Failure pattern</dt>
                <dd>{pp.failure_pattern}</dd>
              </>
            )}
            {pp.business_consequence && (
              <>
                <dt>Business consequence</dt>
                <dd>{pp.business_consequence}</dd>
              </>
            )}
          </dl>
        ) : (
          <EmptyState />
        )}
      </Section>

      <Section title="Evidence">
        {quantified.length > 0 ? (
          <ul className="linkrail">
            {quantified.map((q, i) => (
              <li key={i}>
                {q.text ? q.text : q.label + ": " + String(q.value ?? "") + q.unit}
              </li>
            ))}
          </ul>
        ) : (
          <EmptyState />
        )}
      </Section>

      {pp.detail_table && (
        <Section title="Detail">
          <DataTable table={pp.detail_table} />
        </Section>
      )}

      <Section title="Sources">
        {sources.length > 0 ? (
          <ul className="linkrail">
            {sources.map((src, i) => (
              <li key={i}>
                <strong>{src.doc_id || "—"}</strong>
                {src.quote && <span className="small muted"> — “{src.quote}”</span>}
                {src.locator && <span className="tiny muted"> ({src.locator})</span>}
              </li>
            ))}
          </ul>
        ) : (
          <EmptyState />
        )}
      </Section>

      <Section title="Addressed by">
        {addressedBy.length > 0 ? (
          <div className="linkrail">
            {addressedBy.map((opp) => (
              <Link key={opp.id} to={`/${domain}/opportunities/${opp.id}`} className="tag">
                <strong>{opp.id}</strong> {opp.title}
              </Link>
            ))}
          </div>
        ) : (
          <EmptyState>No opportunities mapped to this pain point yet.</EmptyState>
        )}
      </Section>
    </div>
  );
}
