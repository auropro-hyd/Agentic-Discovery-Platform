# Market Synthesis — Where We Win, Where We're Exposed

_Market research generated 2026-06-02 via a multi-agent web-research workflow (11 agents, deep web
search + analyst/review mining). Cited throughout (see the per-category dossiers for full source
URLs). This is a standing reference — read it instead of re-searching._

> **Product under analysis (the AuroPro Autonomous Discovery Platform):** an LLM-agent + tool-use
> platform that ingests an enterprise's heterogeneous business documents (SOPs, policies, RACIs,
> system CSV exports, working notes) for a domain (O2C, P2P, …) and **autonomously discovers
> findings** — contradictions between documented process and actual system data, undocumented /
> unowned processes, control gaps — by computing over the data with generic tools (code does the
> math; the agent reasons). It emits a client-ready **6-report suite** with confidence/provenance
> and a **grounding gate** (consistent-not-fabricated, no tool jargon), runs on any domain's docs
> with zero config, and is delivered as a **consulting accelerator**, not per-seat SaaS.

---

## 1. The competitive landscape (one page)

We sit at the **intersection of five well-funded categories, and that intersection is currently
unoccupied.** No single incumbent does what we do; each category owns one axis of the problem and
is structurally anchored to its original data dependency.

1. **Process Mining** — Celonis (~$13B), SAP Signavio, UiPath, Microsoft Power Automate,
   Apromore (Salesforce, Nov 2025), ABBYY Timeline. Owns *quantified reality of structured
   processes* from **event logs** (Case ID + Activity + Timestamp). Strength = its cage: **no event
   log → no analysis**; blind to unstructured docs and to manual/off-system/undocumented/unowned
   work. Consumption/seat SaaS ($150K–$5M+), 12–24 month implementations, ~80% of effort in ETL.

2. **APM / Rationalization & EA** — SAP LeanIX, ServiceNow APM (CMDB/Discovery), IBM Apptio,
   Ardoq, Bizzdesign/Alfabet, MEGA HOPEX. Owns *the persistent application-portfolio repository* and
   TIME-framework rationalization. Central weakness: the repository is **survey/questionnaire-fed**
   (or CMDB-fed) and **must be maintained by hand or it rots** — the #1 documented failure mode is
   data-gathering stall and stale data (Gartner: only ~25% think EA is effective).

3. **LLM / Agentic Enterprise Knowledge** — Glean, Microsoft 365 Copilot, Palantir AIP/Foundry,
   Hebbia, Cyera (+ Celonis as adjacent). Owns *the reasoning/retrieval substrate*. But their graph
   is a **retrieval/context graph** (content-people-activity) — it answers questions and routes
   agents; it does **not compute over the numeric content of CSVs**, does not adjudicate
   documented-vs-actual contradictions, and does not emit a grounded consulting deliverable.
   Per-seat SaaS at scale; persistent hallucination is a documented production problem.

4. **Consulting Accelerators** — Accenture (GenWizard/AI Refinery), Deloitte (Ascend + Process
   Bionics), PwC (agent OS + Process Intelligence), Capgemini (eAPM/RAISE), TCS/Infosys/Wipro
   (MasterCraft/Topaz/ai360). "Methodology + people, accelerated by proprietary IP." They own *the
   client relationship and the narrative deliverable* — **and are our delivery channel, not a SaaS
   rival.** None is purpose-built to autonomously discover contradictions from messy docs; their
   typical output is a slide deck, implementation left to the client.

5. **Carve-out / TSA-exit** — PwC, Deloitte, EY, KPMG (+ West Monroe, FTI; SNP CrystalBridge for
   SAP data; Device42/ServiceNow/Faddom for infra dependency). Owns *the separation program*. The
   tooling splits into PMO/TSA trackers, financials engines, CMDB/dependency mappers, and data
   movers — **none autonomously discovers process/control findings from documents.** The
   finding-work is done entirely by people today.

**The map:** every category is racing toward "feed context to AI agents" (Celonis MCP server;
Salesforce/Apromore→Agentforce; Glean autonomous agents; Big-4 agent platforms) — toward *our*
layer. But each is anchored to its origin: an event log, a maintained repository, a retrieval
graph, an army of consultants, a separation PMO. **We start where they end: the heterogeneous,
unstructured corpus they discard, reasoned over autonomously, delivered as a consulting accelerator.**

The one-line truth: **the incumbents quantify, store, retrieve, or execute over what already
exists in structured form; we discover the documented-vs-actual contradictions and the processes
and controls that aren't in any system, log, or repository.**

---

## 2. Where each category's leaders out-compete us (honest)

- **Process mining:** statistically exhaustive rigor on high-volume timestamped processes
  (variants, bottlenecks, conformance %, cycle times); real-time/continuous monitoring; simulation
  & prediction; closed-loop automation (UiPath/MS/Celonis/Salesforce); maturity, Gartner standing,
  prebuilt connectors, procurement fit on existing enterprise agreements.
- **APM / EA:** a **persistent system of record** with live dashboards, lifecycle tracking, and
  multi-year governance — we produce a point-in-time deliverable, not a standing EA tool.
  ServiceNow's automated technical inventory & dependency mapping at scale is real and beyond us.
- **LLM knowledge:** **scale, connector breadth, continuous indexing, and agent execution** —
  Glean/Copilot serve thousands of users live across 100+ connectors and (late 2025) execute tasks;
  we are domain-scoped and point-in-time. Palantir's ontology depth is deeper (and heavier).
- **Consulting:** **board-level trust, references, delivery muscle, and pre-built IP** (Deloitte's
  1000+ industry agents, Accenture's NVIDIA-backed library). "Deloitte stands behind this" beats
  "we used AuroPro's tool" in a CxO bake-off — they own the room.
- **Carve-out:** **physical execution and technical truth** (Device42/ServiceNow auto-discover
  infra; SNP actually moves SAP data) and **deal access** (the Big-4 own the board/PE relationships
  that originate a €16B Opella-class separation).

**Brutal one-liner:** *On any axis where the data is already structured, already in a system,
already in a maintained repository, or where a human will attest to it, the incumbents win. We only
win where the truth is scattered, undocumented, or contradictory — exactly where the value hides,
but it requires us to teach the buyer that this gap exists.*

---

## 3. Our genuine differentiators

1. **We read the documents they can't.** Core input is the unstructured corpus + system CSVs.
   Process-mining literature confirms direct application "is not possible" without
   Case ID/Activity/Timestamp; documents have none (arXiv 2401.13677).
2. **We discover the invisible** — undocumented, manual, off-system, **unowned** processes and
   control gaps that span a policy + a spreadsheet + an email. The structural blind spot of mining
   *and* of CMDB/repository tools.
3. **Cross-modal contradiction detection** — we compute the gap between what the SOP/policy *says*
   and what the system data *shows*. No single-modality tool does this.
4. **Compute-grounded, not retrieved or hallucinated** — code does the math
   (describe/group_by/join_diff/filter_count over any CSV), the agent reasons, and a **grounding
   gate** verifies every number traces to data. This is the direct answer to "but LLMs fabricate"
   (a documented failure for Copilot, and the Deloitte AU$439K refunded-report incident).
5. **Zero-config, any domain, fast TTV** — hours-to-days to first finding vs. 12–24 month
   implementations and the ~80%-ETL / survey-fatigue tax of mining and APM.
6. **Autonomous reasoning → client-ready narrative**, not a graph for an analyst to interpret: the
   full 6-report suite with confidence/provenance and no tool jargon.
7. **Delivery-model fit** — a consulting accelerator for time-boxed engagements, especially
   post-carve-out / TSA-exit rationalisation — not a per-seat SaaS that is overkill and too slow to
   stand up for an episodic, deadline-driven event.

---

## 4. The single most defensible wedge

**"The contradiction & unowned-process layer for post-carve-out / TSA-exit rationalisation —
discovered from the documents and data you already have, delivered as a consulting accelerator in
days."**

Why this beats both "a cheaper/faster Celonis" (loses on rigor) and "an AI consultant" (too vague):

- **It targets a moment, not a market.** A carve-out / TSA exit is a forced, deadline-driven
  discovery event where (a) processes are *known* to be undocumented/contradictory, (b) ownership
  is genuinely unclear (the point of a carve-out), (c) there's no time to stand up a Celonis data
  model or a LeanIX repository, and (d) a consulting firm is *already engaged and accountable*.
  Every one of our differentiators is a buying criterion. The market is large and growing: ~70% of
  large companies plan a carve-out by 2026; reference deals (Sanofi/Opella ~€16B, Kenvue/J&J,
  Organon/Merck, Haleon/GSK, Sandoz/Novartis) each carry multi-year, multi-hundred-million IT
  separations; TSAs cost ~$150K–500K/month and involve 1,500+ interdependent decisions.
- **It is defensible against incumbents** because it is precisely their structural blind spot:
  there is no clean event log in a carve-out, the documents are the only ground truth, and
  "what process is unowned / what control falls through the TSA gap" is a contradiction-detection
  task, not a mining/CMDB/repository task.
- **It is defensible against "just build it on an agent stack"** because the grounding gate + the
  productised 6-report suite + the consulting-delivery wrapper is the hard, trust-bearing part —
  not the LLM call.

Land here, then expand horizontally into general domain discovery (O2C, P2P) and *co-exist* with
the incumbents ("they quantify/store/execute what already exists; we find what isn't").

---

## 5. Prioritised competitor gaps we can credibly resolve

Each gap → the capability that resolves it, and whether we **have** it or must **build** it. (Full
evidence + sources in the per-category dossiers and `gaps-we-can-exploit.md`.)

| # | Competitor gap (category) | Capability that resolves it | Have / Build |
|---|---|---|---|
| **P0** | Cannot derive process from unstructured docs (Process Mining) | LLM-agent extraction over SOPs/RACIs/notes — core design | **HAVE** |
| **P0** | Blind to manual/off-system/undocumented/unowned processes (Process Mining) | Missing/unowned-process discovery via cross-doc reasoning | **HAVE** |
| **P0** | No doc-vs-data contradiction detection (Process Mining, APM, LLM-knowledge) | Cross-modal compute: join_diff/filter_count over CSV vs. extracted SOP claims | **HAVE** |
| **P0** | APM/EA stalls on survey fatigue / stale, hand-maintained repository | We ingest the docs that already exist; point-in-time, no repository to feed | **HAVE** |
| **P1** | ~80% of effort = event-log ETL; 12–24 month TTV (Process Mining) | Zero-config ingestion; hours-to-days to first finding | **HAVE** |
| **P1** | High/opaque consumption or per-seat pricing, multi-year lock-in (all SaaS categories) | Fixed-scope accelerator pricing; no meter, no per-process license, no seat minimum | **HAVE (packaging)** |
| **P1** | Carve-out finding-work is 100% manual people-effort (Big-4/TSA) | Autonomous discovery compresses the data-gathering/extraction phase | **HAVE** |
| **P2** | "LLMs fabricate" — Copilot hallucinations; Deloitte AU$439K refunded report | Grounding gate: every number traces to data; provenance on findings | **HAVE** |
| **P2** | LLM-knowledge graphs retrieve but don't compute over CSV numerics (Glean/Copilot) | Generic compute tools over any CSV; agent reasons over results | **HAVE** |
| **P2** | Big-4 deliverable is a thin slide deck, implementation left to client | 6-report suite built for action (before/after per opportunity, roadmap, artefacts) | **HAVE** |
| **P3** | No conformance vs. a documented model (Process Mining) | Use the SOP *as* the to-be model; diff data against it — a doc-native conformance check | **BUILD (productise)** |
| **P3** | Point-in-time only, no monitoring (us vs. mining/APM) | "Discovery refresh" re-run on cadence (lighter than real-time) | **BUILD (roadmap)** |
| **P4** | Closed-loop automation / data migration / live infra scan (UiPath, SNP, Device42) | *Don't chase.* Recommend + hand off; partner, don't compete | **DO NOT BUILD** |

**Sequencing:** P0/P1 are pure positioning — we already win, we just need to *say and price* it.
P2 neutralises objections. P3 is the credible roadmap that turns a point-in-time accelerator into a
repeatable asset. **P4 is the trap** — automation/monitoring/migration is where incumbents are
strongest and our delivery model is wrong.

---

## 6. Pricing & packaging implications

1. **Sell the inverse of the incumbent model.** They sell per-seat/consumption SaaS with multi-year
   lock-in and unpredictable, volume-based bills (the #1 complaint across mining, APM, LLM-knowledge:
   "hard to estimate cost," "most expensive in the market," "100-seat minimum"). We sell a
   **fixed-scope, fixed-fee consulting accelerator** — cost bounded by the engagement, not by data
   volume, process count, or seats. Lead with this.
2. **Anchor against total incumbent TCO, not list price.** Celonis Year-1 TCO is $470K–$1.5M+
   *before* insight; a large SAP TSA runs $150K–500K/month. The honest accelerator comparison is "a
   fraction of that, findings in days."
3. **Package by engagement type, not feature:**
   - **Discovery Sprint** — single domain, the 6-report suite, time-boxed (2–4 weeks). The land motion.
   - **Carve-out / TSA-Exit Rationalisation** — flagship, premium, multi-domain, deadline-anchored.
     Priced on retired risk (unowned controls falling through TSA gaps), not data volume.
   - **Discovery Refresh** — repeat/retainer at a step-down rate (turns P3 monitoring-lite into
     recurring revenue without becoming SaaS).
4. **Price on retired risk / avoided cost, not tokens** — quantify "contradictions found, unowned
   processes surfaced, control gaps closed before they bite" in the deliverable so the fee is
   self-justifying.
5. **Sell *through* consulting firms, not against them.** Offer firm-level licensing so partners
   deliver the accelerator under their brand and accountability — this co-opts our strongest
   competitor (the Big-4) into distribution and sidesteps their procurement/trust advantage.

---

## 7. Top risks to our position & mitigations

1. **Incumbents bolt LLMs onto their platforms** (Celonis MCP server, Salesforce/Apromore→Agentforce,
   Glean autonomous agents, ABBYY's document heritage is closest). **Mitigation:** race on what they
   can't easily copy — the grounding gate + consulting delivery + carve-out specificity, not the
   LLM. Their data-model/repository anchors and SaaS GTM make a fast, zero-config, doc-first,
   fixed-fee accelerator awkward for them. Partner-and-coexist publicly.
2. **"Just build it on our own agent stack" (DIY).** **Mitigation:** make the moat the grounding
   gate + provenance + 6-report productisation + zero-config robustness on messy real docs — the
   18-month-hard part, not the prompt.
3. **Trust / hallucination skepticism in audit-adjacent settings.** **Mitigation:** lead every
   deliverable with provenance and the grounding-gate guarantee; human-SME-in-the-loop is a feature.
   Consider third-party validation of the gate. (The Deloitte refund is our best sales anecdote for
   why grounding matters.)
4. **Big-4 own deal access and the client room.** **Mitigation:** channel strategy — be the
   accelerator *inside* their engagements, not a direct competitor for the C-suite relationship.
5. **Narrow wedge limits TAM; carve-out events are episodic.** **Mitigation:** wedge to land, then
   expand to general domain discovery + the Discovery Refresh retainer; the accelerator runs on any
   domain's docs zero-config, so horizontal expansion is a GTM motion, not a rebuild.
6. **Positioning confusion — buyers slot us as "a cheaper Celonis"** and judge us on rigor we lack.
   **Mitigation:** discipline the message to the complementary line ("they quantify the log; we find
   what isn't in it"); never sell on structured-throughput rigor.
7. **APM incumbents add GenAI doc-ingestion to populate their repositories** (LeanIX/Ardoq/Bizzdesign
   are moving here). **Mitigation:** our edge is *contradiction + unowned-process discovery and a
   grounded deliverable*, not repository population; position as the feeder that finds what their
   repository can't, and emphasise the audit-grade grounding GenAI copilots lack.

---

### Key evidence anchors (full URLs in the per-category dossiers)
- Process mining can't use unstructured data: arXiv 2401.13677
- Mining blind to off-system/unowned work + 80% ETL: skan.ai (Gartner 2020 Market Guide)
- Mining cost/opacity/TTV: G2 / PeerSpot / Gartner Peer Insights (Celonis, Signavio); processmaker.com
- APM survey-fatigue / stale-repository failure mode: Gartner EA effectiveness (~25%)
- LLM-knowledge hallucination in production (Copilot); per-seat pricing (Glean, Hebbia)
- Consulting fabrication risk: Deloitte Australia ~AU$439K report refund
- Carve-out economics: EY/E78 (~70% plan a carve-out by 2026); PwC (1,500+ TSA decisions); SNP/Archon ($150K–500K/mo TSA); reference deals incl. Sanofi/Opella ~€16B
