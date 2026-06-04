import type { PlanningAssumption } from "../lib/types";

/* THE sacred path for forward-looking content. A planning assumption is NOT discovered fact:
 * it is a clearly-labelled planning input (a date / owner / SLA / threshold / cadence / cost /
 * sequence the engine proposes, grounded by a `basis`). It renders ONLY through this dashed-amber
 * badge (mirroring the print suite's .b-plan), so it can never be skimmed as a measured number.
 * No page renders planning_assumptions as plain prose. */

const KIND_LABEL: Record<string, string> = {
  date: "Date",
  owner: "Owner",
  sla: "SLA",
  threshold: "Threshold",
  cadence: "Cadence",
  cost: "Cost",
  sequence: "Sequence",
};

export function PlanningBadge({ kind }: { kind?: string }) {
  const k = (kind || "").toLowerCase();
  return (
    <span className="badge b-plan" title="A planning assumption — proposed, not discovered fact">
      Planning assumption{k && KIND_LABEL[k] ? ` · ${KIND_LABEL[k]}` : ""}
    </span>
  );
}

/** A full planning-assumption row: the badge, the statement, and its grounding basis. */
export function PlanningRow({ assumption }: { assumption: PlanningAssumption }) {
  return (
    <div className="panel" style={{ borderLeft: "3px dashed var(--amber)" }}>
      <PlanningBadge kind={assumption.kind} />
      <p style={{ margin: "8px 0 4px", fontWeight: 600, color: "var(--navy)" }}>{assumption.statement}</p>
      {assumption.basis && (
        <p className="small muted" style={{ margin: 0 }}>
          <strong>Basis:</strong> {assumption.basis}
        </p>
      )}
    </div>
  );
}
