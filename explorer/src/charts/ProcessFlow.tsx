/* A simple left-to-right process flow from current_state.process_flow (or any {actor,description}
 * step list). Pure render — nodes connected by arrows. Wraps on narrow screens. */

interface FlowStep {
  actor?: string;
  description?: string;
  step?: string;
  label?: string;
}

export function ProcessFlow({ steps }: { steps: FlowStep[] }) {
  if (!steps?.length) return null;
  return (
    <div className="flow">
      {steps.map((s, i) => (
        <span key={i} style={{ display: "contents" }}>
          <div className="node">
            {(s.actor || s.step) && <div className="a">{s.actor || s.step}</div>}
            <div className="d">{s.description || s.label || ""}</div>
          </div>
          {i < steps.length - 1 && <span className="arrow">→</span>}
        </span>
      ))}
    </div>
  );
}
