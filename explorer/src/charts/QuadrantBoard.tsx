import { Link } from "react-router-dom";
import type { Opportunity } from "../lib/types";
import { QuadrantLabel } from "../lib/types";
import { cx } from "../lib/cx";

/* The portfolio hero. NOT a scatter plot — verified that value_score barely varies across
 * opportunities (all 4 in o2c), so a value×feasibility scatter would be a misleading stack of
 * overlapping dots. Instead a priority BOARD: opportunities grouped into their matrix_quadrant
 * lane, each card showing its value/feasibility scores as honest labelled tags. Hovering a card
 * highlights the matching card in the grid below (shared selection lifted to the parent). */

const QUADRANT_ORDER = ["do_first", "plan_for", "consider", "deprioritise"] as const;
const QUADRANT_TONE: Record<string, string> = {
  do_first: "qb-green",
  plan_for: "qb-blue",
  consider: "qb-amber",
  deprioritise: "qb-grey",
};

export function QuadrantBoard({
  domain,
  opportunities,
  selected,
  onHover,
}: {
  domain: string;
  opportunities: Opportunity[];
  selected?: string | null;
  onHover?: (id: string | null) => void;
}) {
  // group by quadrant; unknown/empty quadrant falls into a trailing "Unclassified" lane
  const lanes = QUADRANT_ORDER.map((q) => ({
    key: q,
    label: QuadrantLabel[q] ?? q,
    items: opportunities.filter((o) => (o.matrix_quadrant || "").toLowerCase() === q),
  })).filter((l) => l.items.length > 0);

  const classified = new Set(lanes.flatMap((l) => l.items.map((o) => o.id)));
  const rest = opportunities.filter((o) => !classified.has(o.id));
  if (rest.length) lanes.push({ key: "deprioritise", label: "Unclassified", items: rest });

  if (!opportunities.length) return null;

  return (
    <div className="qboard">
      {lanes.map((lane) => (
        <div key={lane.label} className={cx("qb-lane", QUADRANT_TONE[lane.key])}>
          <div className="qb-lane-head">
            <span className="qb-lane-title">{lane.label}</span>
            <span className="qb-lane-count">{lane.items.length}</span>
          </div>
          <div className="qb-cards">
            {lane.items.map((o) => (
              <Link
                key={o.id}
                to={`/${domain}/opportunities/${o.id}`}
                className={cx("qb-card", selected === o.id && "is-highlight")}
                onMouseEnter={() => onHover?.(o.id)}
                onMouseLeave={() => onHover?.(null)}
              >
                <span className="qb-card-id">{o.id}</span>
                <span className="qb-card-title">{o.title}</span>
                <span className="qb-card-tags">
                  {o.value_rating && <span className="qb-tag">Value: {o.value_rating}</span>}
                  {o.feasibility_rating && <span className="qb-tag">Feasibility: {o.feasibility_rating}</span>}
                </span>
              </Link>
            ))}
          </div>
        </div>
      ))}
    </div>
  );
}
