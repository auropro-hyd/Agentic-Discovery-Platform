import { cx } from "../lib/cx";

/* The DDD bounded-context map for the explorer — the same grounded data the print suite draws as
 * an SVG, rendered here as classified context cards inside the domain boundary, with a shared-
 * kernel band and DDD relationship notes. Renders nothing when the engine emitted no contexts
 * (e.g. a thin domain) — never fabricates structure. */

interface Rel {
  to?: string;
  kind?: string;
  label?: string;
}
export interface Ctx {
  name?: string;
  kind?: string;
  owner?: string;
  responsibilities?: string;
  is_shared_kernel?: boolean;
  relationships?: Rel[];
}

const KIND_LABEL: Record<string, string> = {
  core: "Core",
  supporting: "Supporting",
  generic: "Generic",
  external: "External",
};
const REL_LABEL: Record<string, string> = {
  customer_supplier: "Customer–Supplier",
  conformist: "Conformist",
  anti_corruption_layer: "Anti-corruption layer",
  open_host_service: "Open-host service",
  shared_kernel: "Shared kernel",
  partnership: "Partnership",
};

export function BoundedContextMap({ contexts, domainLabel }: { contexts: Ctx[]; domainLabel: string }) {
  const items = (contexts ?? []).filter((c) => c?.name);
  if (items.length < 2) return null;
  const kernel = items.find((c) => c.is_shared_kernel);
  const cells = items.filter((c) => c !== kernel);

  return (
    <div className="bctx">
      <div className="bctx-frame">
        <div className="bctx-boundary">{(domainLabel || "Domain").toUpperCase()} — DOMAIN BOUNDARY</div>
        <div className="bctx-grid">
          {cells.map((c) => {
            const kind = (c.kind || "core").toLowerCase();
            return (
              <div key={c.name} className={cx("bctx-card", `bk-${kind in KIND_LABEL ? kind : "core"}`)}>
                <div className="bctx-name">{c.name}</div>
                {c.owner && <div className="bctx-owner">{c.owner}</div>}
                {c.responsibilities && <div className="bctx-resp">{c.responsibilities}</div>}
                <span className={cx("bctx-tag", `bt-${kind in KIND_LABEL ? kind : "core"}`)}>
                  {KIND_LABEL[kind] ?? "Core"}
                </span>
                {c.relationships && c.relationships.length > 0 && (
                  <div className="bctx-rels">
                    {c.relationships
                      .filter((r) => r.to)
                      .map((r, i) => (
                        <span className="bctx-rel" key={i}>
                          → {r.to}
                          {r.kind ? ` (${REL_LABEL[r.kind] ?? r.kind})` : ""}
                        </span>
                      ))}
                  </div>
                )}
              </div>
            );
          })}
        </div>
        {kernel && (
          <div className="bctx-kernel">
            <strong>{kernel.name} — Shared Kernel</strong>
            {kernel.responsibilities && <span> · {kernel.responsibilities}</span>}
          </div>
        )}
      </div>
      <p className="tnote">
        Subdomains classified core / supporting / generic / external; relationships show the DDD
        integration pattern between contexts.
      </p>
    </div>
  );
}
