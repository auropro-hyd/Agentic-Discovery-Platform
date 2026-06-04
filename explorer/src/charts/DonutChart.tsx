import type { ChartSpec } from "../lib/types";
import { arcPath, sum, SERIES, numericValue } from "./svg";

/* Draws a donut from a pre-aggregated ChartSpec (synthesis.charts[] with kind:"donut"). The
 * displayed legend value is the VERBATIM segment value from the JSON; only the arc geometry uses
 * the parsed numeric (drawing math, exempt). */
export function DonutChart({ spec }: { spec: ChartSpec }) {
  const segs = (spec.segments ?? []).filter((s) => s.label);
  const nums = segs.map((s) => numericValue(s.value));
  const total = sum(nums.map((n) => (Number.isFinite(n) ? n : 0)));
  if (!segs.length || total <= 0) return null;

  const cx = 70;
  const cy = 70;
  const rO = 64;
  const rI = 38;
  let angle = 0;
  const arcs = segs.map((_s, i) => {
    const n = Number.isFinite(nums[i]!) ? nums[i]! : 0;
    const sweep = (n / total) * 360;
    const path = arcPath(cx, cy, rO, rI, angle, angle + sweep);
    angle += sweep;
    return { path, color: SERIES[i % SERIES.length]! };
  });

  return (
    <div>
      {spec.title && <div className="chart-title">{spec.title}</div>}
      <div className="chartwrap">
        <svg viewBox="0 0 140 140" width="150" height="150" role="img" aria-label={spec.title}>
          {arcs.map((a, i) => (
            <path key={i} d={a.path} fill={a.color} />
          ))}
        </svg>
        <div className="chart-legend">
          {segs.map((s, i) => (
            <div className="li" key={i}>
              <span className="sw" style={{ background: SERIES[i % SERIES.length] }} />
              <span>
                {s.label}: <strong>{String(s.value ?? "")}</strong>
                {spec.unit === "percent" ? "%" : spec.unit ? ` ${spec.unit}` : ""}
              </span>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}
