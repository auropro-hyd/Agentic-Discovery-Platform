import type { DomainStore } from "./store";

/* Flatten the suite into a small in-memory search corpus (~60 records for o2c). Each record
 * deep-links to its detail route. A `kind:"assumption"` flag lets the results UI render planning
 * assumptions with the planning badge, so a forward-looking statement never reads as fact. */

export type RecordKind =
  | "pain_point"
  | "opportunity"
  | "assumption"
  | "evidence"
  | "source"
  | "quote"
  | "table"
  | "metric";

export interface DocRecord {
  id: string;
  kind: RecordKind;
  title: string;
  snippet: string;
  route: string; // hash route (without leading #)
  text: string; // lowercased haystack
}

function rec(r: Omit<DocRecord, "text">): DocRecord {
  return { ...r, text: `${r.title} ${r.snippet}`.toLowerCase() };
}

export function buildSearchIndex(store: DomainStore): DocRecord[] {
  const d = store.domain;
  const s = store.synthesis;
  const out: DocRecord[] = [];

  for (const pp of s.pain_points) {
    out.push(
      rec({
        id: pp.id,
        kind: "pain_point",
        title: pp.title || pp.id,
        snippet: [pp.description, pp.root_cause, pp.business_consequence].filter(Boolean).join(" "),
        route: `/suite/${d}/pain-points/${pp.id}`,
      }),
    );
  }
  for (const opp of s.opportunities) {
    out.push(
      rec({
        id: opp.id,
        kind: "opportunity",
        title: opp.title || opp.id,
        snippet: [opp.overview, opp.implementation_approach, opp.expected_behaviour].filter(Boolean).join(" "),
        route: `/suite/${d}/opportunities/${opp.id}`,
      }),
    );
  }
  s.planning_assumptions.forEach((pa, i) => {
    out.push(
      rec({
        id: `pa-${i}`,
        kind: "assumption",
        title: pa.statement || "Planning assumption",
        snippet: [pa.kind && `(${pa.kind})`, pa.basis].filter(Boolean).join(" "),
        route: `/suite/${d}/assumptions`,
      }),
    );
  });
  s.evidence_register.forEach((e, i) => {
    out.push(
      rec({
        id: `ev-${i}`,
        kind: "evidence",
        title: e.finding || e.data_point || "Evidence",
        snippet: [e.data_point, e.evidence_type, e.source, e.confidence].filter(Boolean).join(" "),
        route: `/suite/${d}/evidence`,
      }),
    );
  });
  for (const src of s.source_index) {
    out.push(
      rec({
        id: src.doc_id,
        kind: "source",
        title: src.business_name || src.doc_id,
        snippet: [src.doc_type, src.what_we_read].filter(Boolean).join(" "),
        route: `/suite/${d}/evidence`,
      }),
    );
  }
  (s.fact_store?.quotes ?? []).forEach((q, i) => {
    if (!q.text) return;
    out.push(
      rec({ id: `q-${i}`, kind: "quote", title: q.text, snippet: q.doc_id, route: `/suite/${d}/evidence` }),
    );
  });
  (s.current_state?.data_tables ?? []).forEach((t, i) => {
    out.push(
      rec({
        id: `t-${i}`,
        kind: "table",
        title: t.title || t.caption || "Data table",
        snippet: [t.caption, (t.columns ?? []).join(" ")].filter(Boolean).join(" "),
        route: `/suite/${d}/current-state`,
      }),
    );
  });
  /* metrics_framework is intentionally NOT indexed: it has no dedicated page/anchor to deep-link to
   * (it previously routed to /opportunities, a dead-end with no metric anchor). Re-add a `metric`
   * record here once a metrics view exists to route into. */
  return out;
}

/** case-insensitive token-AND substring search. Empty query => []. */
export function search(index: DocRecord[], query: string): DocRecord[] {
  const tokens = query.toLowerCase().split(/\s+/).filter(Boolean);
  if (!tokens.length) return [];
  return index.filter((r) => tokens.every((t) => r.text.includes(t)));
}
