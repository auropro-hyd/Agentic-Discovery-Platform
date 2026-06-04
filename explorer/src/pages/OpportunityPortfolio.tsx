import { useState } from "react";
import { useSearchParams } from "react-router-dom";
import { useDomainData } from "../lib/useDomainData";
import type { Opportunity } from "../lib/types";
import { QuadrantLabel, PatternLabel } from "../lib/types";
import { cx } from "../lib/cx";
import { QuadrantBoard } from "../charts/QuadrantBoard";
import { OpportunityCard } from "../cards/OpportunityCard";
import { EmptyState } from "../primitives/EmptyState";

/* The opportunity portfolio. A priority BOARD up top (shared hover selection with the grid),
 * a toolbar of pattern / quadrant filters + a value|feasibility sort (all state in the URL via
 * useSearchParams), then a two-up grid of opportunity cards for the filtered set. Every count is
 * read from the engine's JSON — nothing arithmetic is computed for display. */

const QUADRANT_KEYS = ["do_first", "plan_for", "consider", "deprioritise"] as const;

// Comparator rank for value/feasibility ratings — no arithmetic, a lookup only (high > medium > low).
// Unknown/missing ratings sort last (same rank as "low").
const LOW_RANK = 2;
const RATING_RANK: Record<string, number> = { high: 0, medium: 1, low: LOW_RANK };
function ratingRank(level: string | undefined): number {
  const key = (level || "").toLowerCase();
  const rank = RATING_RANK[key];
  return rank === undefined ? LOW_RANK : rank;
}

export default function OpportunityPortfolio() {
  const { store } = useDomainData();
  const opportunities: Opportunity[] = store.synthesis.opportunities ?? [];

  const [params, setParams] = useSearchParams();
  const [hoverId, setHoverId] = useState<string | null>(null);

  const pat = params.get("pat") ?? "all";
  const quad = params.get("quad") ?? "all";
  const sort = params.get("sort") === "feasibility" ? "feasibility" : "value";

  function setParam(key: string, value: string) {
    const next = new URLSearchParams(params);
    if (value === "all" || (key === "sort" && value === "value")) next.delete(key);
    else next.set(key, value);
    setParams(next, { replace: true });
  }

  // distinct patterns present, in first-seen order
  const patterns: string[] = [];
  for (const o of opportunities) {
    const p = (o.pattern || "").toLowerCase();
    if (p && !patterns.includes(p)) patterns.push(p);
  }

  const filtered = opportunities
    .filter((o) => pat === "all" || (o.pattern || "").toLowerCase() === pat)
    .filter((o) => quad === "all" || (o.matrix_quadrant || "").toLowerCase() === quad)
    .slice()
    .sort((a, b) => {
      const av = sort === "feasibility" ? a.feasibility_rating : a.value_rating;
      const bv = sort === "feasibility" ? b.feasibility_rating : b.value_rating;
      const ar = ratingRank(av);
      const br = ratingRank(bv);
      if (ar < br) return -1;
      if (ar > br) return 1;
      return a.id < b.id ? -1 : a.id > b.id ? 1 : 0;
    });

  return (
    <div>
      <header className="page-head">
        <div className="eyebrow">{store.domainLabel} · Portfolio</div>
        <h1>Opportunity portfolio</h1>
        <p className="lede">
          Identified opportunities placed on a value &times; feasibility priority board, then
          detailed below. Filter by pattern or quadrant and re-rank by value or feasibility — hover
          any card to highlight its match on the board.
        </p>
      </header>

      <QuadrantBoard
        domain={store.domain}
        opportunities={filtered}
        selected={hoverId}
        onHover={setHoverId}
      />

      <div className="toolbar">
        <label>Pattern</label>
        <button
          className={cx("chip", pat === "all" && "active")}
          onClick={() => setParam("pat", "all")}
        >
          All
        </button>
        {patterns.map((p) => (
          <button
            key={p}
            className={cx("chip", pat === p && "active")}
            onClick={() => setParam("pat", p)}
          >
            {PatternLabel[p] ?? p.replace(/_/g, " ")}
          </button>
        ))}

        <label>Quadrant</label>
        <select value={quad} onChange={(e) => setParam("quad", e.target.value)}>
          <option value="all">All</option>
          {QUADRANT_KEYS.map((q) => (
            <option key={q} value={q}>
              {QuadrantLabel[q]}
            </option>
          ))}
        </select>

        <label>Sort by</label>
        <select value={sort} onChange={(e) => setParam("sort", e.target.value)}>
          <option value="value">Value</option>
          <option value="feasibility">Feasibility</option>
        </select>

        <span className="count">
          Showing {filtered.length} of {opportunities.length}
        </span>
      </div>

      {filtered.length === 0 ? (
        <EmptyState>No opportunities match the current filters.</EmptyState>
      ) : (
        <div className="grid cols-2">
          {filtered.map((opp) => (
            <div
              key={opp.id}
              onMouseEnter={() => setHoverId(opp.id)}
              onMouseLeave={() => setHoverId(null)}
            >
              <OpportunityCard domain={store.domain} opp={opp} />
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
