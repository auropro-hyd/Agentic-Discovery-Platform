# shared_context/ — local working context (NOT committed)

This folder holds material we keep **locally** for reference but do **not** push to the repo. It is
gitignored. Use it for raw inputs, hand-offs, and anything that's useful context but isn't our
shippable product.

## Contents

Akhilesh shared material in two waves; both are preserved here for full provenance.

```
shared_context/
  from-akhilesh/
    v1-first-version/                  the ORIGINAL material (first version)
      specs/                           the first design-spec set (incl. steelman review,
                                       demand-planning + O2C demo scripts) — was the repo's
                                       original committed specs/ tree
      Opella - Autonomous Discovery Platform.md   the original master design/engagement doc

    v2-second-version/                 the LATER material (drove the actual build)
      specs.zip                        spec bundle (second version)
      synthetic-inputs.zip             synthetic-data bundle (generators + generated docs)
      specs-extracted/                 unzipped specs.zip — incl. the authoritative
                                       2026-06-01-autonomous-discovery-platform-understanding.md,
                                       the O2C demo guide, and the value/feasibility + timeline mockups
      synthetic-inputs-extracted/      unzipped synthetic-inputs.zip — generators, tests, and the
                                       12 source O2C documents (output/o2c/)
```

**v1 vs v2:** the two sets overlap but diverge — v2 added the 2026-06-01 understanding doc and
new HTML mockups; v1 had a steelman review and a demand-planning demo script that v2 dropped.
v2 is the authoritative basis for what was built.

## Why it's here and not in the repo

- It's **received material**, not our work product — Akhilesh's raw docs, the synthetic-data
  generators, and the source PDFs/CSVs. Not ours to commit.
- It may contain the **real client/org name** in source documents; the committed product is
  deliberately client-agnostic, so this stays out of the pushed repo.
- Keeping it organised here (vs. scattered dotfolders at the root) makes it easy to re-zip,
  hand off, or re-reference.

## Relationship to the prototype

The prototype is **self-contained** — the O2C input documents it runs on live in
`v1/inputs/o2c/` (copied in earlier). Nothing in the prototype depends on this folder;
it's purely reference/archive.
