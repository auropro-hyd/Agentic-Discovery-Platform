import type { Opportunity } from "../lib/types";

/* Two side-by-side lanes — the current process vs the proposed process — from an opportunity's
 * before_process / after_process step arrays. Pure render; the "after" lane is accented blue. */
type Step = Opportunity["before_process"][number];

function Lane({ title, steps, after }: { title: string; steps: Step[]; after?: boolean }) {
  return (
    <div className={`lane ${after ? "after" : "before"}`}>
      <h4>
        {after ? "→ " : ""}
        {title}
      </h4>
      {steps.length === 0 ? (
        <p className="small muted">Not specified.</p>
      ) : (
        steps.map((s, i) => (
          <div className="step" key={i}>
            {s.actor && <div className="actor">{s.actor}</div>}
            <div className="desc">{s.description}</div>
          </div>
        ))
      )}
    </div>
  );
}

export function BeforeAfterProcess({ opportunity }: { opportunity: Opportunity }) {
  const before = opportunity.before_process ?? [];
  const after = opportunity.after_process ?? [];
  if (!before.length && !after.length) return null;
  return (
    <div className="ba">
      <Lane title="Today" steps={before} />
      <Lane title="With the opportunity" steps={after} after />
    </div>
  );
}
