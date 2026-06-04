/* Client for the Discovery Console backend (v1/server.py). The backend drives run.py and streams
 * phase progress over SSE. Base URL is configurable for deployment; defaults to the local backend. */

export const API_BASE =
  (import.meta.env.VITE_CONSOLE_API as string | undefined)?.replace(/\/$/, "") ||
  "http://127.0.0.1:8742";

export const STAGES = [
  { id: "upload", label: "Uploading documents" },
  { id: "assessment", label: "Assessment" },
  { id: "discovery_copilot", label: "Discovery copilot" },
  { id: "analysis", label: "Analysis" },
  { id: "preview", label: "Preview" },
  { id: "report_generation", label: "Report generation" },
] as const;

export type StageId = (typeof STAGES)[number]["id"];

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

export async function startRun(domain: string, mode: "live" | "golden"): Promise<string> {
  const r = await fetch(`${API_BASE}/api/run`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ domain, mode }),
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
