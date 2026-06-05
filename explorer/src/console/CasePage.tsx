import { useEffect, useRef, useState } from "react";
import { Link, useNavigate, useParams } from "react-router-dom";
import { AppShell } from "./AppShell";
import { cx } from "../lib/cx";
import {
  STAGES,
  type StageId,
  type CaseDetail,
  type RunEvent,
  archiveUrl,
  getCase,
  startRun,
  streamRun,
} from "../lib/consoleApi";

/* The case shell — open a discovery case and walk its six stages. The progress bar at the top is
 * the navigator (click any marker to jump to that stage, exactly like Akhilesh's reference). A saved
 * case is fully complete on open (every stage navigable, content from the curated archive/ suite).
 * "Run live" executes the real pipeline for the real time it takes and streams the genuine activity
 * into Domain Analysis; the deliverable shown is still the signed-off archive suite. */

type StageState = "idle" | "active" | "done";

export default function CasePage() {
  const { caseId = "", stageId } = useParams();
  const nav = useNavigate();

  const [detail, setDetail] = useState<CaseDetail | null>(null);
  const [notFound, setNotFound] = useState(false);

  // live-run state (only used when the user triggers a fresh run)
  const [running, setRunning] = useState(false);
  const [activity, setActivity] = useState<string[]>([]);
  const [liveStage, setLiveStage] = useState<Record<string, StageState>>({});
  const [elapsed, setElapsed] = useState(0);
  const [comments, setComments] = useState<string[]>([]);
  const closeRef = useRef<(() => void) | null>(null);
  const feedRef = useRef<HTMLDivElement | null>(null);

  // the active stage comes from the URL; default to the first stage
  const active: StageId = (STAGES.find((s) => s.id === stageId)?.id ?? STAGES[0].id) as StageId;

  useEffect(() => {
    getCase(caseId).then((d) => (d ? setDetail(d) : setNotFound(true)));
    return () => closeRef.current?.();
  }, [caseId]);

  useEffect(() => {
    if (feedRef.current) feedRef.current.scrollTop = feedRef.current.scrollHeight;
  }, [activity]);

  useEffect(() => {
    if (!running) return;
    const t0 = Date.now();
    setElapsed(0);
    const id = window.setInterval(() => setElapsed(Math.round((Date.now() - t0) / 1000)), 1000);
    return () => window.clearInterval(id);
  }, [running]);

  if (notFound) {
    return (
      <AppShell title="Case not found" crumb="Discovery cases">
        <div className="board-empty">
          That case doesn’t exist. <Link to="/">← Back to dashboard</Link>
        </div>
      </AppShell>
    );
  }
  if (!detail) return <AppShell title="Loading…" crumb="Discovery cases"><div className="board-empty">Loading case…</div></AppShell>;

  // a saved case is complete; during a live run the stage state is driven by the SSE stream
  const stageStatus = (id: StageId): StageState => {
    if (running || Object.keys(liveStage).length) return liveStage[id] ?? "idle";
    return "done";
  };

  function goStage(id: StageId) {
    nav(`/case/${caseId}/${id}`);
  }

  async function onRunLive() {
    if (running) return;
    setActivity([]);
    setLiveStage({ upload: "active" });
    setRunning(true);
    goStage("assessment"); // surface the live log
    try {
      const id = await startRun(detail!.domain);
      closeRef.current = streamRun(id, onEvent);
    } catch (err) {
      setActivity((a) => [...a, err instanceof Error ? err.message : "Could not start the run."]);
      setRunning(false);
    }
  }

  function onEvent(e: RunEvent) {
    if (e.type === "stage" && e.stage) {
      setLiveStage((prev) => {
        const next = { ...prev };
        let passed = true;
        for (const s of STAGES) {
          if (s.id === e.stage) {
            next[s.id] = e.state === "done" ? "done" : "active";
            passed = false;
          } else if (passed) next[s.id] = "done";
        }
        return next;
      });
    } else if ((e.type === "activity" || e.type === "warn") && e.text) {
      setActivity((a) => [...a.slice(-200), e.text!]);
    } else if (e.type === "done") {
      setRunning(false);
      setLiveStage(() => {
        const next: Record<string, StageState> = {};
        for (const s of STAGES) next[s.id] = "done";
        return next;
      });
    }
  }

  return (
    <AppShell
      title={detail.title}
      crumb="Discovery cases"
      actions={
        running ? (
          <span className="rx-running">● Live re-run — {fmt(elapsed)}</span>
        ) : (
          <button className="rx-link" onClick={onRunLive}>↻ Re-run live</button>
        )
      }
    >
      <section className="case-meta panel">
        <div className="cm-main">
          <div className="eyebrow">{detail.domain.toUpperCase()} · Discovery case</div>
          <h2 className="cm-h">{detail.title}</h2>
          <div className="cm-sub">{detail.client}</div>
        </div>
        <dl className="cm-facts">
          <div><dt>Run date</dt><dd>{detail.run_date}</dd></div>
          <div><dt>Duration</dt><dd>{running ? fmt(elapsed) : `${detail.duration_minutes} min`}</dd></div>
          <div><dt>Documents</dt><dd>{detail.doc_count}</dd></div>
          <div><dt>Status</dt><dd className="ok">{running ? "Running…" : detail.status}</dd></div>
        </dl>
      </section>

      {/* ── the stage navigator (clickable progress bar) ── */}
      <nav className="case-stepper" aria-label="discovery stages">
        {STAGES.map((s, i) => {
          const st = stageStatus(s.id);
          return (
            <button
              key={s.id}
              className={cx("cs-step", st, s.id === active && "current")}
              onClick={() => goStage(s.id)}
            >
              <span className="cs-num">{st === "done" ? "✓" : i + 1}</span>
              <span className="cs-label">{s.label}</span>
            </button>
          );
        })}
      </nav>

      {/* ── the active stage panel ── */}
      <section className="case-stage">
        {active === "upload" && <IngestionStage detail={detail} />}
        {active === "assessment" && (
          <DomainAnalysisStage activity={activity} running={running} feedRef={feedRef} />
        )}
        {active === "discovery_copilot" && (
          <CopilotStage detail={detail} />
        )}
        {active === "analysis" && <TransformationStage />}
        {active === "preview" && (
          <FindingsReviewStage
            detail={detail}
            comments={comments}
            onComment={(note) => setComments((c) => [...c, note])}
          />
        )}
        {active === "report_generation" && <ReportStage detail={detail} />}
      </section>
    </AppShell>
  );
}

/* ── stage panels ─────────────────────────────────────────────────────────── */

function StageHead({ n, title, blurb }: { n: number; title: string; blurb: string }) {
  return (
    <header className="stage-head">
      <div className="sh-num">{n}</div>
      <div>
        <h2>{title}</h2>
        <p>{blurb}</p>
      </div>
    </header>
  );
}

function IngestionStage({ detail }: { detail: CaseDetail }) {
  return (
    <div className="panel stage-panel">
      <StageHead n={1} title="Ingestion"
        blurb={`${detail.doc_count} source documents ingested — SOPs, RACI, policies, system exports and working notes.`} />
      <div className="ingest-grid">
        {detail.input_docs.map((d) => (
          <a key={d.name} className="doc-chip" href={archiveUrl(`input/${d.name}`)}
             target="_blank" rel="noreferrer">
            <span className={cx("doc-kind", d.kind)}>{d.kind}</span>
            <span className="doc-name">{d.name}</span>
            <span className="doc-size">{d.kb} KB</span>
          </a>
        ))}
      </div>
      <div className="stage-foot ok">✓ All {detail.doc_count} documents ingested.</div>
    </div>
  );
}

function DomainAnalysisStage({
  activity, running, feedRef,
}: { activity: string[]; running: boolean; feedRef: React.RefObject<HTMLDivElement | null> }) {
  const lines = activity.length ? activity : DEMO_LOG;
  return (
    <div className="panel stage-panel">
      <StageHead n={2} title="Domain Analysis"
        blurb="The agent reads each source, cross-checks documented process against the actual data, and computes every figure with deterministic tools — the live activity log." />
      <div className="feed" ref={feedRef}>
        {lines.map((l, i) => (
          <div className="feed-line" key={i}>· {l}</div>
        ))}
        {running && <div className="feed-line is-live">▌</div>}
      </div>
      {!activity.length && (
        <div className="stage-foot">Representative activity from the completed run. Trigger “Run live” to stream a fresh one.</div>
      )}
    </div>
  );
}

function CopilotStage({ detail }: { detail: CaseDetail }) {
  const g = detail.gaps;
  return (
    <div className="panel stage-panel">
      <StageHead n={3} title="Discovery Co-pilot"
        blurb="The single human-in-the-loop surface. The platform raised every open question at the gap gate; the AuroPro SME recorded a decision on each. This working record is frozen — a read-only audit of the judgement behind the clean reports." />
      <div className="copilot-stats">
        <Stat n={g.questions} l="open questions" />
        <Stat n={g.high_resolved} l="high-severity gaps resolved" tone="ok" />
        <Stat n={g.clarifications} l="clarifications reviewed" tone="warn" />
        <Stat n={g.carried_forward} l="carried forward (amber)" tone="amber" />
      </div>
      <iframe className="stage-frame tall" title="Discovery Co-pilot — gap resolution audit trail"
        src={archiveUrl(detail.copilot_audit_url.replace(/^\/archive\//, ""))} />
    </div>
  );
}

const TJ_STEPS = ["Assessment", "Opportunity identification", "Use-case modeling", "Roadmap"];

function TransformationStage() {
  return (
    <div className="panel stage-panel">
      <StageHead n={4} title="Transformation Journey"
        blurb="From the verified knowledge graph, the platform assembles the transformation: the current-state assessment, the opportunities, each modelled as a use case, and a sequenced roadmap." />
      <div className="tj-bar">
        {TJ_STEPS.map((s, i) => (
          <div className="tj-step done" key={s}>
            <span className="tj-dot">✓</span>
            <span className="tj-name">{s}</span>
            {i < TJ_STEPS.length - 1 && <span className="tj-link" />}
          </div>
        ))}
      </div>
      <div className="stage-foot ok">✓ Transformation journey assembled — feeds the six-report suite.</div>
    </div>
  );
}

function FindingsReviewStage({
  detail, comments, onComment,
}: { detail: CaseDetail; comments: string[]; onComment: (n: string) => void }) {
  const [note, setNote] = useState("");
  const [approved, setApproved] = useState(false);
  return (
    <div className="panel stage-panel">
      <StageHead n={5} title="Findings Review"
        blurb="The generated preview suite, ready for the BU lead to review before sign-off. Approve to lock it, or send it back with comments for a re-run." />
      <iframe className="stage-frame tall" title="Findings review — preview suite"
        src={archiveUrl(detail.preview_url.replace(/^\/archive\//, ""))} />
      <div className="review-actions">
        {approved ? (
          <div className="review-approved ok">✓ Approved — signed off for report generation.</div>
        ) : (
          <>
            <button className="approve" onClick={() => setApproved(true)}>Approve &amp; sign off</button>
            <div className="rerun-box">
              <textarea placeholder="Re-run with comments — note what to revisit…"
                value={note} onChange={(e) => setNote(e.target.value)} />
              <button disabled={!note.trim()}
                onClick={() => { onComment(note.trim()); setNote(""); }}>
                Send back for re-run
              </button>
            </div>
          </>
        )}
        {comments.length > 0 && (
          <ul className="comment-log">
            {comments.map((c, i) => <li key={i}>{c}</li>)}
          </ul>
        )}
      </div>
    </div>
  );
}

function ReportStage({ detail }: { detail: CaseDetail }) {
  const urlOf = (r: CaseDetail["reports"][number]) => archiveUrl(r.url.replace(/^\/archive\//, ""));
  return (
    <div className="panel stage-panel">
      <StageHead n={6} title="Report Generation"
        blurb="The signed-off six-report client suite. Every finding is source-cited; each report is a standalone deliverable — view it or download it." />
      <div className="report-grid">
        {detail.reports.map((r) => (
          <div key={r.id} className="report-card">
            <span className="rc-id">{r.id}</span>
            <span className="rc-title">{r.title}</span>
            <span className="rc-actions">
              <a href={urlOf(r)} target="_blank" rel="noreferrer">Open ↗</a>
              {/* ?download=1 → backend sets Content-Disposition: attachment (the <a download>
                  attribute is ignored cross-origin, so we force it server-side) */}
              <a href={`${urlOf(r)}?download=1`}>Download</a>
            </span>
          </div>
        ))}
      </div>
    </div>
  );
}

/* ── small bits ─────────────────────────────────────────────────────────── */

function Stat({ n, l, tone }: { n: number; l: string; tone?: string }) {
  return (
    <div className={cx("cstat", tone)}>
      <span className="cstat-n">{n}</span>
      <span className="cstat-l">{l}</span>
    </div>
  );
}

function fmt(s: number): string {
  const m = Math.floor(s / 60);
  const r = s % 60;
  return m ? `${m}m ${r}s` : `${r}s`;
}

// Representative Domain-Analysis log for the saved case (the same shape a live run streams).
const DEMO_LOG = [
  "Reading order-flow-analysis-export-2025…",
  "Reading sap-crm-customer-export…",
  "Reading sap-s4-customer-master-export…",
  "Cross-checking sap-s4-customer-master-export against sap-crm-customer-export on customer_id…",
  "Breaking down order-flow-analysis-export-2025 by channel…",
  "Counting how often a condition occurs in customer-service-escalation-log-2025…",
  "Searching order-management-sop-opella-europe for: EDI, out of scope, not covered…",
  "Checking sap-crm-customer-export against the documented credit-limit rule…",
  "Totalling credit_limit_eur in sap-crm-customer-export…",
  "Totalling credit_limit_eur in sap-s4-customer-master-export…",
  "Pulling the findings together…",
];
