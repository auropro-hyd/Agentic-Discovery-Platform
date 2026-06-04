import { useEffect, useRef, useState } from "react";
import { Link } from "react-router-dom";
import { Logo } from "../layout/Logo";
import { DOMAIN_SLUGS } from "../lib/domains";
import {
  STAGES,
  type StageId,
  type RunEvent,
  type FindingItem,
  ping,
  startRun,
  streamRun,
  getFindings,
  sendFeedback,
} from "../lib/consoleApi";
import { cx } from "../lib/cx";

/* The Discovery Console — the operator-facing flow that wraps the live pipeline, in Akhilesh's
 * 6 stages: upload -> assessment -> discovery copilot -> analysis -> preview -> report generation.
 * It drives the real run.py via the backend (server.py), streams phase progress, surfaces the
 * copilot gaps + SME feedback, and embeds the report explorer at the Preview stage. A "skip to
 * compiled reports" breakpoint jumps straight to the suite for the demo. */

type StageState = "idle" | "active" | "done";

const HOME = DOMAIN_SLUGS[0] ?? "o2c";

export default function ConsolePage() {
  const [domain, setDomain] = useState<string>(HOME);
  const [mode, setMode] = useState<"live" | "golden">("golden");
  const [running, setRunning] = useState(false);
  const [runId, setRunId] = useState<string | null>(null);
  const [stageState, setStageState] = useState<Record<string, StageState>>({});
  const [activity, setActivity] = useState<string[]>([]);
  const [warnings, setWarnings] = useState<string[]>([]);
  const [findings, setFindings] = useState<FindingItem[]>([]);
  const [feedback, setFeedback] = useState("");
  const [sentNotes, setSentNotes] = useState<string[]>([]);
  const [done, setDone] = useState(false);
  const [backendUp, setBackendUp] = useState<boolean | null>(null);
  const closeRef = useRef<(() => void) | null>(null);
  const feedRef = useRef<HTMLDivElement | null>(null);

  useEffect(() => {
    ping().then(setBackendUp);
    return () => closeRef.current?.();
  }, []);

  useEffect(() => {
    if (feedRef.current) feedRef.current.scrollTop = feedRef.current.scrollHeight;
  }, [activity]);

  const activeStage: StageId | null =
    (STAGES.map((s) => s.id).reverse().find((id) => stageState[id] === "active") as StageId) ?? null;

  function reset() {
    closeRef.current?.();
    setStageState({});
    setActivity([]);
    setWarnings([]);
    setFindings([]);
    setSentNotes([]);
    setDone(false);
    setRunId(null);
  }

  async function onStart() {
    reset();
    setRunning(true);
    try {
      const id = await startRun(domain, mode);
      setRunId(id);
      closeRef.current = streamRun(id, (e: RunEvent) => onEvent(id, e));
    } catch (err) {
      setWarnings((w) => [...w, err instanceof Error ? err.message : "Could not start the run."]);
      setRunning(false);
    }
  }

  function onEvent(id: string, e: RunEvent) {
    if (e.type === "stage" && e.stage) {
      setStageState((prev) => {
        const next = { ...prev };
        // mark every earlier stage done, the named one to its state
        let passed = true;
        for (const s of STAGES) {
          if (s.id === e.stage) {
            next[s.id] = e.state === "done" ? "done" : "active";
            passed = false;
          } else if (passed) {
            next[s.id] = "done";
          }
        }
        return next;
      });
      // when we reach the copilot stage, pull the gaps for the SME to review
      if (e.stage === "discovery_copilot") getFindings(domain).then(setFindings);
    } else if (e.type === "activity" && e.text) {
      setActivity((a) => [...a.slice(-80), e.text!]);
    } else if (e.type === "warn" && e.text) {
      setWarnings((w) => [...w, e.text!]);
    } else if (e.type === "error" && e.message) {
      setWarnings((w) => [...w, e.message!]);
    } else if (e.type === "done") {
      setRunning(false);
      setDone(!!e.ok);
      if (e.ok) {
        setStageState((prev) => {
          const next = { ...prev };
          for (const s of STAGES) next[s.id] = "done";
          return next;
        });
        // ensure copilot gaps are loaded even on a fast golden run
        getFindings(domain).then((f) => f.length && setFindings(f));
      }
      void id;
    }
  }

  async function submitFeedback() {
    const note = feedback.trim();
    if (!note || !runId) return;
    await sendFeedback(runId, note);
    setSentNotes((n) => [...n, note]);
    setFeedback("");
  }

  return (
    <div className="console">
      <header className="console-top">
        <div className="brand-inline">
          <Logo size={26} />
          <div>
            <div className="ci-name">AUROPRO</div>
            <div className="ci-sub">Discovery Console</div>
          </div>
        </div>
        <div className="spacer" />
        <Link to={`/suite/${domain}`} className="ghost-link">
          Skip to compiled reports →
        </Link>
      </header>

      {/* ── controls ── */}
      <section className="console-controls panel">
        <div className="cc-row">
          <label>
            Domain
            <select value={domain} onChange={(e) => setDomain(e.target.value)} disabled={running}>
              {DOMAIN_SLUGS.map((d) => (
                <option key={d} value={d}>
                  {d.toUpperCase()}
                </option>
              ))}
            </select>
          </label>
          <label>
            Mode
            <select
              value={mode}
              onChange={(e) => setMode(e.target.value as "live" | "golden")}
              disabled={running}
            >
              <option value="golden">Replay (fast, cached — demo)</option>
              <option value="live">Live run (real, costs credits)</option>
            </select>
          </label>
          <button className="run-btn" onClick={onStart} disabled={running || backendUp === false}>
            {running ? "Running…" : "Run discovery"}
          </button>
          {backendUp === false && (
            <span className="backend-off">
              Backend offline — start it: <code>cd v1 &amp;&amp; uv run python server.py</code>
            </span>
          )}
        </div>
        {mode === "live" && !running && (
          <p className="small muted" style={{ margin: "8px 0 0" }}>
            A live run drives the real pipeline end to end — it can take many minutes and consumes
            API credits. Use <strong>Replay</strong> for the demo.
          </p>
        )}
      </section>

      {/* ── the 6-stage progress rail ── */}
      <ol className="stepper">
        {STAGES.map((s, i) => {
          const st = (stageState[s.id] ?? "idle") as StageState;
          return (
            <li key={s.id} className={cx("step", st)}>
              <span className="step-dot">{st === "done" ? "✓" : i + 1}</span>
              <span className="step-label">{s.label}</span>
              {i < STAGES.length - 1 && <span className="step-bar" />}
            </li>
          );
        })}
      </ol>

      <div className="console-grid">
        {/* ── live activity feed ── */}
        <section className="panel feed-panel">
          <h3>Live activity {activeStage && <span className="muted small">· {labelFor(activeStage)}</span>}</h3>
          <div className="feed" ref={feedRef}>
            {activity.length === 0 ? (
              <p className="muted small">
                {running ? "Starting…" : "Run discovery to watch the pipeline work in real time."}
              </p>
            ) : (
              activity.map((line, i) => (
                <div className="feed-line" key={i}>
                  <span className="feed-tick" />
                  {line}
                </div>
              ))
            )}
          </div>
          {warnings.map((w, i) => (
            <div className="feed-warn" key={i}>
              ⚠ {w}
            </div>
          ))}
        </section>

        {/* ── discovery copilot: gaps + SME feedback (the HITL touch point) ── */}
        <section className="panel copilot-panel">
          <h3>Discovery copilot</h3>
          <p className="muted small">
            Findings surfaced by the platform. Challenged items are gaps for the SME to confirm or
            correct before the reports are generated.
          </p>
          {findings.length === 0 ? (
            <p className="muted small" style={{ marginTop: 12 }}>
              Review items appear once the assessment completes.
            </p>
          ) : (
            <ul className="gap-list">
              {findings.map((f) => (
                <li key={f.id} className={cx("gap", f.challenged && "is-gap")}>
                  <div className="gap-head">
                    <span className="gap-id">{f.id}</span>
                    {f.challenged ? (
                      <span className="badge b-med">Needs review</span>
                    ) : (
                      <span className="badge b-low">Verified</span>
                    )}
                  </div>
                  <div className="gap-title">{f.title}</div>
                  {f.sources.length > 0 && (
                    <div className="gap-src">{f.sources.join(" · ")}</div>
                  )}
                </li>
              ))}
            </ul>
          )}
          <div className="feedback-box">
            <textarea
              placeholder="SME feedback — a correction, a missing nuance, a source to check…"
              value={feedback}
              onChange={(e) => setFeedback(e.target.value)}
              disabled={!runId}
            />
            <button onClick={submitFeedback} disabled={!runId || !feedback.trim()}>
              Add feedback
            </button>
          </div>
          {sentNotes.map((n, i) => (
            <div className="sent-note" key={i}>
              ✓ {n}
            </div>
          ))}
        </section>
      </div>

      {/* ── preview: embed the report suite once the run is done ── */}
      <section className="panel preview-panel">
        <div className="preview-head">
          <h3>Preview — generated report suite</h3>
          {done && (
            <Link to={`/suite/${domain}`} className="open-suite">
              Open full suite ↗
            </Link>
          )}
        </div>
        {done ? (
          <iframe
            className="preview-frame"
            title="Report suite preview"
            src={`#/suite/${domain}/overview`}
          />
        ) : (
          <div className="preview-empty">
            <p className="muted">
              The interactive report suite appears here once generation completes — or{" "}
              <Link to={`/suite/${domain}`}>skip straight to the compiled reports</Link>.
            </p>
          </div>
        )}
      </section>
    </div>
  );
}

function labelFor(id: StageId): string {
  return STAGES.find((s) => s.id === id)?.label ?? id;
}
