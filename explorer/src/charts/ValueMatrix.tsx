import { Link } from "react-router-dom";
import type { Opportunity } from "../lib/types";

/* Value × feasibility matrix — the classic prioritisation quadrant. value_score (1–5) on the
 * vertical axis, feasibility_score on the horizontal; each opportunity a bubble coloured by its
 * matrix_quadrant. Scores are plotted verbatim from the JSON (no rescaling). When several share a
 * cell, a small deterministic offset by index spreads them so all stay visible. */

const QUAD_FILL: Record<string, string> = {
  do_first: "var(--green)",
  plan_for: "var(--blue)",
  consider: "var(--amber)",
  deprioritise: "var(--muted)",
};

export function ValueMatrix({ domain, opportunities }: { domain: string; opportunities: Opportunity[] }) {
  const items = (opportunities ?? []).filter(
    (o) => o.id && typeof o.value_score === "number" && typeof o.feasibility_score === "number",
  );
  if (items.length < 2) return null;

  const W = 520;
  const H = 420;
  const PAD = 54;
  const plotW = W - PAD - 24;
  const plotH = H - PAD - 30;
  // map a 1–5 score to a pixel coord (positional only — not a computed client figure)
  const xOf = (s: number) => PAD + (plotW * (s - 0.5)) / 5;
  const yOf = (s: number) => H - PAD - (plotH * (s - 0.5)) / 5;

  // deterministic offset for same-cell collisions, by index within the cell
  const cellSeen: Record<string, number> = {};

  return (
    <div className="fig">
      <svg viewBox={`0 0 ${W} ${H}`} width="100%" role="img" aria-label="Value vs feasibility matrix">
        {/* quadrant tints */}
        <rect x={PAD} y={H - PAD - plotH} width={plotW / 2} height={plotH / 2} fill="var(--green-bg)" />
        <rect x={PAD + plotW / 2} y={H - PAD - plotH} width={plotW / 2} height={plotH / 2} fill="var(--note-bg)" />
        <rect x={PAD} y={H - PAD - plotH / 2} width={plotW / 2} height={plotH / 2} fill="var(--amber-bg)" />
        <rect x={PAD + plotW / 2} y={H - PAD - plotH / 2} width={plotW / 2} height={plotH / 2} fill="var(--bg-alt)" />
        {/* axes */}
        <line x1={PAD} y1={H - PAD} x2={W - 18} y2={H - PAD} stroke="var(--line)" strokeWidth="1.2" />
        <line x1={PAD} y1={H - PAD} x2={PAD} y2={H - PAD - plotH} stroke="var(--line)" strokeWidth="1.2" />
        <text x={PAD + plotW / 2} y={H - 10} textAnchor="middle" fontSize="11" fontWeight="700" fill="var(--muted)">
          Feasibility →
        </text>
        <text x={16} y={H - PAD - plotH / 2} textAnchor="middle" fontSize="11" fontWeight="700" fill="var(--muted)" transform={`rotate(-90 16 ${H - PAD - plotH / 2})`}>
          Business value →
        </text>
        {/* quadrant labels */}
        <text x={PAD + plotW / 4} y={H - PAD - plotH + 16} textAnchor="middle" fontSize="9" fontWeight="800" fill="var(--green)" opacity="0.7">PLAN FOR</text>
        <text x={PAD + (plotW * 3) / 4} y={H - PAD - plotH + 16} textAnchor="middle" fontSize="9" fontWeight="800" fill="var(--blue)" opacity="0.7">DO FIRST</text>
        <text x={PAD + plotW / 4} y={H - PAD - 8} textAnchor="middle" fontSize="9" fontWeight="800" fill="var(--amber)" opacity="0.6">RECONSIDER</text>
        <text x={PAD + (plotW * 3) / 4} y={H - PAD - 8} textAnchor="middle" fontSize="9" fontWeight="800" fill="var(--muted)" opacity="0.7">QUICK WIN</text>
        {/* bubbles */}
        {items.map((o) => {
          const vs = o.value_score as number;
          const fs = o.feasibility_score as number;
          const key = `${vs}-${fs}`;
          const k = cellSeen[key] ?? 0;
          cellSeen[key] = k + 1;
          const off = k === 0 ? 0 : 14 * (k % 2 === 1 ? 1 : -1) * Math.ceil(k / 2);
          const cx = xOf(fs) + off;
          const cy = yOf(vs) + (k > 0 ? 12 * Math.ceil(k / 2) : 0);
          const fill = QUAD_FILL[(o.matrix_quadrant || "").toLowerCase()] ?? "var(--blue)";
          return (
            <Link key={o.id} to={`/suite/${domain}/opportunities/${o.id}`}>
              <circle cx={cx} cy={cy} r="15" fill={fill} opacity="0.85" stroke="#fff" strokeWidth="2">
                <title>{`${o.id}: ${o.title} — value ${vs}/5, feasibility ${fs}/5`}</title>
              </circle>
              <text x={cx} y={cy + 4} textAnchor="middle" fontSize="9.5" fontWeight="800" fill="#fff" pointerEvents="none">
                {o.id.replace(/[^0-9]/g, "") || o.id.slice(0, 3)}
              </text>
            </Link>
          );
        })}
      </svg>
      <div className="fig-foot">Each bubble is an opportunity (hover for value/feasibility); colour = priority quadrant.</div>
    </div>
  );
}
