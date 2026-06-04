import type { ChartSpec } from "../lib/types";
import { SERIES, numericValue } from "./svg";

/* Horizontal bars from a pre-aggregated ChartSpec (kind:"bar"). Bar WIDTH is geometry (drawing
 * math, exempt); the displayed value is the verbatim segment value. */
export function BarChart({ spec }: { spec: ChartSpec }) {
  const segs = (spec.segments ?? []).filter((s) => s.label);
  if (!segs.length) return null;
  const nums = segs.map((s) => numericValue(s.value));
  const max = Math.max(...nums.map((n) => (Number.isFinite(n) ? n : 0)), 0);
  if (max <= 0) return null;

  return (
    <div>
      {spec.title && <div className="chart-title">{spec.title}</div>}
      <div style={{ display: "flex", flexDirection: "column", gap: 8 }}>
        {segs.map((s, i) => {
          const n = Number.isFinite(nums[i]!) ? nums[i]! : 0;
          const pct = (n / max) * 100; // geometry only
          return (
            <div key={i} style={{ display: "grid", gridTemplateColumns: "160px 1fr auto", gap: 10, alignItems: "center" }}>
              <span className="small" style={{ color: "var(--ink)" }}>{s.label}</span>
              <span style={{ background: "var(--bg-alt)", borderRadius: 5, height: 16, overflow: "hidden" }}>
                <span style={{ display: "block", height: "100%", width: `${pct}%`, background: SERIES[i % SERIES.length] }} />
              </span>
              <strong className="small" style={{ fontVariantNumeric: "tabular-nums" }}>
                {String(s.value ?? "")}
                {spec.unit === "percent" ? "%" : spec.unit ? ` ${spec.unit}` : ""}
              </strong>
            </div>
          );
        })}
      </div>
    </div>
  );
}

/** Render whichever chart kind a ChartSpec declares. */
export function Chart({ spec }: { spec: ChartSpec }) {
  if ((spec.kind || "").toLowerCase() === "bar") return <BarChart spec={spec} />;
  return null; // donut handled by DonutChart caller; unknown kinds omit themselves
}
