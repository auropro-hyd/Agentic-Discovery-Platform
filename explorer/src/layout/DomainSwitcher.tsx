import { useNavigate, useLocation } from "react-router-dom";
import { DOMAIN_SLUGS } from "../lib/domains";
import { cx } from "../lib/cx";

/* o2c / p2p segmented toggle. Navigates to the SAME section in the other domain, but drops any
 * trailing :id (a PP/OPP id is domain-specific, so we land on that section's index rather than a
 * 404). Falls back to /overview if the path can't be re-sectioned. */
export function DomainSwitcher({ current }: { current: string }) {
  const navigate = useNavigate();
  const { pathname } = useLocation();

  function go(slug: string) {
    if (slug === current) return;
    // pathname looks like /<domain>/<section>[/<id>]
    const parts = pathname.split("/").filter(Boolean); // [domain, section, id?]
    const section = parts[1] ?? "overview";
    navigate(`/${slug}/${section}`);
  }

  if (DOMAIN_SLUGS.length < 2) return null;

  return (
    <div className="domain-switch" role="tablist" aria-label="Domain">
      {DOMAIN_SLUGS.map((slug) => (
        <button
          key={slug}
          role="tab"
          aria-selected={slug === current}
          className={cx(slug === current && "active")}
          onClick={() => go(slug)}
        >
          {slug.toUpperCase()}
        </button>
      ))}
    </div>
  );
}
