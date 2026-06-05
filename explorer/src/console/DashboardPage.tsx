import { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";
import { AppShell } from "./AppShell";
import {
  getCases,
  getActiveRuns,
  ping,
  type CaseCard,
  type ActiveRun,
} from "../lib/consoleApi";
import { cx } from "../lib/cx";
import { NewCaseSection } from "./NewCaseSection";

/* The pre-ingested demo case a "Run live" maps to (matches v1/inputs/o2c). */
const RUN_CASE_ID = "opella-o2c";

/* The discovery dashboard — the landing page, inside the enterprise shell. Sectioned like a real
 * platform: an Initiate-new-case section (upload your own docs, or run the pre-ingested O2C case),
 * a live in-progress strip, a KPI strip, then the saved cases. No mode selector — a run is always
 * live; the saved Opella case is the signed-off, curated result. */

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
  const [activeRuns, setActiveRuns] = useState<ActiveRun[]>([]);

  useEffect(() => {
    ping().then(setBackendUp);
    getCases().then(setCases);
  }, []);

  // Poll for in-progress runs so the dashboard reflects a discovery the user kicked off (here or
  // in a case tab). Light 4s cadence; only meaningful while the backend is up.
  useEffect(() => {
    let live = true;
    const tick = () => getActiveRuns().then((r) => live && setActiveRuns(r));
    tick();
    const id = window.setInterval(tick, 4000);
    return () => {
      live = false;
      window.clearInterval(id);
    };
  }, []);

  // Open a case and kick off a live run there (?run=1). Used by the per-card "Rerun" and the
  // pre-ingested O2C tile — the live pipeline + SSE log all live in CasePage.
  const openAndRun = (id: string) => nav(`/case/${id}?run=1`);

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
      {/* ── in-progress run strip (only while something is running) ── */}
      {activeRuns.length > 0 && (
        <section className="run-strip" aria-live="polite">
          {activeRuns.map((r) => (
            <button key={r.run_id} className="rs-item" onClick={() => nav(resumeHref(r))}>
              <span className="rs-pulse" />
              <span className="rs-text">
                <strong>Live discovery in progress</strong> — {r.label}
                <span className="rs-stage"> · {STAGE_LABEL[r.stage] ?? r.stage}</span>
              </span>
              <span className="rs-resume">Resume →</span>
            </button>
          ))}
        </section>
      )}

      {/* ── initiate a new case ── */}
      <NewCaseSection
        backendUp={backendUp}
        onRunPreingested={() => openAndRun(RUN_CASE_ID)}
        onIngested={(domain, runId) => nav(`/case/${domain}?live=1&rid=${runId}`)}
      />

      {/* ── KPI strip ── */}
      <section className="kpi-strip">
        <Kpi label="Discovery cases" value={String(list.length)} hint="saved workflows" />
        <Kpi label="Completed" value={String(completed)} hint="signed off" tone="ok" />
        <Kpi label="Avg. discovery time" value={avgMin ? `${avgMin} min` : "—"} hint="ingest → sign-off" />
        <Kpi label="Documents processed" value={String(totalDocs)} hint="across all cases" />
      </section>

      {/* ── saved cases ── */}
      <section className="board">
        <div className="board-head">
          <div>
            <h2>Discovery cases</h2>
            <p>Each case is a full autonomous discovery — documents in, a signed-off six-report suite out.</p>
          </div>
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
              <div
                key={c.id}
                className="case-card"
                role="button"
                tabIndex={0}
                onClick={() => nav(`/case/${c.id}`)}
                onKeyDown={(e) => {
                  if (e.key === "Enter" || e.key === " ") {
                    e.preventDefault();
                    nav(`/case/${c.id}`);
                  }
                }}
              >
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
                  <div className="cc-actions">
                    <button
                      className="cc-rerun"
                      onClick={(e) => { e.stopPropagation(); openAndRun(c.id); }}
                      disabled={backendUp === false}
                      title={backendUp === false ? "Start the engine to re-run" : "Run this discovery live again"}
                    >
                      ↻ Rerun
                    </button>
                    <button
                      className="cc-open"
                      onClick={(e) => { e.stopPropagation(); nav(`/case/${c.id}`); }}
                    >
                      Open case →
                    </button>
                  </div>
                </div>
              </div>
            ))}
          </div>
        )}
      </section>
    </AppShell>
  );
}

/* Resume an in-progress run: route into its case and subscribe to that exact run (?rid). The
 * pre-ingested O2C run resumes into the saved case (archive shell, complete); a freshly-ingested
 * domain resumes as a live case (?live=1 → the live shell, no archive deliverable). */
function resumeHref(r: ActiveRun): string {
  return r.domain === "o2c"
    ? `/case/${RUN_CASE_ID}?rid=${r.run_id}`               // subscribe to the live run, keep archive shell
    : `/case/${r.domain}?live=1&rid=${r.run_id}`;          // live case shell + subscribe
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
