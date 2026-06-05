import { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";
import { AppShell } from "./AppShell";
import { getCases, ping, type CaseCard } from "../lib/consoleApi";
import { cx } from "../lib/cx";

/* The discovery dashboard — the landing page, inside the enterprise shell. Sectioned like a real
 * platform: a KPI strip up top, then the cases section (cards). For now one saved, signed-off case
 * (Opella O2C). No mode selector — a run is always live; the saved case is the signed-off result. */

const STATUS_TONE: Record<string, string> = {
  "Signed off": "ok",
  "In review": "warn",
  Running: "run",
};

const STAGE_LABEL: Record<string, string> = {
  upload: "Ingestion",
  assessment: "Domain Analysis",
  discovery_copilot: "Discovery Co-pilot",
  analysis: "Transformation Journey",
  preview: "Findings Review",
  report_generation: "Report Generation",
};

export default function DashboardPage() {
  const nav = useNavigate();
  const [cases, setCases] = useState<CaseCard[] | null>(null);
  const [backendUp, setBackendUp] = useState<boolean | null>(null);

  useEffect(() => {
    ping().then(setBackendUp);
    getCases().then(setCases);
  }, []);

  const list = cases ?? [];
  const completed = list.filter((c) => c.status === "Signed off").length;
  const totalDocs = list.reduce((n, c) => n + c.doc_count, 0);
  const avgMin = list.length
    ? Math.round(list.reduce((n, c) => n + c.duration_minutes, 0) / list.length)
    : 0;

  return (
    <AppShell
      title="Dashboard"
      crumb="Discovery Platform"
      actions={
        <span className={cx("be-chip", backendUp === false && "is-down")}>
          <span className="be-dot" />
          {backendUp === null ? "checking…" : backendUp ? "Engine online" : "Engine offline"}
        </span>
      }
    >
      {/* ── KPI strip ── */}
      <section className="kpi-strip">
        <Kpi label="Discovery cases" value={String(list.length)} hint="active workflows" />
        <Kpi label="Completed" value={String(completed)} hint="signed off" tone="ok" />
        <Kpi label="Avg. discovery time" value={avgMin ? `${avgMin} min` : "—"} hint="ingest → sign-off" />
        <Kpi label="Documents processed" value={String(totalDocs)} hint="across all cases" />
      </section>

      {/* ── cases section ── */}
      <section className="board">
        <div className="board-head">
          <h2>Discovery cases</h2>
          <p>Each case is a full autonomous discovery — documents in, a signed-off six-report suite out.</p>
        </div>

        {cases === null ? (
          <div className="board-empty">Loading cases…</div>
        ) : list.length === 0 ? (
          <div className="board-empty">
            No cases yet.{backendUp === false && " Start the backend (make console) to load them."}
          </div>
        ) : (
          <div className="case-cards">
            {list.map((c) => (
              <button key={c.id} className="case-card" onClick={() => nav(`/case/${c.id}`)}>
                <div className="cc-top">
                  <span className="cc-domain">{c.domain.toUpperCase()}</span>
                  <span className={cx("cc-status", STATUS_TONE[c.status] ?? "neutral")}>{c.status}</span>
                </div>
                <div className="cc-title">{c.title}</div>
                <div className="cc-client">{c.client}</div>
                <dl className="cc-facts">
                  <div><dt>Run</dt><dd>{c.run_date}</dd></div>
                  <div><dt>Duration</dt><dd>{c.duration_minutes} min</dd></div>
                  <div><dt>Documents</dt><dd>{c.doc_count}</dd></div>
                  <div><dt>Findings</dt><dd>{c.findings}</dd></div>
                </dl>
                <div className="cc-foot">
                  <span className="cc-stage">{STAGE_LABEL[c.stage] ?? c.stage}</span>
                  <span className="cc-open">Open case →</span>
                </div>
              </button>
            ))}
          </div>
        )}
      </section>
    </AppShell>
  );
}

function Kpi({ label, value, hint, tone }: { label: string; value: string; hint: string; tone?: string }) {
  return (
    <div className={cx("kpi", tone)}>
      <div className="kpi-label">{label}</div>
      <div className="kpi-value">{value}</div>
      <div className="kpi-hint">{hint}</div>
    </div>
  );
}
