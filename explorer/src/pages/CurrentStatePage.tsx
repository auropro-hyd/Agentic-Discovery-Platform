import { useDomainData } from "../lib/useDomainData";
import { Section, EmptyState } from "../primitives/EmptyState";
import { StatGrid, type StatItem } from "../primitives/StatGrid";
import { DataTable } from "../primitives/DataTable";
import { ProcessFlow } from "../charts/ProcessFlow";
import { DonutChart } from "../charts/DonutChart";
import { BarChart } from "../charts/BarChart";
import { BoundedContextMap } from "../charts/BoundedContextMap";

/* current_state is count-agnostic: o2c has rich data_tables/handoffs, p2p has far fewer and some
 * sections are empty. Every section is guarded and rendered only when it has rows. Several
 * current_state arrays are typed as any[] in the schema, so we read them with light guards and
 * render verbatim — no view-layer math (HARD RULE 1). */

interface OwnershipRow {
  activity?: string;
  responsible?: string;
  accountable?: string;
  consulted?: string;
  informed?: string;
}

interface HandoffRow {
  from_step?: string;
  to_step?: string;
  mechanism?: string;
}

interface FormatRow {
  label?: string;
  description?: string;
  examples?: unknown;
}

function asArray(v: unknown): Record<string, unknown>[] {
  return Array.isArray(v) ? (v as Record<string, unknown>[]) : [];
}

export default function CurrentStatePage() {
  const { store } = useDomainData();
  const cs = store.synthesis.current_state;

  if (!cs) {
    return (
      <main>
        <header className="page-head">
          <div className="eyebrow">Current state</div>
          <h1>How {store.domainLabel} runs today</h1>
        </header>
        <EmptyState>No current-state baseline was captured for this domain.</EmptyState>
      </main>
    );
  }

  const baselineStats: StatItem[] = (cs.baseline_stats ?? [])
    .filter((s) => s && (s.value !== undefined && s.value !== null && s.value !== ""))
    .map((s) => ({
      value: String(s.value),
      label: s.label ?? "",
      sublabel: s.sublabel || undefined,
    }));

  const dataTables = cs.data_tables ?? [];
  const processFlow = asArray(cs.process_flow);
  const ownership = asArray(cs.ownership_map) as OwnershipRow[];
  const systems = asArray(cs.system_inventory);
  const handoffs = asArray(cs.handoff_catalogue) as HandoffRow[];
  const formats = asArray(cs.format_taxonomy) as FormatRow[];

  /* Pre-aggregated charts come from synthesis.charts[] (currently EMPTY in both shipped domains).
   * Guarded by charts.length so the Section never renders empty; lights up if the engine bakes
   * charts later. Chart geometry math lives in the chart components under charts/ (ESLint-exempt);
   * this page only dispatches by kind and passes the verbatim spec through. */
  const charts = store.synthesis.charts ?? [];

  const hasOverview = Boolean(cs.domain_overview) || Boolean(cs.process_summary);

  return (
    <main>
      <header className="page-head">
        <div className="eyebrow">Current state</div>
        <h1>How {store.domainLabel} runs today</h1>
        {cs.domain_overview ? <p className="lede">{cs.domain_overview}</p> : null}
      </header>

      {baselineStats.length > 0 ? <StatGrid items={baselineStats} /> : null}

      {hasOverview ? (
        <Section title="Overview">
          {cs.domain_overview ? <p>{cs.domain_overview}</p> : null}
          {cs.process_summary ? <p>{cs.process_summary}</p> : null}
        </Section>
      ) : null}

      {(cs.bounded_contexts ?? []).length > 1 ? (
        <Section title="Domain landscape">
          <p className="muted small">
            The subdomains that make up this domain, how each is classified, who owns it, and how
            they relate — the bounded-context view of the current state.
          </p>
          <BoundedContextMap contexts={cs.bounded_contexts ?? []} domainLabel={store.domainLabel} />
        </Section>
      ) : null}

      {processFlow.length > 0 ? (
        <Section title="Process flow">
          <ProcessFlow steps={processFlow} />
        </Section>
      ) : null}

      {dataTables.length > 0 ? (
        <Section title="Key data">
          {dataTables.map((t, i) => (
            <DataTable table={t} key={i} />
          ))}
        </Section>
      ) : null}

      {charts.length > 0 ? (
        <Section title="Charts">
          {charts.map((c, i) =>
            (c.kind || "").toLowerCase() === "donut" ? (
              <DonutChart spec={c} key={i} />
            ) : (
              <BarChart spec={c} key={i} />
            ),
          )}
        </Section>
      ) : null}

      {ownership.length > 0 ? (
        <Section title="Ownership (RACI)">
          <table className="dt">
            <thead>
              <tr>
                <th>Activity</th>
                <th>Responsible</th>
                <th>Accountable</th>
                <th>Consulted</th>
                <th>Informed</th>
              </tr>
            </thead>
            <tbody>
              {ownership.map((r, i) => (
                <tr key={i}>
                  <td>{r.activity || "—"}</td>
                  <td>{r.responsible || "—"}</td>
                  <td>{r.accountable || "—"}</td>
                  <td>{r.consulted || "—"}</td>
                  <td>{r.informed || "—"}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </Section>
      ) : null}

      {systems.length > 0 ? (
        <Section title="Systems">
          <div className="grid cols-2">
            {systems.map((sys, i) => {
              const entries = Object.entries(sys).filter(
                ([, value]) => value !== undefined && value !== null && value !== "",
              );
              if (!entries.length) return null;
              return (
                <div className="card" key={i}>
                  <dl className="kv">
                    {entries.map(([key, value]) => (
                      <div key={key}>
                        <dt>{key}</dt>
                        <dd>{String(value)}</dd>
                      </div>
                    ))}
                  </dl>
                </div>
              );
            })}
          </div>
        </Section>
      ) : null}

      {handoffs.length > 0 ? (
        <Section title="Handoffs">
          <table className="dt">
            <thead>
              <tr>
                <th>From</th>
                <th>To</th>
                <th>Mechanism</th>
              </tr>
            </thead>
            <tbody>
              {handoffs.map((h, i) => (
                <tr key={i}>
                  <td>{h.from_step || "—"}</td>
                  <td>{h.to_step || "—"}</td>
                  <td>{h.mechanism || "—"}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </Section>
      ) : null}

      {formats.length > 0 ? (
        <Section title="Information formats">
          <div className="grid cols-2">
            {formats.map((f, i) => {
              const examples = Array.isArray(f.examples)
                ? (f.examples as unknown[]).map((e) => String(e)).join(", ")
                : f.examples
                  ? String(f.examples)
                  : "";
              return (
                <div className="panel" key={i}>
                  {f.label ? <strong style={{ color: "var(--navy)" }}>{f.label}</strong> : null}
                  {f.description ? <p className="small">{f.description}</p> : null}
                  {examples ? (
                    <p className="tiny muted">Examples: {examples}</p>
                  ) : null}
                </div>
              );
            })}
          </div>
        </Section>
      ) : null}
    </main>
  );
}
