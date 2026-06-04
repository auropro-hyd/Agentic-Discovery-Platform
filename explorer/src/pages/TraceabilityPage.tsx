import { useDomainData } from "../lib/useDomainData";
import { SeverityBadge } from "../primitives/badges";
import { EmptyState } from "../primitives/EmptyState";
import type { TraceRow } from "../lib/types";

/* Read-only traceability matrix. Rows are narrative prose strings with NO record ids, so cells
 * are rendered verbatim and never linkified. The summary, when present, becomes a sub-row and a
 * row title attribute. */
export default function TraceabilityPage() {
  const { store } = useDomainData();
  const rows: TraceRow[] = store.synthesis.traceability ?? [];

  return (
    <div>
      <header className="page-head">
        <div className="eyebrow">Traceability</div>
        <h1>Traceability matrix</h1>
        <p className="lede">
          End-to-end thread from each pain point through to its recommendation, expected outcome and
          delivery horizon for {store.domainLabel}.
        </p>
      </header>

      {rows.length === 0 ? (
        <EmptyState>No traceability rows recorded for this domain.</EmptyState>
      ) : (
        <div className="panel">
          <table className="dt">
            <thead>
              <tr>
                <th>Pain point</th>
                <th>Opportunity</th>
                <th>Recommendation</th>
                <th>Expected outcome</th>
                <th>Horizon</th>
                <th>Severity</th>
              </tr>
            </thead>
            <tbody>
              {rows.map((row, i) => [
                <tr key={`r-${i}`} title={row.summary || undefined}>
                  <td>{row.pain_point}</td>
                  <td>{row.opportunity}</td>
                  <td>{row.recommendation}</td>
                  <td>{row.expected_outcome}</td>
                  <td>{row.horizon}</td>
                  <td>
                    {row.severity ? <SeverityBadge severity={row.severity} /> : <span className="muted">—</span>}
                  </td>
                </tr>,
                row.summary ? (
                  <tr key={`s-${i}`}>
                    <td colSpan={6} className="small muted">
                      {row.summary}
                    </td>
                  </tr>
                ) : null,
              ])}
            </tbody>
          </table>
          <p className="small muted">
            This matrix is generated from narrative summaries; cells are not yet machine-linked to
            individual records.
          </p>
        </div>
      )}
    </div>
  );
}
