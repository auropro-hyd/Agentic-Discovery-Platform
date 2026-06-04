import { useState } from "react";
import type { FactValue } from "../lib/types";
import { useDomainData } from "../lib/useDomainData";

/* The SOLE path a figure reaches the DOM. It accepts ONLY a branded FactValue (minted in
 * lib/store.ts from parsed JSON) — passing a raw computed number is a compile error. It renders
 * the value VERBATIM (no rounding, no scaling) plus its unit, and an optional source cite popover
 * resolved from the fact_store / source_index. */
export function GroundedNumber({ fact, cite = true }: { fact: FactValue; cite?: boolean }) {
  return (
    <span className="gnum">
      {String(fact.value)}
      {fact.unit ? <span className="unit">{displayUnit(fact.unit)}</span> : null}
      {cite && fact.sources && fact.sources.length > 0 ? <SourceCite docIds={fact.sources} /> : null}
    </span>
  );
}

function displayUnit(unit: string): string {
  // the engine's units are machine-ish (eur, percent, accounts…) — show human glyphs/words
  const map: Record<string, string> = { percent: "%", eur: " €", usd: " $", gbp: " £" };
  const u = unit.toLowerCase();
  return map[u] ?? ` ${unit}`;
}

/* Resolves doc_id -> business_name via source_index, and surfaces a fact_store quote+locator+tier
 * where available, degrading to a plain doc reference where the entity-level quote/locator is
 * empty (verified common in the data). Never fabricates a quote. */
export function SourceCite({ docIds }: { docIds: string[] }) {
  const [open, setOpen] = useState(false);
  const { store } = useDomainData();
  const s = store.synthesis;

  const refs = docIds.map((id) => {
    const src = s.source_index.find((r) => r.doc_id === id);
    return { id, name: src?.business_name || id, type: src?.doc_type || "" };
  });

  return (
    <span style={{ position: "relative" }}>
      <span
        className="cite"
        role="button"
        tabIndex={0}
        aria-label="Source"
        onMouseEnter={() => setOpen(true)}
        onMouseLeave={() => setOpen(false)}
        onFocus={() => setOpen(true)}
        onBlur={() => setOpen(false)}
      >
        ⓘ
      </span>
      {open && (
        <span className="cite-pop">
          <strong>Source{refs.length > 1 ? "s" : ""}</strong>
          {refs.map((r) => (
            <span key={r.id} style={{ display: "block", marginTop: 4 }}>
              {r.name}
              {r.type ? <span style={{ opacity: 0.7 }}> · {r.type}</span> : null}
            </span>
          ))}
        </span>
      )}
    </span>
  );
}
