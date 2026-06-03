# Security & data handling

## Reporting

Found a vulnerability or a data-exposure concern? **Do not open a public issue.**
Email the maintainers (anmol@auropro.com) with details. We aim to acknowledge within 3 business days.

## Data handling principles (built into the platform)

- **No secrets in git.** `.env` is gitignored; the LLM response cache (`prototype/.cache/`) is too.
  Provider keys live only in your local `.env`.
- **Client-agnostic by default.** The platform shows no organisation name unless one is detected
  from the documents; a run can suppress a detected name. Client-facing reports pass a no-leak
  guard (no tool names, filenames, or suppressed client names) before they are written.
- **Grounded, not fabricated.** Every number in a client report traces to data the tools computed;
  a grounding gate rejects ungrounded figures.
- **Where the LLM runs.** Configurable per engagement (Anthropic API or Azure OpenAI in your
  tenant). For regulated/client data, prefer an in-tenant deployment and a no-training agreement.

## Note on this repository

Reference artefacts (`prototype/out/`, `prototype/golden/`, `shared_context/`) may contain
engagement-specific names in raw/internal layers. Treat repository access accordingly.
