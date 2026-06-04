import { Link } from "react-router-dom";

/** A simple breadcrumb / back-chip. Used on detail pages; honours a ?from= cross-link trail. */
export function Crumb({ items }: { items: Array<{ label: string; to?: string }> }) {
  return (
    <nav className="crumb" aria-label="Breadcrumb">
      {items.map((it, i) => (
        <span key={i}>
          {i > 0 && <span className="sep"> / </span>}
          {it.to ? <Link to={it.to}>{it.label}</Link> : <span>{it.label}</span>}
        </span>
      ))}
    </nav>
  );
}

export function BackChip({ to, label }: { to: string; label: string }) {
  return (
    <Link to={to} className="backchip">
      ← {label}
    </Link>
  );
}
