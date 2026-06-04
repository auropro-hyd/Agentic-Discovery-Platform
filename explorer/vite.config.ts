import { defineConfig } from "vite";
import react from "@vitejs/plugin-react";

// base:'./' => relative asset URLs, so the built dist/ opens from file:// and from any
// sub-path on a static host with no rewrite rules. Paired with HashRouter for deep links.
export default defineConfig({
  base: "./",
  plugins: [react()],
  build: {
    outDir: "dist",
    // the per-domain JSON is code-split via dynamic import in lib/domains.ts
    chunkSizeWarningLimit: 900,
  },
});
