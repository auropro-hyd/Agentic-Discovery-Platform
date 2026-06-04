import { Link } from "react-router-dom";
import type { Opportunity } from "../lib/types";
import { PatternChip, QuadrantBadge, RatingPill } from "../primitives/badges";

/* An opportunity summary card for the portfolio grid. */
export function OpportunityCard({ domain, opp }: { domain: string; opp: Opportunity }) {
  return (
    <Link to={`/suite/${domain}/opportunities/${opp.id}`} className="card">
      <div className="card-meta">
        <span className="tiny muted" style={{ fontWeight: 800, color: "var(--blue)" }}>{opp.id}</span>
        {opp.pattern && <PatternChip pattern={opp.pattern} />}
        {opp.matrix_quadrant && <QuadrantBadge quadrant={opp.matrix_quadrant} />}
      </div>
      <div className="card-title">{opp.title}</div>
      <div className="card-body">{opp.overview}</div>
      <div className="card-meta" style={{ marginTop: 10, marginBottom: 0 }}>
        {opp.value_rating && <RatingPill level={opp.value_rating} label="Value" />}
        {opp.feasibility_rating && <RatingPill level={opp.feasibility_rating} label="Feasibility" />}
      </div>
    </Link>
  );
}
