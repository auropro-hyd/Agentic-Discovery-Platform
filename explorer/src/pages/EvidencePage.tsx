import { useDomainData } from "../lib/useDomainData";
import { Section, EmptyState } from "../primitives/EmptyState";
import { TierBadge } from "../primitives/badges";
import { GroundedNumber } from "../primitives/GroundedNumber";
import { factFromQuant } from "../lib/store";

/* The provenance hub. Everything here is rendered VERBATIM from the engine's JSON — the evidence
 * register, the source index, and the three fact_store stores (quantified facts, document quotes,
 * entities). No view-layer computation: counts use .length only, and nothing is cited that the
 * engine didn't already attach. Every count-variable section degrades to an <EmptyState/>. */

export default function EvidencePage() {
  const { store } = useDomainData();
  const s = store.synthesis;

  const evidence = s.evidence_register ?? [];
  const sources = s.source_index ?? [];
  const quant = s.fact_store?.quant ?? [];
  const quotes = s.fact_store?.quotes ?? [];
  const entities = s.fact_store?.entities ?? [];

  return (
    <div>
      <header className="page-head">
        <div className="eyebrow">Evidence &amp; provenance</div>
        <h1>Where every finding comes from</h1>
        <p className="lede">
          The grounding trail for {store.domainLabel}: the evidence register, the documents we read,
          and the fact store of quantified figures, verbatim quotes, and entities — each rendered
          exactly as recorded, with its confidence tier.
        </p>
      </header>

      <Section title="Evidence register">
        {evidence.length === 0 ? (
          <EmptyState>No evidence recorded for this domain.</EmptyState>
        ) : (
          <table className="dt">
            <thead>
              <tr>
                <th>Finding</th>
                <th>Data point</th>
                <th>Type</th>
                <th>Source</th>
                <th>Confidence</th>
              </tr>
            </thead>
            <tbody>
              {evidence.map((row, i) => (
                <tr key={i}>
                  <td>{row.finding || "—"}</td>
                  <td>{row.data_point || "—"}</td>
                  <td>{row.evidence_type || "—"}</td>
                  <td>{row.source || "—"}</td>
                  <td>{row.confidence ? <TierBadge tier={row.confidence} /> : "—"}</td>
                </tr>
              ))}
            </tbody>
          </table>
        )}
      </Section>

      <Section title="Sources">
        {sources.length === 0 ? (
          <EmptyState>No source documents indexed for this domain.</EmptyState>
        ) : (
          <div className="grid cols-2">
            {sources.map((src, i) => (
              <div className="card" key={src.doc_id || i}>
                <h3 style={{ margin: "0 0 4px" }}>{src.business_name || src.doc_id || "Untitled source"}</h3>
                {src.doc_type ? <div className="small muted">{src.doc_type}</div> : null}
                {src.what_we_read ? <p style={{ marginTop: 8 }}>{src.what_we_read}</p> : null}
                {src.supported_findings && src.supported_findings.length > 0 ? (
                  <div className="taglist" style={{ marginTop: 8 }}>
                    {src.supported_findings.map((f, fi) => (
                      <span className="tag tiny" key={fi}>
                        {f}
                      </span>
                    ))}
                  </div>
                ) : null}
              </div>
            ))}
          </div>
        )}
      </Section>

      <Section title="Fact store">
        <h3 style={{ marginBottom: 8 }}>Quantified facts</h3>
        {quant.length === 0 ? (
          <EmptyState>No quantified facts recorded.</EmptyState>
        ) : (
          <table className="dt">
            <thead>
              <tr>
                <th>Label</th>
                <th>Value</th>
                <th>Tier</th>
                <th>Sources</th>
              </tr>
            </thead>
            <tbody>
              {quant.map((q, i) => (
                <tr key={i}>
                  <td>{q.label || "—"}</td>
                  <td className="num">
                    <GroundedNumber fact={factFromQuant(q)} cite={false} />
                  </td>
                  <td>{q.tier ? <TierBadge tier={q.tier} /> : "—"}</td>
                  <td className="small muted">
                    {q.sources && q.sources.length > 0 ? q.sources.join(", ") : "—"}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        )}

        <h3 style={{ margin: "20px 0 8px" }}>Document quotes</h3>
        {quotes.length === 0 ? (
          <EmptyState>No verbatim quotes captured.</EmptyState>
        ) : (
          <div className="linkrail">
            {quotes.map((q, i) => (
              <div className="card" key={i}>
                <blockquote style={{ margin: 0 }}>“{q.text}”</blockquote>
                <div className="small muted" style={{ marginTop: 8 }}>
                  {q.doc_id || "Unknown document"}
                  {q.locator ? <span> · {q.locator}</span> : null}
                  {q.tier ? (
                    <span style={{ marginLeft: 8 }}>
                      <TierBadge tier={q.tier} />
                    </span>
                  ) : null}
                </div>
              </div>
            ))}
          </div>
        )}

        <h3 style={{ margin: "20px 0 8px" }}>Entities</h3>
        {entities.length === 0 ? (
          <EmptyState>No entities extracted.</EmptyState>
        ) : (
          <div className="grid cols-3">
            {entities.map((e, i) => {
              const attrs = Object.entries(e.attributes ?? {});
              return (
                <div className="card" key={i}>
                  <div className="small muted">{e.kind || "entity"}</div>
                  <h3 style={{ margin: "2px 0 6px" }}>
                    {e.name || "—"}
                    {e.tier ? (
                      <span style={{ marginLeft: 8 }}>
                        <TierBadge tier={e.tier} />
                      </span>
                    ) : null}
                  </h3>
                  {attrs.length > 0 ? (
                    <dl className="kv">
                      {attrs.map(([k, v]) => (
                        <div key={k}>
                          <dt>{k}</dt>
                          <dd>{v == null ? "—" : String(v)}</dd>
                        </div>
                      ))}
                    </dl>
                  ) : (
                    <p className="small muted">No attributes recorded.</p>
                  )}
                  {e.sources && e.sources.length > 0 ? (
                    <div className="tiny muted" style={{ marginTop: 8 }}>
                      Sources: {e.sources.join(", ")}
                    </div>
                  ) : null}
                </div>
              );
            })}
          </div>
        )}
      </Section>
    </div>
  );
}
