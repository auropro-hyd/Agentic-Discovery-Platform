/* Domain registry, derived at build time from the synced JSON files in src/data/.
 * Adding a future domain is literally "drop discovery-<slug>.json into v1/out + npm run sync:data"
 * — import.meta.glob picks it up, no code change. Each domain is dynamically imported (code-split)
 * so first paint only loads the active domain's chunk. */

// eager:false => each file becomes a () => Promise<module> loader (lazy, code-split)
const loaders = import.meta.glob("../data/discovery-*.json");

export interface DomainEntry {
  slug: string;
  load: () => Promise<unknown>;
}

function slugFromPath(path: string): string {
  const m = path.match(/discovery-(.+)\.json$/);
  return m && m[1] ? m[1] : path;
}

export const DOMAINS: DomainEntry[] = Object.entries(loaders)
  .map(([path, load]) => ({ slug: slugFromPath(path), load: load as () => Promise<unknown> }))
  .sort((a, b) => a.slug.localeCompare(b.slug));

export const DOMAIN_SLUGS = DOMAINS.map((d) => d.slug);

export function isKnownDomain(slug: string | undefined): slug is string {
  return !!slug && DOMAIN_SLUGS.includes(slug);
}

export function loaderFor(slug: string): (() => Promise<unknown>) | undefined {
  return DOMAINS.find((d) => d.slug === slug)?.load;
}
