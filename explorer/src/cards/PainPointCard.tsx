import { Link } from "react-router-dom";
import type { PainPoint } from "../lib/types";
import { SeverityBadge, CategoryBadge } from "../primitives/badges";

/* A pain-point summary card for the list view. UI-chrome only (no client figures computed). */
export function PainPointCard({ domain, pp }: { domain: string; pp: PainPoint }) {
  return (
    <Link to={`/${domain}/pain-points/${pp.id}`} className="card">
      <div className="card-meta">
        <span className="tiny muted" style={{ fontWeight: 800, color: "var(--blue)" }}>{pp.id}</span>
        <SeverityBadge severity={pp.severity} />
        {pp.category && <CategoryBadge category={pp.category} />}
      </div>
      <div className="card-title">{pp.title}</div>
      <div className="card-body">{pp.description}</div>
      {pp.business_consequence && (
        <p className="small muted" style={{ margin: "8px 0 0" }}>
          <strong>Consequence:</strong> {pp.business_consequence}
        </p>
      )}
    </Link>
  );
}
