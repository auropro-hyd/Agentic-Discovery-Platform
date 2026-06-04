import { Link } from "react-router-dom";
import { useDomainData } from "../lib/useDomainData";
import { RoadmapTimeline } from "../charts/RoadmapTimeline";
import { PlanningRow } from "../primitives/PlanningBadge";
import { EmptyState, Section } from "../primitives/EmptyState";

/* The phased plan. The timeline itself is honest about its limits (depends_on is a label, not a
 * resolved link, and opportunity_id does not match the opportunity namespace). We surface only the
 * roadmap-relevant planning assumptions (date / sequence / cadence) here, routing to the full
 * register for the rest. Every figure shown is a verbatim engine string — nothing is computed. */

const ROADMAP_KINDS = new Set(["date", "sequence", "cadence"]);
const MAX_ASSUMPTIONS = 5;

export default function RoadmapPage() {
  const { store } = useDomainData();
  const { synthesis, domain } = store;

  const roadmap = synthesis.roadmap ?? [];
  const sequencing = synthesis.sequencing_rationale;
  const dependencies = synthesis.dependency_notes;

  const planningAssumptions = (synthesis.planning_assumptions ?? []).filter((pa) =>
    ROADMAP_KINDS.has((pa.kind || "").toLowerCase()),
  );
  const shownAssumptions = planningAssumptions.slice(0, MAX_ASSUMPTIONS);

  return (
    <div>
      <header className="page-head">
        <div className="eyebrow">Roadmap</div>
        <h1>{store.domainLabel} — phased delivery plan</h1>
        <p className="lede">
          A horizon-based sequence of themes and items, with dependencies and sequencing rationale
          drawn from the discovery synthesis.
        </p>
      </header>

      {roadmap.length === 0 ? (
        <EmptyState>No roadmap horizons were recorded for this domain.</EmptyState>
      ) : (
        <>
          <RoadmapTimeline horizons={roadmap} />
          <p className="small muted">
            Dependencies are shown as labelled notes; roadmap items are not yet linked to specific
            opportunities in the source data.
          </p>
        </>
      )}

      {sequencing && (
        <Section title="Sequencing rationale">
          <div className="panel">
            <p style={{ margin: 0 }}>{sequencing}</p>
          </div>
        </Section>
      )}

      {dependencies && (
        <Section title="Dependencies">
          <div className="panel">
            <p style={{ margin: 0 }}>{dependencies}</p>
          </div>
        </Section>
      )}

      <Section title="Planning assumptions in this plan">
        {shownAssumptions.length === 0 ? (
          <EmptyState>
            No roadmap-relevant planning assumptions (dates, sequence, or cadence) were recorded for
            this domain.
          </EmptyState>
        ) : (
          <>
            <p className="small muted">
              These are proposed planning inputs behind the timeline — not discovered fact.
            </p>
            <div className="grid">
              {shownAssumptions.map((pa, i) => (
                <PlanningRow key={i} assumption={pa} />
              ))}
            </div>
            <div className="linkrail">
              <Link to={`/${domain}/assumptions`}>See all planning assumptions →</Link>
            </div>
          </>
        )}
      </Section>
    </div>
  );
}
