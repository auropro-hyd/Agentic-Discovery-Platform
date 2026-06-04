import type { ReactNode } from "react";
import { cx } from "../lib/cx";
import { QuadrantLabel, PatternLabel } from "../lib/types";

/* Enum -> badge-class maps. They cover the FULL spec enum sets (not just observed values), so a
 * future bake with, say, a "deprioritise" opportunity renders correctly. Status colour is used
 * ONLY for severity/priority/readiness (the discipline inherited from the print suite). */

function Badge({ cls, children, title }: { cls: string; children: ReactNode; title?: string }) {
  return (
    <span className={cx("badge", cls)} title={title}>
      {children}
    </span>
  );
}

const SEVERITY_CLASS: Record<string, string> = {
  high: "b-high",
  critical: "b-crit",
  medium: "b-med",
  lower: "b-low",
  low: "b-low",
};
export function SeverityBadge({ severity }: { severity: string }) {
  const key = (severity || "").toLowerCase();
  if (!key) return null;
  return <Badge cls={SEVERITY_CLASS[key] ?? "b-neutral"}>{key}</Badge>;
}

const QUADRANT_CLASS: Record<string, string> = {
  do_first: "b-low", // green — highest priority
  plan_for: "b-pat", // blue
  consider: "b-med", // amber
  deprioritise: "b-neutral",
};
export function QuadrantBadge({ quadrant }: { quadrant: string }) {
  const key = (quadrant || "").toLowerCase();
  if (!key) return null;
  return <Badge cls={QUADRANT_CLASS[key] ?? "b-neutral"}>{QuadrantLabel[key] ?? key}</Badge>;
}

export function PatternChip({ pattern }: { pattern: string }) {
  const key = (pattern || "").toLowerCase();
  if (!key) return null;
  return <Badge cls="b-pat">{PatternLabel[key] ?? key.replace(/_/g, " ")}</Badge>;
}

export function CategoryBadge({ category }: { category: string }) {
  if (!category) return null;
  return <Badge cls="b-cat">{category}</Badge>;
}

const TIER_CLASS: Record<string, string> = { verified: "b-low", amber: "b-med", gap: "b-high" };
export function TierBadge({ tier }: { tier: string }) {
  const key = (tier || "").toLowerCase();
  if (!key) return null;
  return <Badge cls={TIER_CLASS[key] ?? "b-neutral"} title={`Confidence: ${key}`}>{key}</Badge>;
}

/* Rating pill — a level word (high/medium/low) with a coloured dot. Used for value/feasibility/
 * readiness. The score, when shown, is rendered separately via <GroundedNumber>. */
export function RatingPill({ level, label }: { level: string; label?: string }) {
  const key = (level || "").toLowerCase();
  const cls = key === "high" ? "high" : key === "medium" ? "medium" : key === "low" ? "low" : "na";
  if (!key) return null;
  return (
    <span className={cx("pill", cls)}>
      <span className="dot" />
      {label ? `${label}: ${key}` : key}
    </span>
  );
}
