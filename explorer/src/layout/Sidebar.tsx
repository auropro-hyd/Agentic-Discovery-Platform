import { NavLink, Link } from "react-router-dom";
import { Logo } from "./Logo";

/* The navy left rail. Nav items carry .secnum chips mirroring the print suite's report numbering
 * (00 Executive Summary … 06 Supporting Artefacts), plus the two SPA-native ledger routes
 * (Assumptions, Search is in the top bar). */

interface NavItem {
  num: string;
  to: string;
  label: string;
}

const PRIMARY: NavItem[] = [
  { num: "00", to: "overview", label: "Overview" },
  { num: "01", to: "current-state", label: "Current state" },
  { num: "02", to: "pain-points", label: "Pain points" },
  { num: "03", to: "opportunities", label: "Opportunities" },
  { num: "04", to: "roadmap", label: "Roadmap" },
];

const PROVENANCE: NavItem[] = [
  { num: "05", to: "traceability", label: "Traceability" },
  { num: "06", to: "evidence", label: "Evidence & sources" },
  { num: "·", to: "assumptions", label: "Planning assumptions" },
];

function Item({ domain, item }: { domain: string; item: NavItem }) {
  return (
    <NavLink to={`/suite/${domain}/${item.to}`} className={({ isActive }) => (isActive ? "active" : "")}>
      <span className="secnum">{item.num}</span>
      <span>{item.label}</span>
    </NavLink>
  );
}

export function Sidebar({
  domain,
  domainLabel,
  clientDisplay,
}: {
  domain: string;
  domainLabel: string;
  clientDisplay?: string;
}) {
  const subtitle = [domainLabel, clientDisplay && clientDisplay !== domainLabel ? clientDisplay : ""]
    .filter(Boolean)
    .join(" · ");
  return (
    <aside className="sidebar">
      <div className="brand">
        <Logo />
        <div>
          <div className="name">AUROPRO</div>
          <div className="sub">Discovery Explorer</div>
        </div>
      </div>
      <nav>
        {subtitle && <div className="navgroup">{subtitle}</div>}
        {PRIMARY.map((it) => (
          <Item key={it.to} domain={domain} item={it} />
        ))}
        <div className="navgroup">Provenance</div>
        {PROVENANCE.map((it) => (
          <Item key={it.to} domain={domain} item={it} />
        ))}
        <Link to="/" className="console-back">
          ← Discovery console
        </Link>
      </nav>
    </aside>
  );
}
