import type { DataTable as DataTableT } from "../lib/types";

/* Renders a grounded data table verbatim from the engine (current_state.data_tables / a pain
 * point's detail_table). Columns, rows, caption, note all come straight from JSON; no view-layer
 * computation. Numeric-looking cells are right-aligned for readability only. */

function isNumeric(v: string | number | null): boolean {
  if (typeof v === "number") return true;
  if (v == null) return false;
  return /^[€$£]?\s?[\d,.]+%?$/.test(String(v).trim()) && /\d/.test(String(v));
}

export function DataTable({ table }: { table: DataTableT }) {
  const cols = table.columns ?? [];
  const rows = table.rows ?? [];
  if (!cols.length && !rows.length) return null;
  return (
    <figure style={{ margin: "0 0 16px" }}>
      {(table.title || table.caption) && (
        <figcaption style={{ marginBottom: 8 }}>
          {table.title && <strong style={{ color: "var(--navy)" }}>{table.title}</strong>}
          {table.caption && <span className="small muted"> — {table.caption}</span>}
        </figcaption>
      )}
      <table className="dt">
        {cols.length > 0 && (
          <thead>
            <tr>
              {cols.map((c, i) => (
                <th key={i}>{c}</th>
              ))}
            </tr>
          </thead>
        )}
        <tbody>
          {rows.map((row, ri) => (
            <tr key={ri}>
              {row.map((cell, ci) => (
                <td key={ci} className={isNumeric(cell) ? "num" : ""}>
                  {cell == null ? "—" : String(cell)}
                </td>
              ))}
            </tr>
          ))}
        </tbody>
      </table>
      {table.note && <p className="tnote">{table.note}</p>}
    </figure>
  );
}
