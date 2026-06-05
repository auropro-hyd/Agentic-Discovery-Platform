import { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";
import { Logo } from "../layout/Logo";
import { getCases, ping, type CaseCard } from "../lib/consoleApi";
import { cx } from "../lib/cx";

/* The Discovery dashboard — the landing page. A list of discovery cases (Claims-Workbench style);
 * for now a single saved case (Opella O2C), already executed and signed off. Clicking it opens the
 * 6-stage case shell. The mode selector (real/cached) is gone: a run is always live. */

const STATUS_TONE: Record<string, string> = {
  "Signed off": "ok",
  "In review": "warn",
  Running: "run",
};

export default function DashboardPage() {
  const nav = useNavigate();
  const [cases, setCases] = useState<CaseCard[] | null>(null);
  const [backendUp, setBackendUp] = useState<boolean | null>(null);

  useEffect(() => {
    ping().then(setBackendUp);
    getCases().then(setCases);
  }, []);

  return (
    <div className="dash">
      <header className="dash-top">
        <div className="brand-inline">
          <Logo size={28} />
          <div>
            <div className="ci-name">AUROPRO</div>
            <div className="ci-sub">Autonomous Discovery Platform</div>
          </div>
        </div>
        <div className="spacer" />
        <span className={cx("be-dot", backendUp === false && "is-down")} title="backend status" />
        <span className="be-label">
          {backendUp === null ? "checking…" : backendUp ? "engine online" : "engine offline"}
        </span>
      </header>

      <section className="dash-hero">
        <h1>Discovery cases</h1>
        <p className="lede">
          Each case is a full autonomous discovery run — documents in, a signed-off six-report suite
          out. Open one to walk the pipeline stage by stage, or start a new live run.
        </p>
      </section>

      <section className="dash-list panel">
        <div className="dl-head">
          <span>Case</span>
          <span>Domain</span>
          <span>Run date</span>
          <span>Duration</span>
          <span>Stage</span>
          <span>Status</span>
        </div>

        {cases === null ? (
          <div className="dl-empty">Loading cases…</div>
        ) : cases.length === 0 ? (
          <div className="dl-empty">
            No cases yet. {backendUp === false && "Start the backend (make console) to load them."}
          </div>
        ) : (
          cases.map((c) => (
            <button key={c.id} className="dl-row" onClick={() => nav(`/case/${c.id}`)}>
              <span className="dl-case">
                <span className="dl-title">{c.title}</span>
                <span className="dl-client">{c.client}</span>
              </span>
              <span className="dl-domain">{c.domain.toUpperCase()}</span>
              <span>{c.run_date}</span>
              <span>{c.duration_minutes} min</span>
              <span className="dl-stage">{stageLabel(c.stage)}</span>
              <span className={cx("dl-status", STATUS_TONE[c.status] ?? "neutral")}>
                {c.status}
              </span>
            </button>
          ))
        )}
      </section>

      <div className="dash-foot">
        <span className="df-note">
          A new run executes the real pipeline and takes the time it needs; the case it produces is
          the signed-off deliverable suite.
        </span>
      </div>
    </div>
  );
}

// the human stage name for a completed-case's current stage chip (kept local; mirrors STAGES)
function stageLabel(stage: string): string {
  const map: Record<string, string> = {
    upload: "Ingestion",
    assessment: "Domain Analysis",
    discovery_copilot: "Discovery Co-pilot",
    analysis: "Transformation Journey",
    preview: "Findings Review",
    report_generation: "Report Generation",
  };
  return map[stage] ?? stage;
}
