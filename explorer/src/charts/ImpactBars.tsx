import { Link } from "react-router-dom";
import type { PainPoint } from "../lib/types";

/* Pain points ranked by impact — horizontal SVG bars, coloured by severity, longest (most
 * material) on top. Bar length is purely positional (a rank-ordered ladder, not a measured
 * magnitude), so it implies no fabricated number; the displayed label is the verbatim title. */

const SEV_FILL: Record<string, string> = {
  high: "var(--red)",
  critical: "var(--red)",
  medium: "var(--amber)",
  lower: "var(--green)",
  low: "var(--green)",
};

export function ImpactBars({ domain, painPoints }: { domain: string; painPoints: PainPoint[] }) {
  const items = [...(painPoints ?? [])]
    .filter((p) => p.id)
    .sort((a, b) => (a.impact_rank ?? 99) - (b.impact_rank ?? 99));
  if (items.length < 2) return null;

  const n = items.length;
  const ROW = 34;
  const W = 720;
  const LBL = 44;
  const H = n * ROW + 12;
  // longest bar for rank 1, shrinking down the ladder — positional only
  const widthFor = (i: number) => LBL + ((W - LBL - 20) * (n - i)) / n;

  return (
    <div className="fig">
      <svg viewBox={`0 0 ${W} ${H}`} width="100%" role="img" aria-label="Pain points by impact rank">
        {items.map((p, i) => {
          const y = 6 + i * ROW;
          const fill = SEV_FILL[(p.severity || "").toLowerCase()] ?? "var(--blue-mid)";
          return (
            <g key={p.id}>
              <rect x={LBL} y={y} width={widthFor(i) - LBL} height={ROW - 12} rx="4" fill={fill} opacity="0.9" />
              <text x={LBL - 8} y={y + (ROW - 12) / 2 + 4} textAnchor="end" fontSize="11" fontWeight="800" fill="var(--navy)">
                {p.id}
              </text>
              <text x={LBL + 10} y={y + (ROW - 12) / 2 + 4} fontSize="11" fontWeight="600" fill="#fff">
                {clip(p.title, 78)}
              </text>
            </g>
          );
        })}
      </svg>
      <div className="fig-foot">
        Pain points ranked most-material first (bar length is rank order, not a measured value).{" "}
        <Link to={`/suite/${domain}/pain-points`}>See all →</Link>
      </div>
    </div>
  );
}

function clip(s: string, n: number): string {
  return s.length > n ? s.slice(0, n - 1) + "…" : s;
}
