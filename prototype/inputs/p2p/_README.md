# inputs/p2p/ — Procure-to-Pay document set (cross-domain proof)

A small synthetic Procure-to-Pay set used to prove the platform generalises to any domain with zero
code changes. The actual documents are **gitignored**; see `../../docs/INPUT_CONTRACT.md` for the
expected shape.

`_manifest.json` here sets an explicit (fictional) client "Acme Manufacturing" — demonstrating the
manifest-override path (vs. O2C, which detects-and-suppresses its org name).
