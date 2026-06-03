# inputs/o2c/ — Order-to-Cash document set

The actual documents (PDFs/CSVs/notes) are **gitignored** — they carry synthetic/client data and the
organisation name. Drop a domain's documents here to run the platform on it; see
`../../docs/INPUT_CONTRACT.md` for the expected shape.

This O2C set (12 documents) is kept locally and also archived in
`shared_context/from-akhilesh/synthetic-inputs-extracted/`.

Optional sidecars in this folder:
- `_manifest.json` — domain label, optional client name, `suppress_client`, effort numbers.
- `_resolutions.json` — SME resolutions for non-interactive runs.
