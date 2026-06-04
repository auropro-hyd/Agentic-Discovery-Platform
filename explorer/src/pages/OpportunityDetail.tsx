import { Link, useParams } from "react-router-dom";
import { useDomainData } from "../lib/useDomainData";
import { PatternChip, QuadrantBadge, RatingPill } from "../primitives/badges";
import { EmptyState, Section } from "../primitives/EmptyState";
import { BackChip } from "../layout/Breadcrumb";
import { BeforeAfterProcess } from "../charts/BeforeAfterProcess";

/* Detail for a single opportunity. Reads :oppId from the route and resolves it from
 * store.opportunityById; an unknown id degrades to an .empty notice rather than crashing.
 * Every figure is rendered verbatim from the engine's strings (business_impact.quantified[].text);
 * count-variable list sections all guard for empty. The "Addresses" linkrail cross-links back to
 * the pain point this opportunity targets, but only when that id actually exists in this domain. */
export default function OpportunityDetail() {
  const { store } = useDomainData();
  const { oppId } = useParams();

  const opp = oppId ? store.opportunityById.get(oppId) : undefined;
  if (!opp) {
    return (
      <div>
        <BackChip to={`/${store.domain}/opportunities`} label="Opportunity portfolio" />
        <EmptyState>No such opportunity in this domain.</EmptyState>
      </div>
    );
  }

  const impact = opp.business_impact;
  const impactQuant = impact?.quantified ?? [];

  const targetId = (opp.addresses_pain_point || "").trim();
  const targetPp = targetId ? store.painPointById.get(targetId) : undefined;

  const kvRows: Array<{ term: string; value: string }> = [
    { term: "Implementation approach", value: opp.implementation_approach },
    { term: "Expected behaviour", value: opp.expected_behaviour },
    { term: "Escalation", value: opp.escalation },
    { term: "Technical complexity", value: opp.technical_complexity },
    { term: "Data readiness", value: opp.data_readiness },
    { term: "Operational readiness", value: opp.operational_readiness },
  ].filter((r) => r.value);

  const tagSections: Array<{ title: string; items: string[] }> = [
    { title: "Personas", items: opp.personas ?? [] },
    { title: "Required integrations", items: opp.required_integrations ?? [] },
    { title: "Knowledge sources", items: opp.knowledge_sources ?? [] },
    { title: "Document formats", items: opp.document_formats ?? [] },
    { title: "Success metrics", items: opp.success_metrics ?? [] },
    { title: "Risks", items: opp.risks ?? [] },
  ];

  return (
    <div>
      <BackChip to={`/${store.domain}/opportunities`} label="Opportunity portfolio" />

      <header className="page-head">
        <div className="eyebrow">Opportunity · {opp.id}</div>
        <h1>{opp.title}</h1>
        <div className="taglist" style={{ marginTop: 8 }}>
          {opp.pattern ? <PatternChip pattern={opp.pattern} /> : null}
          {opp.matrix_quadrant ? <QuadrantBadge quadrant={opp.matrix_quadrant} /> : null}
          {opp.value_rating ? <RatingPill level={opp.value_rating} label="Value" /> : null}
          {opp.feasibility_rating ? (
            <RatingPill level={opp.feasibility_rating} label="Feasibility" />
          ) : null}
        </div>
        {opp.overview ? <p className="lede">{opp.overview}</p> : null}
      </header>

      {targetPp ? (
        <Section title="Addresses">
          <div className="linkrail">
            <Link to={`/${store.domain}/pain-points/${targetPp.id}`}>
              {targetPp.id} · {targetPp.title}
            </Link>
          </div>
        </Section>
      ) : null}

      <Section title="Business impact">
        {impact && (impact.narrative || impactQuant.length > 0 || impact.derivation) ? (
          <div className="panel">
            {impact.narrative ? <p>{impact.narrative}</p> : null}
            {impactQuant.length > 0 ? (
              <ul>
                {impactQuant.map((q, i) => (
                  <li key={i}>{q.text}</li>
                ))}
              </ul>
            ) : null}
            {impact.derivation ? (
              <p className="muted small">Derivation: {impact.derivation}</p>
            ) : null}
          </div>
        ) : (
          <EmptyState />
        )}
      </Section>

      <Section title="How it works today vs. with the opportunity">
        {(opp.before_process?.length ?? 0) === 0 &&
        (opp.after_process?.length ?? 0) === 0 ? (
          <EmptyState />
        ) : (
          <BeforeAfterProcess opportunity={opp} />
        )}
      </Section>

      <Section title="Delivery profile">
        {kvRows.length === 0 ? (
          <EmptyState />
        ) : (
          <dl className="kv">
            {kvRows.map((r) => [
              <dt key={`${r.term}-t`}>{r.term}</dt>,
              <dd key={`${r.term}-d`}>{r.value}</dd>,
            ])}
          </dl>
        )}
      </Section>

      {tagSections.map((sec) =>
        sec.items.length === 0 ? null : (
          <Section key={sec.title} title={sec.title}>
            <div className="taglist">
              {sec.items.map((item, i) => (
                <span className="tag" key={i}>
                  {item}
                </span>
              ))}
            </div>
          </Section>
        ),
      )}
    </div>
  );
}
