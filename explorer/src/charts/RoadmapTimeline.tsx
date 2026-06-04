import type { RoadmapHorizon } from "../lib/types";

/* H1/H2/H3 swimlanes. IMPORTANT (grounding/honesty): roadmap items are NOT clickable by
 * opportunity_id — verified that opportunity_id is null in o2c and a non-matching slug namespace
 * in p2p, so a "link to opportunity" would resolve to nothing. depends_on is shown as labelled
 * text chips, NOT as resolved arrows to other items. A future pipeline change adding real ids
 * would upgrade this to a clickable dependency graph. */

export function RoadmapTimeline({ horizons }: { horizons: RoadmapHorizon[] }) {
  if (!horizons.length) return null;
  return (
    <div className="roadmap">
      {horizons.map((h, i) => (
        <div className="rm-lane" key={i}>
          <div className="rm-lane-head">
            <div className="h">{h.horizon || `Horizon ${i + 1}`}</div>
            {h.window && <div className="w">{h.window}</div>}
            {h.theme && <div className="t">{h.theme}</div>}
          </div>
          {h.items.length === 0 ? (
            <div className="rm-item small muted">No items in this horizon.</div>
          ) : (
            h.items.map((it, j) => (
              <div className="rm-item" key={j}>
                <div className="t">{it.title}</div>
                {it.rationale && <div className="r">{it.rationale}</div>}
                {it.depends_on && it.depends_on.length > 0 && (
                  <div className="rm-dep">
                    {it.depends_on.map((d, k) => (
                      <span className="tag tiny" key={k}>
                        depends on: {d}
                      </span>
                    ))}
                  </div>
                )}
              </div>
            ))
          )}
        </div>
      ))}
    </div>
  );
}
