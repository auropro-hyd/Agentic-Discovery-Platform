import { createContext, useContext } from "react";
import type { DomainStore } from "./store";
import type { DocRecord } from "./buildSearchIndex";

export interface DomainData {
  store: DomainStore;
  searchIndex: DocRecord[];
}

export const DomainDataContext = createContext<DomainData | null>(null);

/** Access the active domain's store + search index. Throws if used outside DomainLayout. */
export function useDomainData(): DomainData {
  const ctx = useContext(DomainDataContext);
  if (!ctx) throw new Error("useDomainData must be used within a DomainLayout");
  return ctx;
}
