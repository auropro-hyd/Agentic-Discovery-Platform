import type { ReactNode } from "react";

/* A KPI strip. Each stat shows a value (already a JSON-verbatim string/number from baseline_stats
 * — these are pre-formatted by the engine, e.g. "67.3%"), a label, and an optional sublabel.
 * Because baseline_stats.value is a verbatim string, no view math occurs. */

export interface StatItem {
  value: ReactNode;
  label: string;
  sublabel?: string;
  tone?: "navy" | "red" | "amber" | "blue" | "green";
}

export function StatGrid({ items }: { items: StatItem[] }) {
  if (!items.length) return null;
  return (
    <div className="statgrid">
      {items.map((it, i) => (
        <div className="stat" key={i}>
          <div className={`sv ${it.tone && it.tone !== "navy" ? it.tone : ""}`}>{it.value}</div>
          <div className="sl">{it.label}</div>
          {it.sublabel ? <div className="ss">{it.sublabel}</div> : null}
        </div>
      ))}
    </div>
  );
}
