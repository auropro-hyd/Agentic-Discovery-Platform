/* SVG geometry helpers. This file is EXEMPT from the no-arithmetic grounding rule (see
 * eslint.config.js) because the math here is pixel layout, not client figures. Charts in this
 * folder must take ALREADY-AGGREGATED values from the JSON and only do drawing geometry. */

/** sum of numeric segment values (for donut proportions) — drawing math, not a displayed figure. */
export function sum(values: number[]): number {
  return values.reduce((a, b) => a + b, 0);
}

/** polar -> cartesian for donut arcs. */
export function polar(cx: number, cy: number, r: number, angleDeg: number): [number, number] {
  const a = ((angleDeg - 90) * Math.PI) / 180;
  return [cx + r * Math.cos(a), cy + r * Math.sin(a)];
}

/** an SVG arc path for a donut segment between two angles. */
export function arcPath(cx: number, cy: number, rOuter: number, rInner: number, startDeg: number, endDeg: number): string {
  const [sx, sy] = polar(cx, cy, rOuter, endDeg);
  const [ex, ey] = polar(cx, cy, rOuter, startDeg);
  const [isx, isy] = polar(cx, cy, rInner, endDeg);
  const [iex, iey] = polar(cx, cy, rInner, startDeg);
  const large = endDeg - startDeg <= 180 ? 0 : 1;
  return [
    `M ${sx} ${sy}`,
    `A ${rOuter} ${rOuter} 0 ${large} 0 ${ex} ${ey}`,
    `L ${iex} ${iey}`,
    `A ${rInner} ${rInner} 0 ${large} 1 ${isx} ${isy}`,
    "Z",
  ].join(" ");
}

export const SERIES = ["var(--c1)", "var(--c2)", "var(--c3)", "var(--c4)", "var(--c5)"];

/** parse a chart segment value that may be a number or a numeric string ("67.3"/"€12.4m" → NaN).
 *  Used only for DRAWING proportions; the displayed label keeps the verbatim value. */
export function numericValue(v: number | string | undefined): number {
  if (typeof v === "number") return v;
  if (typeof v === "string") {
    const m = v.replace(/[, ]/g, "").match(/-?\d+(\.\d+)?/);
    return m ? parseFloat(m[0]) : NaN;
  }
  return NaN;
}
