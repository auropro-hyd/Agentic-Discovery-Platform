/* Client for the Discovery Console backend (v1/server.py). The backend drives run.py and streams
 * phase progress over SSE. Base URL is configurable for deployment; defaults to the local backend. */

export const API_BASE =
  (import.meta.env.VITE_CONSOLE_API as string | undefined)?.replace(/\/$/, "") ||
  "http://127.0.0.1:8742";

/** Absolute URL for a backend-served archive asset (the curated demo suite). The backend serves
 * archive/ verbatim at /archive/...; these are the report/preview/audit-trail HTMLs the case
 * stages iframe or link to. */
export function archiveUrl(path: string): string {
  return `${API_BASE}/archive/${path.replace(/^\/+/, "")}`;
}

/* The 6 case stages. `id` stays stable (the backend/run.py emit these), `label` is Akhilesh's naming. */
export const STAGES = [
  { id: "upload", label: "Ingestion" },
  { id: "assessment", label: "Domain Analysis" },
  { id: "discovery_copilot", label: "Discovery Co-pilot" },
  { id: "analysis", label: "Transformation Journey" },
  { id: "preview", label: "Findings Review" },
  { id: "report_generation", label: "Report Generation" },
] as const;

export type StageId = (typeof STAGES)[number]["id"];

/* ── Cases (the dashboard + case shell) ─────────────────────────────────────── */
export interface GapSummary {
  questions: number;
  high_resolved: number;
  clarifications: number;
  carried_forward: number;
}

export interface CaseCard {
  id: string;
  title: string;
  domain: string;
  client: string;
  run_date: string;
  duration_minutes: number;
  stage: StageId;
  status: string;
  doc_count: number;
  gaps: GapSummary;
  findings: number;
  opportunities: number;
}

export interface InputDoc {
  name: string;
  kind: string;
  kb: number;
}

export interface ReportLink {
  id: string;
  title: string;
  file: string;
  url: string;
}

export interface GapLedgerItem {
  id: string;
  severity: "high" | "clarification" | "amber";
  status: string;
  question: string;
  decision: string;
  resolves: string;
}

export interface CaseDetail extends CaseCard {
  input_docs: InputDoc[];
  gap_ledger: GapLedgerItem[];
  reports: ReportLink[];
  copilot_audit_url: string;
  preview_url: string;
}

export async function getCases(): Promise<CaseCard[]> {
  try {
    const r = await fetch(`${API_BASE}/api/cases`);
    if (!r.ok) return [];
    return ((await r.json()).cases ?? []) as CaseCard[];
  } catch {
    return [];
  }
}

export async function getCase(id: string): Promise<CaseDetail | null> {
  try {
    const r = await fetch(`${API_BASE}/api/case/${id}`);
    if (!r.ok) return null;
    return (await r.json()) as CaseDetail;
  } catch {
    return null;
  }
}

export interface RunEvent {
  type: "stage" | "activity" | "warn" | "feedback" | "error" | "done";
  stage?: StageId;
  state?: "active" | "done";
  text?: string;
  note?: string;
  message?: string;
  ok?: boolean;
  domain?: string;
}

export interface FindingItem {
  id: string;
  title: string;
  confidence: string;
  severity: string;
  challenged: boolean;
  challenge: string;
  sources: string[];
}

/** Health check — used to tell "backend offline" from "run failed". */
export async function ping(): Promise<boolean> {
  try {
    const r = await fetch(`${API_BASE}/healthz`, { signal: AbortSignal.timeout(2500) });
    return r.ok;
  } catch {
    return false;
  }
}

/** Start a genuinely LIVE run (always --fresh on the backend — no mode selector). */
export async function startRun(domain: string): Promise<string> {
  const r = await fetch(`${API_BASE}/api/run`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ domain }),
  });
  if (!r.ok) throw new Error((await r.json().catch(() => ({})))?.error || `run failed (${r.status})`);
  return (await r.json()).run_id as string;
}

/** Open the SSE stream; calls onEvent per event. Returns a close() to stop. */
export function streamRun(runId: string, onEvent: (e: RunEvent) => void): () => void {
  const es = new EventSource(`${API_BASE}/api/stream/${runId}`);
  es.onmessage = (m) => {
    try {
      onEvent(JSON.parse(m.data) as RunEvent);
    } catch {
      /* ignore malformed frame */
    }
  };
  es.onerror = () => {
    /* EventSource auto-reconnects; the backend replays history on resubscribe */
  };
  return () => es.close();
}

export async function getFindings(domain: string): Promise<FindingItem[]> {
  try {
    const r = await fetch(`${API_BASE}/api/findings/${domain}`);
    if (!r.ok) return [];
    return ((await r.json()).findings ?? []) as FindingItem[];
  } catch {
    return [];
  }
}

export async function sendFeedback(runId: string, note: string): Promise<void> {
  await fetch(`${API_BASE}/api/feedback`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ run_id: runId, note }),
  }).catch(() => {});
}
