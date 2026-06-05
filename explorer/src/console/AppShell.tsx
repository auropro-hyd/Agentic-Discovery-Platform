import { useState, type ReactNode } from "react";
import { NavLink } from "react-router-dom";
import { Logo } from "../layout/Logo";
import { cx } from "../lib/cx";

/* The enterprise application shell — a persistent navy left rail + a top app bar, wrapping the
 * Discovery Console pages (dashboard, case detail). Modelled on the Claims-Workbench reference so
 * the product reads as a real platform: branded rail, primary nav, settings pinned at the foot, a
 * top bar with the page title, a notification bell, and the operator avatar. */

interface NavEntry {
  to: string;
  label: string;
  icon: ReactNode;
  end?: boolean;
}

const NAV: NavEntry[] = [
  { to: "/", label: "Dashboard", end: true, icon: <GridIcon /> },
  { to: "/case/opella-o2c", label: "Discovery cases", icon: <FlowIcon /> },
];

export function AppShell({
  title,
  crumb,
  actions,
  children,
}: {
  title: string;
  crumb?: string;
  actions?: ReactNode;
  children: ReactNode;
}) {
  const [collapsed, setCollapsed] = useState(false);

  return (
    <div className={cx("shell", collapsed && "is-collapsed")}>
      <aside className="shell-rail">
        <div className="rail-brand">
          <Logo size={26} />
          {!collapsed && (
            <div className="rb-text">
              <div className="rb-name">AuroPro</div>
              <div className="rb-sub">Discovery Platform</div>
            </div>
          )}
          <button className="rail-toggle" onClick={() => setCollapsed((c) => !c)}
            aria-label={collapsed ? "expand sidebar" : "collapse sidebar"}>
            {collapsed ? "›" : "‹"}
          </button>
        </div>

        <nav className="rail-nav">
          {NAV.map((n) => (
            <NavLink key={n.to} to={n.to} end={n.end}
              className={({ isActive }) => cx("rail-item", isActive && "active")}
              title={n.label}>
              <span className="ri-icon">{n.icon}</span>
              {!collapsed && <span className="ri-label">{n.label}</span>}
            </NavLink>
          ))}
        </nav>

        <div className="rail-foot">
          <button className="rail-item" title="Settings" disabled>
            <span className="ri-icon"><GearIcon /></span>
            {!collapsed && <span className="ri-label">Settings</span>}
          </button>
        </div>
      </aside>

      <div className="shell-main">
        <header className="shell-bar">
          <div className="sb-titles">
            {crumb && <div className="sb-crumb">{crumb}</div>}
            <h1 className="sb-title">{title}</h1>
          </div>
          <div className="sb-right">
            {actions}
            <button className="sb-bell" aria-label="notifications" title="Notifications">
              <BellIcon />
            </button>
            <span className="sb-avatar" title="Operator">SU</span>
          </div>
        </header>
        <main className="shell-content">{children}</main>
      </div>
    </div>
  );
}

/* ── inline icons (stroke = currentColor, so they inherit rail/bar colour) ── */
function GridIcon() {
  return (
    <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
      <rect x="3" y="3" width="7" height="7" rx="1" /><rect x="14" y="3" width="7" height="7" rx="1" />
      <rect x="3" y="14" width="7" height="7" rx="1" /><rect x="14" y="14" width="7" height="7" rx="1" />
    </svg>
  );
}
function FlowIcon() {
  return (
    <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
      <circle cx="5" cy="6" r="2" /><circle cx="5" cy="18" r="2" /><circle cx="19" cy="12" r="2" />
      <path d="M7 6h6a2 2 0 0 1 2 2v2M7 18h6a2 2 0 0 0 2-2v-2" />
    </svg>
  );
}
function GearIcon() {
  return (
    <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
      <circle cx="12" cy="12" r="3" />
      <path d="M12 2v3M12 19v3M4.2 4.2l2.1 2.1M17.7 17.7l2.1 2.1M2 12h3M19 12h3M4.2 19.8l2.1-2.1M17.7 6.3l2.1-2.1" />
    </svg>
  );
}
function BellIcon() {
  return (
    <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
      <path d="M18 8a6 6 0 0 0-12 0c0 7-3 9-3 9h18s-3-2-3-9" /><path d="M13.7 21a2 2 0 0 1-3.4 0" />
    </svg>
  );
}
