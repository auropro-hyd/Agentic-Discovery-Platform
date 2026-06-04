import { useEffect, useMemo, useState } from "react";
import { Outlet, useParams, Navigate } from "react-router-dom";
import { isKnownDomain, DOMAIN_SLUGS } from "../lib/domains";
import { loadDomain, LoadError } from "../lib/loadSynthesis";
import type { DomainStore } from "../lib/store";
import { buildSearchIndex } from "../lib/buildSearchIndex";
import { DomainDataContext, type DomainData } from "../lib/useDomainData";
import { ErrorBoundary } from "./ErrorBoundary";
import { Sidebar } from "./Sidebar";
import { TopBar } from "./TopBar";

export function DomainLayout() {
  const { domain } = useParams();

  if (!isKnownDomain(domain)) {
    const fallback = DOMAIN_SLUGS[0] ?? "o2c";
    return <Navigate to={`/${fallback}`} replace />;
  }

  return (
    <ErrorBoundary key={domain}>
      <DomainShell domain={domain} />
    </ErrorBoundary>
  );
}

function DomainShell({ domain }: { domain: string }) {
  const [store, setStore] = useState<DomainStore | null>(null);
  const [error, setError] = useState<Error | null>(null);

  useEffect(() => {
    let live = true;
    setStore(null);
    setError(null);
    loadDomain(domain)
      .then((s) => live && setStore(s))
      .catch((e) => live && setError(e instanceof Error ? e : new LoadError(String(e))));
    return () => {
      live = false;
    };
  }, [domain]);

  if (error) throw error; // let ErrorBoundary render the banner

  const data: DomainData | null = useMemo(
    () => (store ? { store, searchIndex: buildSearchIndex(store) } : null),
    [store],
  );

  return (
    <div className="shell">
      <Sidebar domain={domain} domainLabel={store?.domainLabel ?? ""} clientDisplay={store?.clientDisplay ?? ""} />
      <div className="main">
        <TopBar domain={domain} />
        <main className="content">
          {data ? (
            <DomainDataContext.Provider value={data}>
              <Outlet />
            </DomainDataContext.Provider>
          ) : (
            <div className="loading">Loading {domain.toUpperCase()} suite…</div>
          )}
        </main>
      </div>
    </div>
  );
}
