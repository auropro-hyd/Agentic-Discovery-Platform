import { useEffect, useRef, useState } from "react";
import { Link, useNavigate, useParams, useSearchParams } from "react-router-dom";
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
  const [params, setParams] = useSearchParams();

  const [detail, setDetail] = useState<CaseDetail | null>(null);
  const [notFound, setNotFound] = useState(false);
  const autoRan = useRef(false);

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
  const isLive = params.get("live") === "1"; // a freshly-ingested case (no saved/curated record)

  useEffect(() => {
    getCase(caseId).then((d) => {
      if (d) setDetail(d);
      else if (isLive) setDetail(liveCaseDetail(caseId)); // fresh ingested run — synthesise the shell
      else setNotFound(true);
    });
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

  // ?run=1 / ?live=1 (set by the dashboard actions) auto-start a live run once the case is loaded.
  // ?rid=<id> means a run was ALREADY started (by /api/ingest) — subscribe to it instead of starting
  // a second. The transient flags are stripped after firing so a refresh doesn't re-trigger.
  useEffect(() => {
    if (!detail || autoRan.current) return;
    const existingRunId = params.get("rid") || undefined;
    const wantsRun = params.get("run") === "1";
    const wantsLive = params.get("live") === "1";
    if (!wantsRun && !wantsLive && !existingRunId) return;
    autoRan.current = true;
    if (params.get("run") || params.get("rid")) {
      const next = new URLSearchParams(params);
      next.delete("run");
      next.delete("rid");        // keep ?live=1 (marks the case as a fresh ingested run)
      setParams(next, { replace: true });
    }
    onRunLive(existingRunId);
  }, [detail, params]);

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

  const live = detail.kind === "live"; // a freshly-ingested case (no curated, signed-off record)

  // a saved case is complete on open; during a live run the stage state is driven by the SSE stream.
  // a live case starts all-idle (it has no completed history) and only fills in as the run streams.
  const stageStatus = (id: StageId): StageState => {
    if (running || Object.keys(liveStage).length) return liveStage[id] ?? "idle";
    return live ? "idle" : "done";
  };

  function goStage(id: StageId) {
    nav(`/case/${caseId}/${id}`);
  }

  async function onRunLive(existingRunId?: string) {
    if (running) return;
    setActivity([]);
    setLiveStage({ upload: "active" });
    setRunning(true);
    goStage("assessment"); // surface the live log
    try {
      // a fresh ingested case already has its run going (from /api/ingest) — subscribe, don't restart
      const id = existingRunId ?? (await startRun(detail!.domain));
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
          <span className="rx-running">● {live ? "Live run" : "Live re-run"} — {fmt(elapsed)}</span>
        ) : (
          <button className="rx-link" onClick={() => onRunLive()}>↻ {live ? "Run again" : "Re-run live"}</button>
        )
      }
    >
      <section className="case-meta panel">
        <div className="cm-main">
          <div className="eyebrow">
            {detail.domain.toUpperCase()} · {live ? "Live discovery" : "Discovery case"}
          </div>
          <h2 className="cm-h">{detail.title}</h2>
          <div className="cm-sub">{detail.client}</div>
        </div>
        <dl className="cm-facts">
          <div><dt>Run date</dt><dd>{live ? (running ? "now" : "—") : detail.run_date}</dd></div>
          <div><dt>Duration</dt><dd>{running ? fmt(elapsed) : live ? "—" : `${detail.duration_minutes} min`}</dd></div>
          <div><dt>Documents</dt><dd>{detail.doc_count}</dd></div>
          <div><dt>Status</dt><dd className="ok">{running ? "Running…" : live ? "Live run" : detail.status}</dd></div>
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
          <DomainAnalysisStage activity={activity} running={running} live={live} feedRef={feedRef} />
        )}
        {active === "discovery_copilot" && (
          <CopilotStage detail={detail} live={live} />
        )}
        {active === "analysis" && <TransformationStage live={live} running={running} />}
        {active === "preview" && (
          <FindingsReviewStage
            detail={detail}
            live={live}
            comments={comments}
            onComment={(note) => setComments((c) => [...c, note])}
          />
        )}
        {active === "report_generation" && <ReportStage detail={detail} live={live} running={running} />}
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
  // a freshly-ingested live case has no curated doc catalogue to chip out (the files were just
  // uploaded); the saved case lists its 12 source documents.
  if (!detail.input_docs.length) {
    return (
      <div className="panel stage-panel">
        <StageHead n={1} title="Ingestion"
          blurb="Your uploaded documents were staged and handed to the pipeline. This is a fresh, live discovery — the activity streams under Domain Analysis." />
        <div className="stage-foot ok">✓ Documents staged for ingestion.</div>
      </div>
    );
  }
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
  activity, running, live, feedRef,
}: { activity: string[]; running: boolean; live: boolean; feedRef: React.RefObject<HTMLDivElement | null> }) {
  // saved case with no live stream → show representative activity; a fresh live case shows only its
  // genuine stream (never the Opella-specific demo log).
  const lines = activity.length ? activity : live ? ["Waiting for the live pipeline to start…"] : DEMO_LOG;
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
      {!activity.length && !live && (
        <div className="stage-foot">Representative activity from the completed run. Trigger “Run live” to stream a fresh one.</div>
      )}
    </div>
  );
}

const SEV_LABEL: Record<string, string> = {
  high: "High · blocking", clarification: "Clarification", amber: "Low · carried forward",
};

/* For a fresh live case, archive-backed stages have nothing curated to show yet — say so plainly
 * rather than render an empty or borrowed surface. */
function LivePending({ n, title, blurb, note }: { n: number; title: string; blurb: string; note: string }) {
  return (
    <div className="panel stage-panel">
      <StageHead n={n} title={title} blurb={blurb} />
      <div className="live-pending">
        <span className="lp-dot" />
        <p>{note}</p>
      </div>
    </div>
  );
}

function CopilotStage({ detail, live }: { detail: CaseDetail; live: boolean }) {
  if (live) {
    return <LivePending n={3} title="Discovery Co-pilot"
      blurb="The single human-in-the-loop surface. Open questions surface here for SME decisions once the live run reaches the gap gate."
      note="This is a fresh discovery — the gap gate runs live as the pipeline analyses your documents. Decisions will appear here as questions are raised." />;
  }
  const g = detail.gaps;
  const ledger = detail.gap_ledger ?? [];
  return (
    <div className="panel stage-panel">
      <StageHead n={3} title="Discovery Co-pilot"
        blurb="The single human-in-the-loop surface. The platform routed every open question to the AuroPro SME, who recorded a decision on each — the chain of judgement that cleared the gap gate before any report was generated." />
      <div className="copilot-stats">
        <Stat n={g.questions} l="open questions" />
        <Stat n={g.high_resolved} l="high-severity gaps resolved" tone="ok" />
        <Stat n={g.clarifications} l="clarifications reviewed" tone="warn" />
        <Stat n={g.carried_forward} l="carried forward (amber)" tone="amber" />
      </div>

      <div className="gate-banner">
        <span className="gate-dot" /> Gap gate <strong>CLEARED</strong> — all blocking gaps resolved;
        Block 3 &amp; report generation authorised.
      </div>

      {/* native SME decision ledger — this is the governance surface, not a report */}
      <ul className="decisions">
        {ledger.map((d) => (
          <li key={d.id} className={cx("decision", d.severity)}>
            <div className="dz-l">
              <span className="dz-id">{d.id}</span>
              <span className={cx("dz-sev", d.severity)}>{SEV_LABEL[d.severity] ?? d.severity}</span>
            </div>
            <div className="dz-body">
              <div className="dz-q">{d.question}</div>
              <div className="dz-decision">
                <span className="dz-tag">SME decision</span> {d.decision}
              </div>
              <div className="dz-resolves">→ feeds {d.resolves}</div>
            </div>
            <span className={cx("dz-status", d.severity)}>{d.status}</span>
          </li>
        ))}
      </ul>

      <details className="record-toggle">
        <summary>View the full gap-resolution working record (SME audit trail) ↗</summary>
        <iframe className="stage-frame tall" title="Discovery Co-pilot — gap resolution audit trail"
          src={archiveUrl(detail.copilot_audit_url.replace(/^\/archive\//, ""))} />
      </details>
    </div>
  );
}

const TJ_STEPS = ["Assessment", "Opportunity identification", "Use-case modeling", "Roadmap"];

function TransformationStage({ live, running }: { live: boolean; running: boolean }) {
  if (live) {
    return <LivePending n={4} title="Transformation Journey"
      blurb="From the verified knowledge graph, the platform assembles the transformation: current-state, opportunities, use cases and a sequenced roadmap."
      note={running
        ? "Assembling live from your documents — the journey appears once the analysis and gap gate complete."
        : "This stage assembles once the live run reaches it."} />;
  }
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
  detail, live, comments, onComment,
}: { detail: CaseDetail; live: boolean; comments: string[]; onComment: (n: string) => void }) {
  const [note, setNote] = useState("");
  const [approved, setApproved] = useState(false);
  if (live) {
    return <LivePending n={5} title="Findings Review"
      blurb="The sign-off gate. The reviewer approves the assembled suite for final generation, or sends it back with comments."
      note="This is a fresh discovery — the findings suite becomes available for sign-off once the live run completes its analysis." />;
  }
  return (
    <div className="panel stage-panel">
      <StageHead n={5} title="Findings Review"
        blurb="The sign-off gate. The BU lead reviews the assembled suite and either approves it for final generation or sends it back with comments. This is the decision point — the reports below are the evidence under review." />

      {/* the approval gate — the distinctive content of THIS stage */}
      <div className="review-gate">
        <div className="rg-summary">
          <div className="rg-line">Under review for sign-off:</div>
          <ul className="rg-items">
            <li><strong>{detail.reports.length}</strong> report suite</li>
            <li><strong>{detail.findings}</strong> validated findings</li>
            <li><strong>{detail.opportunities}</strong> opportunities mapped</li>
            <li><strong>{detail.gaps.high_resolved}</strong> blocking gaps resolved</li>
          </ul>
        </div>
        <div className="rg-action">
          {approved ? (
            <div className="review-approved ok">✓ Approved &amp; signed off — released to report generation.</div>
          ) : (
            <>
              <button className="approve" onClick={() => setApproved(true)}>Approve &amp; sign off</button>
              <div className="rerun-box">
                <textarea placeholder="…or send back with comments for a re-run"
                  value={note} onChange={(e) => setNote(e.target.value)} />
                <button disabled={!note.trim()}
                  onClick={() => { onComment(note.trim()); setNote(""); }}>
                  Send back
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

      <details className="record-toggle" open>
        <summary>Review the full preview suite ↗</summary>
        <iframe className="stage-frame tall" title="Findings review — preview suite"
          src={archiveUrl(detail.preview_url.replace(/^\/archive\//, ""))} />
      </details>
    </div>
  );
}

function ReportStage({ detail, live, running }: { detail: CaseDetail; live: boolean; running: boolean }) {
  if (live && !detail.reports.length) {
    return <LivePending n={6} title="Report Generation"
      blurb="The signed-off client report suite — each report a standalone, source-cited deliverable."
      note={running
        ? "Generating live — the report suite is written once the pipeline finishes. This run produces fresh reports under out/ for this case."
        : "The report suite is produced when the live run completes. Run this case to generate it."} />;
  }
  const urlOf = (r: CaseDetail["reports"][number]) => archiveUrl(r.url.replace(/^\/archive\//, ""));
  return (
    <div className="panel stage-panel">
      <StageHead n={6} title="Report Generation"
        blurb="The signed-off six-report client suite. Every finding is source-cited; each report is a standalone deliverable — view it or download it." />
      <div className="report-grid">
        {detail.reports.map((r) => (
          <div key={r.id} className="report-card">
            <div className="rc-head">
              <span className="rc-id">{r.id}</span>
              <span className="rc-title">{r.title}</span>
            </div>
            <div className="rc-actions">
              <a className="rc-open" href={urlOf(r)} target="_blank" rel="noreferrer">Open ↗</a>
              {/* ?download=1 → backend sets Content-Disposition: attachment (the <a download>
                  attribute is ignored cross-origin, so we force it server-side) */}
              <a className="rc-dl" href={`${urlOf(r)}?download=1`}>Download</a>
            </div>
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

/* Synthesise the case shell for a freshly-ingested domain (no saved/curated record on the backend).
 * Title-cases the slug; the shell renders the live run honestly — no archive deliverable. */
function liveCaseDetail(domain: string): CaseDetail {
  const title = domain
    .split("-")
    .map((w) => (w ? w.charAt(0).toUpperCase() + w.slice(1) : w))
    .join(" ");
  return {
    id: domain,
    title,
    domain,
    client: "Uploaded documents",
    run_date: "—",
    duration_minutes: 0,
    stage: "upload",
    status: "Live run",
    doc_count: 0,
    gaps: { questions: 0, high_resolved: 0, clarifications: 0, carried_forward: 0 },
    findings: 0,
    opportunities: 0,
    kind: "live",
    input_docs: [],
    gap_ledger: [],
    reports: [],
    copilot_audit_url: "",
    preview_url: "",
  };
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
