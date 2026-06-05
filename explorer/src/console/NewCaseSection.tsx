import { useRef, useState } from "react";
import { cx } from "../lib/cx";
import { fileToUpload, ingestDocs } from "../lib/consoleApi";

/* "Initiate new case" — the dashboard's entry point for starting a discovery. Two paths:
 *   1. Upload your own documents → they're staged on the backend and a genuinely LIVE run starts.
 *   2. Run the pre-ingested Opella · O2C case → the curated, signed-off demo case.
 * The upload path is real: files are read in-browser, posted to /api/ingest, and the pipeline runs
 * on them for the real time it takes. A fresh case has no curated deliverable — the case shell shows
 * the live run honestly. */

const ACCEPT = ".pdf,.csv,.txt,.md,.docx,.xlsx,.json";
const MAX_FILES = 30;

export function NewCaseSection({
  backendUp,
  onRunPreingested,
  onIngested,
}: {
  backendUp: boolean | null;
  onRunPreingested: () => void;
  onIngested: (domain: string, runId: string) => void;
}) {
  const [files, setFiles] = useState<File[]>([]);
  const [title, setTitle] = useState("");
  const [dragOver, setDragOver] = useState(false);
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const inputRef = useRef<HTMLInputElement | null>(null);

  const offline = backendUp === false;

  function addFiles(incoming: FileList | File[]) {
    const next = [...files];
    for (const f of Array.from(incoming)) {
      if (!next.some((e) => e.name === f.name && e.size === f.size)) next.push(f);
    }
    setFiles(next.slice(0, MAX_FILES));
    setError(null);
  }

  function removeFile(name: string) {
    setFiles((fs) => fs.filter((f) => f.name !== name));
  }

  async function startUpload() {
    if (!files.length || busy) return;
    setBusy(true);
    setError(null);
    try {
      const payload = await Promise.all(files.map(fileToUpload));
      // /api/ingest already starts the live run — hand its run_id to the case shell so it subscribes
      // to that run rather than starting a redundant second one.
      const { domain, run_id } = await ingestDocs(title.trim() || "New discovery", payload);
      onIngested(domain, run_id);
    } catch (e) {
      setError(e instanceof Error ? e.message : "Could not start the discovery.");
      setBusy(false);
    }
  }

  return (
    <section className="initiate">
      <div className="initiate-head">
        <h2>Initiate a new discovery</h2>
        <p>Ingest your own source documents, or run the pre-ingested Opella case end-to-end.</p>
      </div>

      <div className="initiate-grid">
        {/* ── upload your own documents ── */}
        <div className={cx("nc-tile upload", dragOver && "is-drag", offline && "is-disabled")}>
          <div className="nc-tile-head">
            <span className="nc-badge">Upload</span>
            <h3>Your documents</h3>
            <p>SOPs, RACI, policies, system exports — PDF, CSV, TXT, DOCX, XLSX.</p>
          </div>

          <label className="nc-title-field">
            <span>Case name</span>
            <input
              type="text"
              placeholder="e.g. Acme · Procure-to-Pay"
              value={title}
              onChange={(e) => setTitle(e.target.value)}
              disabled={offline || busy}
            />
          </label>

          <button
            type="button"
            className="dropzone"
            onClick={() => inputRef.current?.click()}
            onDragOver={(e) => { e.preventDefault(); setDragOver(true); }}
            onDragLeave={() => setDragOver(false)}
            onDrop={(e) => {
              e.preventDefault();
              setDragOver(false);
              if (e.dataTransfer.files?.length) addFiles(e.dataTransfer.files);
            }}
            disabled={offline || busy}
          >
            <span className="dz-glyph">⬆</span>
            <span className="dz-main">Drop files here or <u>browse</u></span>
            <span className="dz-sub">up to {MAX_FILES} files</span>
          </button>
          <input
            ref={inputRef}
            type="file"
            multiple
            accept={ACCEPT}
            hidden
            onChange={(e) => { if (e.target.files) addFiles(e.target.files); e.target.value = ""; }}
          />

          {files.length > 0 && (
            <ul className="nc-files">
              {files.map((f) => (
                <li key={f.name}>
                  <span className="ncf-name">{f.name}</span>
                  <span className="ncf-size">{Math.max(1, Math.round(f.size / 1024))} KB</span>
                  <button className="ncf-x" onClick={() => removeFile(f.name)} disabled={busy}
                    aria-label={`remove ${f.name}`}>×</button>
                </li>
              ))}
            </ul>
          )}

          {error && <div className="nc-error">{error}</div>}

          <button className="nc-go" onClick={startUpload} disabled={offline || busy || !files.length}>
            {busy ? "Starting discovery…" : (
              <>▸ Start discovery <span className="nc-go-sub">{files.length} {files.length === 1 ? "document" : "documents"}</span></>
            )}
          </button>
          {offline && <div className="nc-foot-note">Start the engine (make console) to ingest.</div>}
        </div>

        {/* ── pre-ingested Opella O2C ── */}
        <div className={cx("nc-tile preingested", offline && "is-disabled")}>
          <div className="nc-tile-head">
            <span className="nc-badge accent">Pre-ingested</span>
            <h3>Opella · Order-to-Cash</h3>
            <p>The curated 12-document O2C case — the signed-off reference discovery.</p>
          </div>

          <dl className="nc-pre-facts">
            <div><dt>Documents</dt><dd>12</dd></div>
            <div><dt>Domain</dt><dd>O2C</dd></div>
            <div><dt>Reports</dt><dd>6</dd></div>
            <div><dt>Duration</dt><dd>~34 min</dd></div>
          </dl>

          <button className="nc-go accent" onClick={onRunPreingested} disabled={offline}>
            ▸ Run live <span className="nc-go-sub">real pipeline</span>
          </button>
          <div className="nc-foot-note">
            {offline ? "Start the engine (make console) to run." : "Streams a genuine run; the signed-off suite is shown on completion."}
          </div>
        </div>
      </div>
    </section>
  );
}
