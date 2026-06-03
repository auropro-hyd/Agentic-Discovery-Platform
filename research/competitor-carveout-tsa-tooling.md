# Competitor Dossier — carveout-tsa-tooling

_Market research generated 2026-06-02 via a multi-agent web-research workflow (11 agents, deep web search + analyst/review mining). Cited throughout. This is a standing reference — read it instead of re-searching._


## Category summary

The carve-out / TSA-exit market is dominated by the Big Four advisory practices (PwC, Deloitte, EY, KPMG) plus specialist boutiques (West Monroe, FTI, Liberty Advisor, Infosys Consulting) and SAP/data-migration product vendors (SNP). The market is large and structurally growing: roughly 70% of large companies plan at least one carve-out by 2026 (EY/E78), and the reference mega-deals — Sanofi/Opella (~EUR 16B, closed Apr 2025, CD&R), Kenvue/J&J (2023, one of the largest consumer-health separations ever), Organon/Merck (2021), Haleon/GSK (2022), Sandoz/Novartis (2023) — each carry multi-year, multi-hundred-million-dollar IT separation programs. IT is repeatedly cited as the most entangled, most expensive, longest-lead workstream. The economics are the pain: large SAP-environment TSAs cost roughly USD 150K-500K/month (Archon/SNP benchmark), a typical TSA exit involves 1,500+ interdependent design decisions (PwC), and TSAs typically run 6-24 months. This is why early TSA-exit acceleration is the value lever everyone sells.

CRITICAL STRUCTURAL FINDING — the tooling splits into four non-overlapping buckets, and NONE of them does what our product does: (1) Consulting PMO/transaction platforms (EY Capital Edge, Deloitte DigitalMIX, PwC Exit Readiness Accelerator, KPMG Carve AI) — these TRACK and ORCHESTRATE a separation (workstreams, TSA milestones, synergy/cost tracking) and, in KPMG's case, consolidate carve-out FINANCIALS; they do not autonomously read an enterprise's heterogeneous process docs and discover contradictions/control gaps. (2) Application discovery / dependency-mapping CMDB tools (Device42, ServiceNow APM/ITOM, SAP LeanIX, Flexera, Faddom) — these map the technical estate (servers, apps, network dependencies) via agents/scanners, but they discover INFRASTRUCTURE topology, not process-vs-data contradictions, and they require live-system access not documents. (3) SAP data-migration engines (SNP CrystalBridge/Kyano) — these analyse and selectively extract/migrate SAP data for the physical carve-out; deep but SAP-bound and execution-stage, not discovery/diagnosis. (4) Process mining (Celonis, KYP.ai) — closest analytically; mines event logs to reveal as-is process, but requires structured event-log extraction per source system, is process-flow-centric not finding-centric, and does not reason over unstructured SOPs/policies/RACIs. THE GAP: there is no productized tool that ingests an enterprise's messy business documents (SOPs, policies, RACIs, CSV exports, working notes) for a domain with zero config and AUTONOMOUSLY surfaces contradictions between documented process and actual system data, undocumented/unowned processes, and control gaps — then writes a client-grade report suite. The Big Four do exactly this finding-work, but manually with armies of consultants; their "tools" are project-management scaffolding, not the discovery engine itself. Our product productizes the consultant's reasoning layer, which is currently 100% labour.

## Vendors

### PwC (Deals — Separation & Divestitures; TSA Exit; Exit Readiness Accelerator / DDV)

**What it does:** Full-service carve-out and TSA-exit advisory practice. Productized assets include the PwC Exit Readiness Accelerator and DDV Exit Readiness Accelerator — a workshop-driven tool to identify, analyse and resolve operational 'entanglements' across entities, functions and processes, and to set high-level TSA strategy (logical vs physical separation). PwC reports running ~650 divestitures annually and claims ~30% speed-to-market improvement.

**Approach:** Consulting-led. Frames separation around entanglement dimensions (entities/functions/processes), establishes a TSA-exit blueprint early, drives ~1,500+ interdependent design decisions to closure. The accelerator is a structured one-day workshop + framework, not an autonomous engine — humans do the discovery and analysis.

**Inputs required:** Workshop participation by client decision-makers; client-provided process, org, system and contract documentation; SME interviews. Inputs are gathered and interpreted by the consulting team.

**Pricing:** Not published. Engagement-based consulting fees scaled to deal size; typically a percentage of a multi-year separation program budget (separation programs on mega-deals run into tens-to-hundreds of millions).

**Differentiator:** Brand, scale (~650 divestitures/yr), and a quantified TSA-exit value thesis (exit in 6-12 months vs typical 12-24; 1,500+ design decisions). Deep cross-functional separation muscle.

**Sources:**
- https://www.pwc.com/us/en/services/consulting/deals/library/tsa-exit.html
- https://www.pwc.de/en/deals/separation-and-integration/ddv-exit-readiness-accelerator.html
- https://www.pwc.com/us/en/services/consulting/deals/divestitures-separations.html
- https://www.pwc.de/en/deals/a-strategic-approach-to-carve-outs.html

### Deloitte (M&A / Divestiture & Separation; DigitalMIX; Divestiture Readiness SelfAssess)

**What it does:** Leading divestiture/separation practice (claims involvement in many of the world's top-10 divestitures). Productized accelerator DigitalMIX is a preconfigured SaaS-based delivery platform used to stand up new-company technology programs during separation (now integrating Salesforce Einstein AI). Also offers Divestiture Readiness SelfAssess and TSA design/management frameworks ('Fast Break', 'The Art of Speed').

**Approach:** Consulting-led; bias toward avoiding IT TSAs entirely by separating apps/infrastructure by close where feasible. DigitalMIX is delivery/program scaffolding (technology stand-up, ops transition) rather than an autonomous document-discovery diagnostic.

**Inputs required:** Client system landscape, application/infrastructure entanglement data, data-access permissions, target operating model; gathered by consultants. SelfAssess is a questionnaire-style readiness tool.

**Pricing:** Not published. Consulting fees scaled to deal size; DigitalMIX delivered as part of an engagement, not sold as a standalone seat.

**Differentiator:** Depth on the hardest separations and a packaged tech-stand-up accelerator (DigitalMIX) that compresses Day-1 technology delivery; emerging GenAI via Salesforce Einstein.

**Sources:**
- https://www.deloitte.com/ch/en/services/consulting-financial/research/it-transitional-service-agreements.html
- https://www.deloitte.com/ch/en/services/consulting-financial/research/the-art-of-speed.html
- https://www.deloittedigital.com/us/en/accelerators/digitalmix.html
- https://www.deloittedigital.com/us/en/insights/perspective/digitalmix-press-release.html
- https://www2.deloitte.com/content/dam/Deloitte/us/Documents/mergers-acqisitions/us-ma-consulting-fastbreak-080908.pdf

### EY (Strategy & Transactions; EY Capital Edge platform)

**What it does:** Carve-out sale and operational-separation advisory, fronted by EY Capital Edge — an AI-powered M&A transaction & transformation platform spanning M&A, spins and carve-outs. Capital Edge provides connected workstream/PMO management, a TSA module (create/approve/execute TSAs, real-time TSA enablement progress), auto-generation of Day-1/end-state operating models from sector templates, and synergy/cost/value-capture tracking against benchmarks. Curates EY-Parthenon leading practices and M&A accelerators.

**Approach:** Software-assisted consulting. Capital Edge is the productized layer — but it is a transaction execution / PMO / TSA-tracking platform, not an autonomous discovery engine. EY states IT is the most entangled, longest-lead, most expensive workstream and pushes early separation to shrink TSA scope.

**Inputs required:** Workstream/project data, TSA schedules, cost baselines, operating-model inputs — entered/uploaded into the platform by the engagement team. No documented capability to autonomously ingest raw SOPs/CSVs and discover contradictions.

**Pricing:** Not published; request-a-demo, delivered within EY engagements. Platform access bundled with advisory fees.

**Differentiator:** The most mature, branded productized platform among the Big Four — genuine end-to-end M&A/separation PMO + TSA workflow with a leading-practice content library and AI-assisted operating-model generation.

**Sources:**
- https://www.ey.com/en_us/services/strategy/ey-capital-edge-mergers-acquisitions-transaction-platform
- https://www.ey.com/en_us/insights/divestitures/carve-out-sale-road-map-sign-to-close
- https://www.ey.com/en_us/insights/tech-sector/enterprise-software-carve-out-strategies
- https://www.ey.com/en_uk/services/strategy-transactions/operational-separation

### KPMG (Deal Advisory — Integration & Separation; KPMG Carve AI)

**What it does:** Carve-out/separation advisory plus the productized KPMG Carve AI — an integrated, AI-supported platform that consolidates heterogeneous data sources into a single source of truth to produce auditable carve-out FINANCIAL statements (P&L, balance sheet, segmentation by region/product/function, working capital). Separately, KPMG methodology builds a 5-dimension inventory + dependency matrix to find Day-1 TSA 'hotspots'.

**Approach:** KPMG Carve AI is the most genuinely 'AI/data' product among the Big Four — but it is scoped to FINANCIAL carve-out reporting (the 'data cube'), NOT IT application discovery or process-vs-data contradiction finding. The IT separation work (dependency matrix, TSA hotspots) is still consultant-driven methodology.

**Inputs required:** ERP extracts and Excel/heterogeneous financial data sources for Carve AI; for IT separation, client-provided application/dependency data assembled by consultants.

**Pricing:** Not published. Delivered within Deal Advisory engagements.

**Differentiator:** Carve AI's auditable single-source-of-truth for carve-out financials with automated dashboards/Excel outputs — strongest productized data engine in the category, but financials-only.

**Sources:**
- https://kpmg.com/de/en/services/advisory/deal-advisory/kpmg-carve-ai.html
- https://assets.kpmg.com/content/dam/kpmgsites/xx/pdf/2026/03/carve-out-strategy.pdf.coredownload.inline.pdf
- https://kpmg.com/ch/en/insights/deals/it-separation-challenges-mergers-acquistitions.html
- https://kpmg.com/kpmg-us/content/dam/kpmg/pdf/2023/accelerated-tsa-exits.pdf

### SNP (Kyano CrystalBridge — SAP carve-out / data migration platform)

**What it does:** Software platform that analyses SAP system landscapes and selectively extracts, transforms and migrates data to execute SAP-to-SAP carve-outs and divestitures with minimal downtime, plus archive/decommissioning support to exit SAP TSAs.

**Approach:** Productized, automation-heavy engine for the physical/data layer of an SAP carve-out (discovery of SAP data scope -> extraction -> validation -> migration -> decommission). Deep but SAP-bound and execution-stage, not a domain-agnostic diagnostic/discovery layer.

**Inputs required:** Direct access to source SAP systems and landscape metadata; SAP-centric. Does not reason over unstructured SOPs/policies/RACIs.

**Pricing:** Software licence + services model (not publicly listed). Positioned against TSA run-rate (large SAP TSAs benchmarked at ~USD 150K-500K/month), so ROI is faster SAP decommissioning.

**Differentiator:** Best-in-class automated SAP data transformation/migration; the technical workhorse partners and Big Four pull in for the SAP execution itself.

**Sources:**
- https://www.snpgroup.com/en/platform/kyano-move/products/kyano-crystalbridge/
- https://www.snpgroup.com/en-us/crystalbridge-carve-out
- https://insidesap.com/automated-sap-carve-outs-with-snps-data-transformation-platform-crystalbridge/
- https://www.archondatastore.com/blog/sap-carve-out-strategy/

### IT discovery / dependency-mapping & APM tools (Device42, ServiceNow ITOM/APM, SAP LeanIX, Flexera, Faddom)

**What it does:** Automatically discover the IT estate and map application-to-infrastructure dependencies (Device42, Faddom, ServiceNow ITOM), or manage the application portfolio for rationalisation/assessment (SAP LeanIX, ServiceNow APM). Used in data-centre exits, consolidations and increasingly carve-outs to understand what must be separated.

**Approach:** Agent/agentless scanners and CMDB modeling for technical topology (Device42/Faddom/ServiceNow); business-context APM modeling for rationalisation (LeanIX). They reveal WHAT exists and how it connects, supporting TSA-scope and separation planning.

**Inputs required:** Live system/network access for discovery scanners; for LeanIX/APM, manually or integration-fed application inventory with business context. Not document-ingesting; not contradiction-finding.

**Pricing:** Per-asset / per-application / subscription SaaS licensing (e.g., Device42 priced per device/resource; LeanIX per-application subscription). Generally enterprise SaaS, six figures+ for large estates.

**Differentiator:** Authoritative technical dependency truth (Device42/ServiceNow) or APM rationalisation lens (LeanIX) — strong on the infrastructure/portfolio layer that our product does NOT attempt.

**Sources:**
- https://virima.com/blog/top-application-dependency-mapping-tools
- https://www.device42.com/application-mapping-dependency-flow/
- https://www.leanix.net/en/use-cases/application-portfolio-assessment
- https://www.leanix.net/en/products/application-portfolio-management

### Process mining (Celonis, KYP.ai) — closest analytical adjacent

**What it does:** Mine event logs from source systems to reconstruct the actual as-is process, expose variants/bottlenecks/non-conformance, and quantify process behaviour. Applicable to understanding processes before separation and to TSA-scope/decommissioning decisions.

**Approach:** Data-driven discovery of actual process flow from structured event logs; conformance checking compares observed vs a reference model. Process-flow-centric, requires per-system log extraction, and does not reason over unstructured policy/SOP/RACI documents.

**Inputs required:** Structured event logs extracted/connectored per source system (case ID, activity, timestamp). Heavy data-engineering setup; not zero-config; not document-native.

**Pricing:** Enterprise SaaS subscription (Celonis), typically six-to-seven figures for large deployments; KYP.ai subscription.

**Differentiator:** Quantitative ground-truth on real process execution from event logs — the strongest existing 'what actually happens vs what's documented' signal, but bound to structured logs and reference models rather than autonomous reasoning over messy docs.

**Sources:**
- https://www.celonis.com/insights/topics/what-is-process-mining
- https://www.celonis.com/blog/what-are-5-working-examples-of-process-mining
- https://kyp.ai/automated-process-discovery-tools/

## Where they beat us (be honest)

1) PHYSICAL EXECUTION & TECHNICAL TRUTH: Device42/ServiceNow/Faddom give authoritative, auto-discovered infrastructure dependency maps and SNP CrystalBridge actually performs the SAP data extraction/migration/decommission. Our product reasons over docs+CSVs; it does not scan live networks or move data, so for 'what servers/apps connect to what' and 'execute the separation' the incumbents win outright. 2) BRAND, TRUST & DEAL ACCESS: PwC/Deloitte/EY/KPMG own the C-suite/board and PE relationships that originate carve-outs; they are the default buyer for a EUR 16B Opella-class separation. They also carry audit-grade credibility (KPMG Carve AI produces auditable financials) — a 'consistent-not-fabricated' claim from a startup must overcome that incumbency. 3) END-TO-END PROGRAM SCAFFOLDING: EY Capital Edge and Deloitte DigitalMIX manage the entire multi-year separation — TSA workflow, milestones, synergy/cost tracking, Day-1 operating-model generation, technology stand-up. Our product is a discovery/diagnosis accelerator, not a program-execution platform, so for ongoing TSA-exit orchestration they cover more of the lifecycle. 4) PROCESS MINING RIGOUR: Celonis quantifies real process execution from event logs with conformance metrics — a harder, system-of-record-grade evidence base than document reasoning for the subset of processes that have clean logs. 5) FINANCIALS: KPMG Carve AI directly produces the auditable carve-out P&L/balance sheet — a regulated deliverable our product does not target. 6) PROVEN SCALE/REFERENCES: Incumbents have delivered the marquee deals (Kenvue, Organon, Haleon, Sandoz, Opella) at scale; we have the cold-start credibility problem.

## Where we beat them

1) AUTONOMOUS FINDING-DISCOVERY IS THE WHITE SPACE: Every incumbent 'tool' is either a PMO/TSA tracker (EY Capital Edge, Deloitte DigitalMIX, PwC accelerator), a financials engine (KPMG Carve AI), a CMDB/dependency mapper (Device42/ServiceNow), an SAP data mover (SNP), or process mining (Celonis). NONE autonomously ingests heterogeneous business documents (SOPs, policies, RACIs, CSV exports, working notes) and computes findings — contradictions between documented process and actual system data, undocumented/unowned processes, control gaps. The Big Four do this finding-work today entirely with manual SME labour. We productize the consultant's reasoning layer, which is the most expensive, slowest part of the engagement. 2) ZERO-CONFIG, DOMAIN-AGNOSTIC, DOCUMENT-NATIVE: Process mining and discovery tools need per-system connectors/event-log extraction or live-network access — weeks of data engineering. We run on whatever messy docs+CSVs the client already has, on ANY domain (O2C, P2P) with zero config and no source-system integration. This is decisive in carve-outs where the seller restricts data-access and live-system connectivity during the deal. 3) CONTRADICTION/CONTROL-GAP DETECTION across docs-vs-data is genuinely novel: incumbents map dependencies or mine flows; we surface 'the SOP says X owns this control but the system export shows it never runs' — exactly the carve-out risk (undocumented/unowned processes, stranded controls) the Big Four bill armies to find. 4) GROUNDED, NON-FABRICATED OUTPUT WITH PROVENANCE: every number traces to the data via a grounding gate, with confidence/provenance per finding and human-SME-in-the-loop — directly answering the #1 objection to GenAI in regulated deal work, and matching KPMG's auditability framing without the financials-only narrowness. 5) CLIENT-READY 6-REPORT SUITE WITH NO TOOL JARGON: we output Current State, Pain Points, Transformation Recommendation (value-feasibility matrix), AI Opportunity Portfolio (before/after), Roadmap, Supporting Artefacts — the actual consulting deliverable, not a dashboard the consultant must still write a deck from. 6) ECONOMICS / DELIVERY MODEL FIT: positioned as a consulting accelerator (not a SaaS seat), we compress the discovery phase that currently consumes the most hours, letting a firm bid faster/cheaper or win where TSA run-rate (USD 150K-500K/month) makes speed the whole value case. We are a force-multiplier the incumbents could license or that a challenger boutique can use to punch above its weight.

## Documented weaknesses / complaints (and how we address them)

### Celonis process mining requires per-source-system integration to extract structured event logs, and many business applications have no event log available — so the upfront data-engineering plumbing is heavy and many processes simply can't be mined.

_Evidence:_ 'Celonis process mining requires integrations to every different source system to extract event logs, and there are many business applications that don't have event logs available, leading to significant data integration hassle.' Academic literature reinforces this: 'process mining requires data to be organized in a scheme that enables retrieval of information as an event log... unstructured data does not fulfill the requirements for process mining.'

_Source:_ G2 Celonis reviews (g2.com/products/celonis/reviews); arXiv 'Process Mining for Unstructured Data: Challenges and Research Directions' (arxiv.org/html/2401.13677v1)

**How we address it:** Our platform requires NO event-log extraction and no per-system connectors. It ingests whatever the client already has — SOPs, policies, RACIs, raw CSV/system exports, working notes — with zero config, and computes over any CSV using generic tools (describe/group_by/join_diff/filter_count). It is finding-centric, not flow-centric, so it works even where no event log exists.

### Celonis is the most expensive tool in the market, with multi-year (typically 3-year) contracts, opaque/shifting licensing, and indirect implementation costs — pricing it out of many use cases and making it a poor fit for a one-off discovery engagement.

_Evidence:_ 'Celonis is the most expensive solution in the market'; 'The cost would be a concern for a certain category of customers.' Enterprise pricing 'starts at $15,000 but can exceed $200,000'; reviewers cite 'long contract length (typically 3 years)' and 'constant changes in the licensing structure.'

_Source:_ PeerSpot Celonis reviews (peerspot.com/products/celonis-reviews); G2 Celonis reviews (g2.com/products/celonis/reviews)

**How we address it:** We are delivered as a consulting accelerator for a discovery engagement, not a per-seat SaaS subscription with multi-year lock-in. There is no platform license to amortize or annual renewal — value is realized in a single bounded discovery, which fits the episodic, deal-driven nature of carve-out/TSA work.

### Celonis implementation is technically heavy and IT/data-engineer-dependent, with a proprietary query language (PQL) that locks out business users — undercutting its 'results in weeks' marketing and creating a steep learning curve.

_Evidence:_ 'Initial setup and modelling feel heavy with too much dependency on data engineers'; PQL 'is code that only Celonis uses, so there is little help available on the internet or through AI beyond Celonis documentation,' creating a barrier for non-technical users. Setup 'varies considerably — from days to months — depending on data quality and technical resources.'

_Source:_ Gartner Peer Insights / G2 Celonis reviews (gartner.com/reviews/product/celonis-process-intelligence-platform)

**How we address it:** The reasoning is fully autonomous — the agent calls the generic tools itself; there is no proprietary query language for anyone to learn and no data-engineering setup phase. Consultants and SMEs interact with plain findings and a client-grade report suite, not a PQL console. Human-SME-in-the-loop validation replaces the IT plumbing requirement.

### Process mining (Celonis and peers) fundamentally cannot reason over unstructured business documents (SOPs, policies, RACIs, contracts, notes); textual/semantic information must be pre-extracted before any mining can occur.

_Evidence:_ 'When dealing with unstructured sources... process mining techniques cannot be applied directly, making it necessary to generate structured event logs'; 'relevant information is often captured as unstructured, textual data... the information cannot be exploited by process mining techniques without processing individual attribute values to extract the semantic information.'

_Source:_ arXiv 'Process Mining for Unstructured Data' (arxiv.org/html/2401.13677v1); ACM 'Unstructured Data in Process Mining: A Systematic Literature Review' (dl.acm.org/doi/pdf/10.1145/3727148)

**How we address it:** Reading and reasoning over heterogeneous unstructured documents is the core capability of our LLM-agent. It discovers contradictions between what policies/SOPs DOCUMENT and what the CSV/system data actually SHOWS, and surfaces undocumented or unowned processes — precisely the semantic, cross-document work process mining cannot do.

### ServiceNow APM / dependency tools depend on the CMDB and Discovery, which are notoriously inaccurate, stale, and incomplete — a 'garbage in, garbage out' source of false confidence requiring perpetual manual upkeep.

_Evidence:_ 'Most CMDBs' accuracy hovers around 60%'; 'when records are stale... it becomes something worse than no system of record at all: a source of false confidence.' 'ServiceNow does not keep your CMDB accurate. It stores what you feed it.' Per Gartner, 'only 25% of enterprises receive meaningful value from their CMDBs.' APM data also relies on 'scheduled data certifications' by app owners.

_Source:_ Oomnitza (oomnitza.com/blog/servicenow-cmdb-data-accuracy-boost-roi); ServiceNow Community 'Why CMDB Fails'; G2 ServiceNow APM reviews

**How we address it:** We don't depend on a maintained system-of-record. We compute over point-in-time exports the client provides, and every finding carries confidence and provenance tracing back to the underlying data, verified by a grounding gate. There is no perpetual data-hygiene burden — and detecting where documented reality diverges from actual data is exactly the divergence a stale CMDB hides.

### Application/dependency-mapping tools (Device42, ServiceNow ITOM, Faddom et al.) require agents or network access to LIVE, running systems and cannot capture decommissioned systems, document-only processes, or process/ownership context — they map infrastructure topology, not business process.

_Evidence:_ 'Organizations need to place agents on every relevant... server... potentially increasing costs significantly'; agent-based mapping 'inherently requires the systems to be running and accessible on the network' and 'cannot effectively map decommissioned systems or document-only processes.' Device42 reviewers note 'limitations in real-time application dependency mapping' and that 'basic dependency maps are not enough... you need ITSM context.'

_Source:_ Faddom 'Application Dependency Mapping' (faddom.com/application-dependency-mapping); Device42 reviews via SpotSaaS / AWS Marketplace / Gartner Peer Insights

**How we address it:** We need no agents, no scanners, and no live-system access. We work from documents and exports, so we can analyze processes regardless of whether the system is live, being decommissioned, or moving under a TSA. And we discover process-vs-data contradictions, control gaps, and unowned processes — business-process findings, not server topology.

### Enterprise AI/analytics outputs are widely distrusted as 'black boxes' with no explainability or provenance — executives, compliance, and audit won't act on or sign off on recommendations they can't trace.

_Evidence:_ '76% of executives struggle to trust AI systems because they cannot explain the outputs' (Accenture); 'only 17% of organizations are proactively addressing explainability, despite 40% identifying it as one of the most significant risks'; '67% of enterprises failed AI governance audits in 2022 due to lack of transparency'; 'Compliance teams won't approve models they can't audit.'

_Source:_ EWSolutions 'The White Box Model in AI' (ewsolutions.com/the-white-box-model-in-ai); Raconteur 'Beyond the Black Box'; Censinet 'Explainable AI Imperative'

**How we address it:** Every finding is consistent-not-fabricated: each number traces to the source data and is verified by a grounding gate before it reaches the client, and findings carry explicit confidence and provenance. This is the auditable, white-box answer to the black-box trust problem — designed so a consultant or audit committee can stand behind every figure.

### SAP LeanIX and similar EA repositories suffer from heavy manual data entry, stale fact sheets, and integration limits — value collapses without continuous human upkeep (garbage-in/garbage-out), and the tool itself is complex.

_Evidence:_ Users report 'struggling with unclear content and excessive manual work'; LeanIX added an 'AI inventory builder to reduce manual data entry'; fact sheets expire on a renewal interval (30 days–1 year) or the 'Quality Seal breaks.' 'Users find SAP LeanIX very complex'; 'integration issues hinder automation... existing options are limited.'

_Source:_ G2 SAP LeanIX reviews (g2.com/products/sap-leanix/reviews); LeanIX Community fact-sheet quality guide; TrustRadius SAP LeanIX reviews

**How we address it:** There is no repository to populate or keep fresh. We ingest the client's existing documents and data as-is and autonomously produce findings — no manual fact-sheet entry, no decay timers, no per-source connectors to maintain. The output is a one-time client-grade diagnostic, not a living model the client must staff to keep accurate.

### SNP CrystalBridge/Kyano is SAP-bound and execution-stage: it analyzes and selectively migrates SAP data for the physical carve-out, but does no cross-domain discovery/diagnosis over non-SAP, document, or business-process content.

_Evidence:_ 'Kyano CrystalBridge is a... data migration solution designed to streamline SAP-to-SAP transitions'; carve-out support is 'selective migration' and 'clone and delete' of SAP objects (company codes, controlling areas) — i.e. the physical move, not pre-deal process diagnosis.

_Source:_ SNP Group product pages (snpgroup.com/en/platform/kyano-move/products/kyano-crystalbridge; .../use-cases/s4hana-migration)

**How we address it:** We sit upstream of migration, at the discovery/diagnosis stage, and are system-agnostic: we reason over any domain's documents and any CSV export, SAP or not. We find the contradictions, control gaps, and unowned processes that should shape WHAT to separate and rationalize — the analysis SNP's execution engine assumes has already been done.

### Big Four carve-out/TSA-exit 'platforms' (EY Capital Edge, Deloitte DigitalMIX, PwC Exit Readiness Accelerator, KPMG Carve AI) are PMO/orchestration scaffolding that TRACK milestones, workstreams, synergies and financials — the actual discovery of findings is still manual, labour-intensive consulting against ~1,500+ interdependent decisions.

_Evidence:_ EY Capital Edge 'combines traditional project management office (PMO) functionality... across more than 30 purpose-built apps' to 'connect multiple workstreams.' PwC: 'a typical TSA exit requires more than 1,500 design decisions, and most are interdependent,' driving 'timeline and budget overruns'; IT TSAs commonly run '12 to 18 months.' Carve-out post-mortems cite IT as 'one of the most underestimated and complex aspects.'

_Source:_ EY Capital Edge (ey.com/.../ey-capital-edge-mergers-acquisitions-transaction-platform); PwC 'Expediting TSA exits' (pwc.com/.../tsa-exit.html); Alvarez & Marsal / Forvis Mazars carve-out pitfall analyses

**How we address it:** We productize the consultant's reasoning layer that these PMO tools deliberately leave to humans. Instead of tracking 1,500 decisions in a dashboard, our agent autonomously surfaces the underlying findings — contradictions, control gaps, undocumented/unowned processes — from the messy docs, accelerating the most labour-intensive, longest-lead part of the engagement while remaining human-SME-in-the-loop.

### None of the four existing tooling buckets is carve-out/TSA-specific at the discovery layer, and the cost/time pain of carve-outs is concentrated in exactly the manual diagnostic work no tool automates — large SAP TSAs run ~$150K–$500K/month over 6–24 months.

_Evidence:_ Market analysis: 'TSAs are expensive... bundled monthly cost... unreasonably expensive and led to painful renegotiations'; buyers face 'overruns in their budgets for one-time costs and EBITDA' from involving 'too many vendors'; 'hidden licensing and contract separation costs, unsupported legacy systems and uncosted implementation timelines frequently lead to budget and timeline overruns.'

_Source:_ PwC 'Expediting TSA exits' (pwc.com/.../tsa-exit.html); FTI 'Hidden Costs in Carve-Outs' (fticonsulting.com); Forvis Mazars 'Common Carve-Out Transaction Pitfalls'

**How we address it:** We are positioned specifically for consulting-led, post-carve-out / TSA-exit application and process rationalisation. By autonomously diagnosing contradictions, gaps, and unowned/undocumented processes early — with traceable numbers and a 6-report client suite (Current State, Pain Points, Transformation Recommendation, AI Opportunity Portfolio, Roadmap, Supporting Artefacts) — we compress the most expensive, longest-lead diagnostic phase that drives TSA duration and monthly burn.
