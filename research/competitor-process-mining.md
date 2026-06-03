# Competitor Dossier — Process Mining

_Market research generated 2026-06-02 via a multi-agent web-research workflow (11 agents, deep web search + analyst/review mining). Cited throughout. This is a standing reference — read it instead of re-searching._


## Category summary

Process mining is a mature, well-funded category (Celonis alone is a ~$13B+ company; the space now includes SAP, Microsoft, UiPath, and—as of Nov 2025—Salesforce via its Apromore acquisition) that reconstructs how processes ACTUALLY run by ingesting structured EVENT LOGS extracted from transactional systems (SAP, Oracle, ServiceNow, Salesforce, etc.). The universal, non-negotiable input contract is three columns per event: Case ID + Activity + Timestamp; vendors layer extra attributes for richer slicing. From these logs the tools algorithmically derive a process graph/digital twin (UiPath uses a Probabilistic Inductive Miner; others use directly-follows / inductive miners), then do conformance checking, variant/bottleneck analysis, root-cause, simulation, and increasingly feed AI agents for automated execution. THIS IS THE CATEGORY'S DEFINING STRENGTH AND ITS DEFINING LIMIT. Where the data is high-volume, structured, and timestamped (O2C, P2P, AP, service ticketing), these tools are statistically rigorous, real-time, and deeply tooled — far beyond what a discovery accelerator does. But the category structurally CANNOT do three things our product is built for: (1) it cannot derive process from UNSTRUCTURED documents (SOPs, policies, RACIs, working notes) — academic literature (arXiv 2401.13677) confirms 'a direct application of process mining is not possible' on data lacking case ID/activity/timestamp, and documents have none of these natively; (2) it can only show processes that EXIST in a system's logs — it is blind to undocumented, manual, off-system, or unowned processes (a control gap that lives in a spreadsheet + an email is invisible); (3) it requires significant ETL/data-extraction effort and per-process licensing, making time-to-first-insight long and cost high. The 2025-2026 vendor narrative has pivoted hard to 'feeding context to AI agents' (Celonis MCP server + Orchestration Engine; Salesforce/Apromore for Agentforce; Microsoft into Power Platform; SAP into business transformation), but the underlying data dependency is unchanged: no event log, no process mining. Pricing is consumption/volume-based and opaque-to-high (Celonis $150K entry to $5M+ enterprise; Microsoft a relatively cheap $5,000/tenant/mo add-on; ABBYY from ~$1,000/mo; Signavio modular per-user + per-record). These are SaaS platforms sold on seats/capacity, not consulting accelerators — the inverse of our delivery model.

## Vendors

### Celonis

**What it does:** Market-leading process intelligence platform. Extracts event logs from ERP/CRM systems and reconstructs end-to-end process 'digital twins', then does variant analysis, conformance checking, bottleneck/root-cause analysis, and (increasingly) automated action. 2025 push: Object-Centric Process Mining (OCPM), the Process Intelligence Graph, an Orchestration Engine for coordinating AI agents, and 'the world's first MCP server for process intelligence' to feed agents operational context.

**Approach:** Algorithmic discovery over structured event logs. Object-centric model (events linked to multiple business objects) rather than single-case-ID, plus a Process Intelligence Graph that now ingests structured + some semi/unstructured sources via Celonis Data Core (zero-copy integrations with Databricks/Microsoft). Math is done in-engine; output is dashboards/graphs.

**Inputs required:** Event logs from source systems: minimum Case ID + Activity + Timestamp per event, extracted via connectors or CSV. Heavy ETL/data-modeling step to build the data model per process. OCPM and the Graph can layer in PDFs/emails/external data but still anchor on transactional event data.

**Pricing:** Consumption-based (Analytics Processing Capacity / APC, measured in bytes), not per-seat. No public rate card — redirects to sales. Reported: ~$150K entry packages; one buyer cited $80K-95K/yr for APC-100GB + 10 users; Forrester composite scaled $1.26M (Yr1, 4 processes) to $5.25M (Yr3, ~12 processes). Each business process (O2C, P2P, AP) typically needs dedicated licensing. Year-1 TCO incl. implementation $470K-$1.5M+.

**Differentiator:** Deepest/most mature platform, real-time execution capabilities, object-centric mining, and the strongest agentic-AI ecosystem play (MCP server, Orchestration Engine). The de facto category benchmark.

**Sources:**
- https://www.celonis.com/insights/topics/how-does-process-mining-work
- https://docs.celonis.com/en/object-centric-process-mining-overview.html
- https://checkthat.ai/brands/celonis/pricing
- https://www.processexcellencenetwork.com/process-mining/news/celonis-announces-new-platform-innovations-to-power-ai-driven-composable-enterprises
- https://siliconangle.com/2025/11/05/exploring-object-centric-process-mining-celosphere/

### SAP Signavio

**What it does:** Process intelligence module within SAP's Business Process Transformation suite. Turns enterprise system data into process maps, monitors how processes actually run, does root-cause and conformance analysis, and ships ready-to-use 'accelerators' / best-practice content for common processes. Strongest fit for SAP-centric estates.

**Approach:** Event-log-based process mining tied to SAP's broader modeling stack (Process Manager for BPMN modeling, Process Governance, Journey Modeler). AI features add dashboards and automated improvement recommendations. Combines as-is mining with to-be modeling in one suite.

**Inputs required:** Event logs from SAP and other enterprise systems (Case ID + Activity + Timestamp + attributes). Benefits from SAP-native connectors. Like all peers, requires ETL into the required event-log shape.

**Pricing:** Modular, named-user + capacity based. Per published estimates: Process Manager priced per named user; Collaboration Hub per block of 10 users; Process Intelligence per ~200,000-record block. Indicative annual ranges ~£1,250-£7,750 (1 user) up to ~£125K-£775K (100 users). Separate AI units for AI features. Implementation, migration, training are extra.

**Differentiator:** Tight SAP integration + combined process-modeling AND process-mining in one suite (design and discover together), with prebuilt accelerators for SAP processes.

**Sources:**
- https://www.sap.com/products/business-transformation-management/process-mining.html
- https://www.signavio.com/products/process-intelligence/
- https://pricingnow.com/question/sap-signavio-pricing/
- https://www.gartner.com/reviews/product/sap-signavio-process-intelligence

### UiPath Process Mining

**What it does:** Process mining tightly coupled to UiPath's RPA/automation platform — discovers processes from event logs primarily to identify and prioritize automation opportunities, then hands off to UiPath bots. Supports discovered-model, directly-follows, and BPMN-import modeling modes.

**Approach:** Algorithmic discovery using a Probabilistic Inductive Miner (PIM) that auto-detects parallelism, decisions, and loops across the full event log; also offers simpler directly-follows models and can overlay data onto an imported BPMN model. Automation-led: mining feeds the RPA pipeline.

**Inputs required:** Event log table with mandatory technical fields (Process_event_ID, Event_ID, throughput/cycle times) plus business Case/Activity/Timestamp. Data loaded into the platform; consumption metered on visualized rows.

**Pricing:** Platform Units consumption model: 1 Platform Unit = 625 rows; initial load charges 1,600 Platform Units (covers ~1M rows for 12 months); minimum re-consumption equal to 1M rows at renewal. Dev + prod datasets both consume units.

**Differentiator:** Native, closed-loop integration with the UiPath automation platform — mine a process, then automate it with the same vendor. Strong 'discover-to-automate' story.

**Sources:**
- https://docs.uipath.com/process-mining/automation-cloud/latest/user-guide/unified-pricing
- https://docs.uipath.com/process-mining/automation-cloud/latest/user-guide/discover-process-model
- https://docs.uipath.com/process-mining/automation-cloud/latest/user-guide/process-mining-types

### Microsoft Power Automate Process Mining

**What it does:** Process mining + task mining capability inside Power Automate (formerly Minit / Process Advisor). Process mining discovers org-wide process inefficiencies from event logs; task mining records desktop user actions to zoom into specific tasks. Outputs feed Power Automate automation and Power BI reporting.

**Approach:** Event-log-based process discovery in the web app + a desktop app for advanced analytics; task mining via recorded desktop interactions. Reporting customization runs through Power BI. Built to drive automation opportunities within the Microsoft/Power Platform ecosystem.

**Inputs required:** Event log connected via Power Platform data flows into Dataverse (Case ID + Activity + Timestamp). Requires a Dataverse database and (for report customization) a Power BI Premium license; task mining requires Power Automate for desktop.

**Pricing:** Most affordable major option. Process Mining add-on listed ~$5,000/tenant/month for 100GB capacity; requires Power Automate Premium (per-user) as prerequisite. Premium licenses contribute 50MB each to a tenant pool up to 100GB before the add-on is needed. 90-day trial with 100MB/process.

**Differentiator:** Lowest entry cost of the majors and deep Microsoft/Power Platform + Power BI integration; bundles process AND task mining for organizations already standardized on Microsoft.

**Sources:**
- https://learn.microsoft.com/en-us/power-automate/process-advisor-overview
- https://www.microsoft.com/en-us/power-platform/products/power-automate/pricing
- https://cdn-dynmedia-1.microsoft.com/is/content/microsoftcorp/microsoft/bade/documents/products-and-services/en-us/bizapps/Power-Platform-Licensing-Guide-November-2025.pdf

### Apromore

**What it does:** Full-spectrum process intelligence platform (process mining + task mining + simulation + real-time monitoring) with academic roots and a no-code UI. Strong on process discovery, conformance checking, BPMN authoring, predictive monitoring, and simulation. Acquired by Salesforce in Nov 2025 to power Agentforce's agentic process automation.

**Approach:** Event-log-based discovery with research-grade algorithms; comparison/conformance checking; predictive process monitoring with tunable settings; what-if simulation. Offered as Community (open-source heritage, free) and subscription Enterprise editions; SaaS or on-prem.

**Inputs required:** Event logs (Case ID + Activity + Timestamp + attributes), uploaded or connected. Same structured-data dependency as peers.

**Pricing:** Capacity-based model with no per-process or per-user caps (positioned as flexible/scalable). Free Community Edition plus paid Enterprise Edition (commercial add-ons, connectors, services). Public rate card not disclosed; now part of Salesforce.

**Differentiator:** Open-source/community heritage + strong simulation and academic-grade algorithms; cheapest path to experiment. Post-acquisition, the process-intelligence layer feeding Salesforce Agentforce agents.

**Sources:**
- https://apromore.com/
- https://www.salesforceben.com/salesforce-acquires-apromore-to-boost-agentforces-process-mining-abilities/
- https://github.com/apromore
- https://www.processmining-software.com/tools/apromore/

### ABBYY Timeline

**What it does:** Cloud, AI-driven process mining platform that builds an interactive 'digital twin' of business processes. Five capabilities: process discovery, analysis, monitoring, prediction, and simulation. Differentiates on document-centric journeys, leveraging ABBYY's IDP (intelligent document processing) heritage.

**Approach:** Event-log-based mining over data extracted from enterprise systems 'without integration'; non-intrusive session-log recording; AI to extract/analyze flows. Positioned for document-heavy processes by combining its document-extraction lineage with process analysis.

**Inputs required:** Three essentials to start: unique identifier, timestamp, event name (the standard Case/Activity/Timestamp triple). Event data extracted from one or more enterprise systems; richer attributes improve depth. 'Strong data-prep discipline required.'

**Pricing:** Subscription, per-user-per-month with feature/user/capacity tiers. Paid version reportedly starts ~$1,000/month.

**Differentiator:** Document-centric angle backed by ABBYY's IDP heritage — closest of the majors to touching documents, though still anchored on structured event/timestamp data for the mining itself.

**Sources:**
- https://www.abbyy.com/timeline/
- https://www.processmining-software.com/tools/abbyy-timeline/
- https://www.gartner.com/reviews/market/process-mining-platforms/vendor/abbyy/product/abby-timeline
- https://www.softwareadvice.co.uk/software/53093/timelinepi

## Where they beat us (be honest)

1) STRUCTURED, HIGH-VOLUME PROCESS RIGOR: Where a process leaves millions of timestamped rows in an ERP (O2C, P2P, AP, service tickets), these tools deliver statistically exhaustive, quantified process graphs — every variant, every bottleneck, conformance % against a model, cycle times, rework loops — with a precision and completeness our document-and-CSV reasoning approach cannot match on raw transactional throughput. 2) REAL-TIME / CONTINUOUS MONITORING: They run live against connected systems and continuously re-mine; our platform is a point-in-time discovery accelerator, not a always-on monitor. 3) SIMULATION & PREDICTION: Apromore, ABBYY, Signavio, Celonis offer what-if simulation and predictive process monitoring — we reason and recommend, we don't simulate. 4) AUTOMATION CLOSED LOOP: UiPath (RPA), Microsoft (Power Automate), Celonis (Orchestration Engine + MCP), Salesforce/Apromore (Agentforce) can EXECUTE the fix, not just recommend it. 5) MATURITY, ECOSYSTEM & TRUST: Gartner-rated, reference-able at the largest enterprises, prebuilt connectors and accelerators for SAP/Oracle/ServiceNow, large partner ecosystems, security/compliance certifications, and proven scale. 6) CONFORMANCE AGAINST A KNOWN MODEL: If a documented to-be model exists, they precisely measure deviation case-by-case. 7) BIG-VENDOR PROCUREMENT FIT: Backed by Microsoft/SAP/Salesforce/Celonis — easy to buy on existing enterprise agreements.

## Where we beat them

1) NO EVENT LOG REQUIRED — WE READ THE DOCUMENTS THEY CAN'T: Our core input is the heterogeneous, UNSTRUCTURED corpus (SOPs, policies, RACIs, working notes) plus system CSVs. Academic literature (arXiv 2401.13677) confirms process mining 'cannot be directly applied' to data lacking Case ID/Activity/Timestamp — documents have none of these. We turn the exact artifacts process mining discards into findings. 2) DISCOVERS THE INVISIBLE: Process mining can only show what already exists in a system's log; it is structurally BLIND to undocumented, manual, off-system, and UNOWNED processes and to control gaps that live across a policy + a spreadsheet + an email. Missing-system / missing-process discovery is precisely our differentiator and their structural blind spot. 3) CONTRADICTION DETECTION (DOC vs DATA): We specifically compute the gap between what the SOP/policy SAYS and what the system data SHOWS — a cross-modal reasoning task process mining (single-modality, structured-only) cannot perform. 4) ZERO-CONFIG, ANY DOMAIN, FAST TIME-TO-VALUE: Process mining requires a heavy ETL/data-modeling project and per-process licensing before first insight; we run on any domain's docs with zero config and produce a 6-report client suite without building a data model per process. 5) AUTONOMOUS REASONING, NOT JUST MAPS: They output process graphs requiring an analyst to interpret; we autonomously produce client-ready narrative findings (Current State, Pain Points, Transformation Recommendation w/ value-feasibility matrix, AI Opportunity Portfolio with before/after, Roadmap, Artefacts) with confidence/provenance and a grounding gate — consistent-not-fabricated, no tool jargon. 6) DELIVERY MODEL FIT: We are a consulting accelerator (especially for post-carve-out / TSA-exit app & process rationalisation), not a SaaS seat — ideal for time-boxed engagements where standing up a Celonis data model is overkill and too slow. 7) COST/EFFORT: We avoid the $150K-$5M+ platform spend and multi-month ETL setup for a discovery deliverable. NOTE: these are complementary, not mutually exclusive — the honest competitive line is 'process mining quantifies the structured processes that exist; we discover the documented-vs-actual contradictions and the processes that aren't in any log.'

## Documented weaknesses / complaints (and how we address them)

### High and opaque cost; very expensive vs. alternatives, long multi-year contracts, plus indirect cost of hiring data scientists/process analysts. Celonis 'is the most expensive solution in the market'; entry ~$15K but routinely $200K+; SAP Signavio $150K-$800K/yr; UiPath $40K-$200K/yr; Microsoft 'very expensive.' Licensing is data/consumption-based, making client costs 'hard to estimate.'

_Evidence:_ PeerSpot reviewers: Celonis 'is very expensive compared to other process mining tools' (Data Engineer, Baker Hughes); 'Celonis is the most expensive solution in the market.' SAP Signavio: 'Their licensing structure isn't ideal as it's based on data; therefore, it's hard to estimate client costs'; prices 'increased significantly' after the SAP acquisition. G2/Gartner: 'cost and packaging complexity are described as very expensive.'

_Source:_ G2 Celonis reviews (https://www.g2.com/products/celonis/reviews?qs=pros-and-cons); PeerSpot Celonis (https://www.peerspot.com/products/celonis-reviews); PeerSpot SAP Signavio Process Intelligence (https://www.peerspot.com/products/sap-signavio-process-intelligence-reviews); Gartner Peer Insights Celonis likes/dislikes (https://www.gartner.com/reviews/market/process-mining-platforms/vendor/celonis/product/celonis-process-intelligence-platform/likes-dislikes)

**How we address it:** Delivered as a fixed-scope consulting accelerator, not a per-seat/consumption SaaS license with multi-year lock-in. No analytics-processing-capacity meter, no per-process license, no separately-staffed data-science team required — the agent calls generic tools over whatever docs/CSVs exist. Cost is bounded by the engagement, not by data volume or number of processes.

### Long time-to-value / lengthy, difficult implementation. Initial setup and data integration is 'complex and time-consuming'; full implementations 'commonly take 12 to 24 months, and even longer in large organizations'; even best-case initial insights take 4-8 weeks AFTER data is loaded, and 'more often than not it takes longer than expected.' Misaligned expectations and unrealistic timelines are a top cause of project abandonment.

_Evidence:_ ProcessMaker / ProcessMind: implementations 'commonly take 12 to 24 months'; '70% of transformation programs don't achieve their desired outcomes.' Gartner via reviews: 'time to value being slower than expected.' G2: setup 'complex and time-consuming, requiring significant technical effort.'

_Source:_ ProcessMaker '5 reasons process mining projects fail' (https://www.processmaker.com/blog/5-reasons-process-mining-projects-fail-and-how-to-overcome-them/); ProcessMind challenges guide (https://processmind.com/resources/blog/process-mining-challenges-common-failures-and-best-practices); G2 Celonis reviews (https://www.g2.com/products/celonis/reviews)

**How we address it:** Time-to-first-finding is hours-to-days, not months: the platform ingests heterogeneous documents as-is (no event-log modeling, no per-process data model build) and autonomously produces findings plus the full 6-report client suite. Zero-config across any domain's docs removes the up-front data-modeling project that drives the 12-24 month timelines.

### Requires clean, structured event logs (Case ID + Activity + Timestamp); 80%+ of project effort goes to locating, extracting, transforming and cleaning data before any analysis can start. Logs routinely have incorrect timestamps, missing attributes, and noise that distort results and need heavy IT remediation first.

_Evidence:_ Gartner 2020 Process Mining Market Guide (quoted by Skan.ai): 'Typically, 80% of the effort and time are spent on locating, selecting, extracting and transforming the process.' Survey data: '81% of respondents stated that event log extraction efforts consume significant time'; '84% reported event logs are typically extracted from multiple database tables.' MDPI review: logs 'have data quality issues such as incorrect timestamps, noisy data and missing data attributes.'

_Source:_ Skan.ai 'What's Wrong with Process Mining' (https://www.skan.ai/blogs/whats-wrong-with-process-mining-skan); SAP Community on event log generation challenges (https://community.sap.com/t5/technology-blog-posts-by-sap/preparing-data-in-process-mining-challenges-with-event-log-generation/ba-p/13523010); MDPI Event Log Preprocessing review (https://www.mdpi.com/2076-3417/11/22/10556)

**How we address it:** No event-log contract required. The agent computes directly over raw heterogeneous inputs (SOPs, policies, RACIs, system CSV exports, working notes) using generic describe/group_by/join_diff/filter_count tools — it does NOT need pre-built Case-ID/Activity/Timestamp logs. The expensive 80% ETL/event-log-construction step is eliminated, not just reduced.

### Cannot derive process from UNSTRUCTURED documents (SOPs, policies, RACIs, notes). Process mining is built for structured, totally-ordered, timestamped event data; on unstructured text 'a direct application of process mining is not possible or unlikely to lead to useful results.' Documents have no native Case ID/Activity/Timestamp.

_Evidence:_ arXiv 2401.13677 ('Process Mining for Unstructured Data'): classical process mining 'assumes that event data is totally ordered, discrete, correct, and accurate... meeting these requirements is challenging for unstructured data, making direct application of process mining not possible or unlikely to lead to useful results.' ACM SLR (10.1145/3727148) confirms unstructured-data integration is still an emerging research direction, not a shipped capability.

_Source:_ arXiv 2401.13677 (https://arxiv.org/abs/2401.13677); ACM Transactions on MIS, 'Unstructured Data in Process Mining: A Systematic Literature Review' (https://dl.acm.org/doi/10.1145/3727148)

**How we address it:** This is the product's core design. It is an LLM-agent platform purpose-built to read and reason over unstructured business documents, extracting documented process, ownership (RACI), and controls — then cross-checks them against system CSV data. It does natively what the process-mining category's own literature says it cannot do.

### Blind to manual, off-system, undocumented, or unowned processes. Process mining only shows what generates logs inside a system — 'Many process steps are not visible from an event-log.' Manual work, off-system activities, and steps that don't emit logged events stay invisible, producing an incomplete or misleading picture of how work actually gets done. A control gap living in a spreadsheet plus an email is unseeable.

_Evidence:_ Skan.ai: 'Many process steps are not visible from an event-log... Manual work, off-system activities, and steps within systems that don't produce logged events remain invisible, creating significant gaps between what process mining reveals and actual operational reality.' Reinforced by the 'knowledge paradox' (Deloitte 2021): you already need process knowledge to make process mining work.

_Source:_ Skan.ai 'What's Wrong with Process Mining' (https://www.skan.ai/blogs/whats-wrong-with-process-mining-skan); Deloitte 2021 Global Process Mining Survey (cited via Skan.ai)

**How we address it:** Because findings come from documents AND data (not logs), the platform surfaces exactly these blind spots: undocumented/unowned processes, control gaps, and contradictions between what the SOP says and what the system data shows. Discovering the off-system/unowned process is a primary output, not a gap.

### Black-box outputs that business users struggle to trust and validate; no built-in provenance/confidence. Data-science outputs are 'shown as black boxes... which affects the confidence of professionals who are suspicious of the results'; verification of validity/reliability 'cannot be accomplished, which leads to lack of trust.' Root-cause results become untrustworthy when underlying systems hold conflicting/outdated records, and users lack a clear way to validate output quality.

_Evidence:_ Springer/research ('Can Users Trust Process Mining?', study of 18 PM users): documents 'challenges they face when validating the quality of process mining output.' arXiv XAI-for-PM literature: black-box techniques 'suffer notably in delivering appropriate explanations about their outcomes... leads to lack of trust and reliance.' eSystems RCA: 'when different systems contain conflicting or outdated records, RCA results become less trustworthy.'

_Source:_ 'Can Users Trust Process Mining?' Springer (https://link.springer.com/chapter/10.1007/978-3-031-94193-1_11); XAI for Predictive Process Monitoring SLR (https://arxiv.org/pdf/2312.17584); eSystems Root Cause Analysis (https://www.esystems.fi/en/blog/root-cause-analysis-principles-and-role-in-process-data-mining)

**How we address it:** Every finding carries explicit confidence and provenance, and every number traces back to the source data, enforced by a grounding gate (consistent-not-fabricated). A human SME stays in the loop. This directly answers the 'can I trust/validate this output?' problem rather than presenting an opaque score.

### Steep learning curve / requires specialist (data scientist, PQL/analyst) skills; cumbersome usability for non-technical users. Celonis users 'find the learning curve to be steep, particularly those without a data background.' Microsoft's advanced analytics/AI features 'have a steep learning curve.' UiPath's debugging is 'steeper than the low-code positioning suggests.'

_Evidence:_ Gartner Peer Insights / G2 Celonis: 'steep learning curve... cumbersome functionalities hindering usability'; 'steep, particularly those without a data background.' Microsoft Power Automate Process Mining: 'advanced features can have a steep learning curve... difficult to understand for new users.' UiPath: 'debugging complex workflows has a steeper learning curve than the low-code positioning suggests.'

_Source:_ Gartner Peer Insights Celonis likes/dislikes (https://www.gartner.com/reviews/market/process-mining-platforms/vendor/celonis/product/celonis-process-intelligence-platform/likes-dislikes); G2 Celonis (https://www.g2.com/products/celonis/reviews); Gartner Power Automate Process Mining (https://www.gartner.com/reviews/product/power-automate-process-mining)

**How we address it:** The agent does the reasoning and the tooling internally; clients consume plain-language reports with no tool jargon (no PQL, no event-log modeling, no dashboard-building skill needed). SMEs review findings in business language. There is no specialist platform skill set to staff or train up.

### Ongoing manual data upkeep, connector maintenance, and per-tenant capacity limits. Process mining 'requires integrations to every different source system' with continual upkeep; Microsoft imposes hard platform ceilings (Dataverse-managed Power BI workspaces 'allow only 1,000 reports per environment'; you can 'run out of Dataverse storage capacity' and must buy more or delete processes); large datasets degrade performance.

_Evidence:_ G2 Celonis: 'requires integrations to every different source system to extract event logs.' Microsoft Learn / Gartner: 'Dataverse-managed Power BI workspaces allow only 1,000 reports for each environment'; 'you might run out of Dataverse storage capacity'; 'Performance is a little degraded while compiling a large set of data.' UiPath: 'limitations in terms of the number of rows of data it can actually handle.'

_Source:_ G2 Celonis reviews (https://www.g2.com/products/celonis/reviews); Microsoft Learn Power Automate process mining data prep (https://learn.microsoft.com/en-us/power-automate/process-mining-processes-and-data); Gartner Power Automate Process Mining (https://www.gartner.com/reviews/market/process-mining-platforms/vendor/microsoft/product/power-automate-process-mining); PeerSpot UiPath Process Mining (https://www.peerspot.com/products/uipath-process-mining-reviews)

**How we address it:** Engagement-based discovery rather than a standing, continuously-fed data pipeline: the platform analyzes the document/CSV corpus provided for the engagement, so there are no live connectors to maintain, no per-environment report ceilings, and no consumption meter to keep topped up between analyses.

### Vendor/ecosystem lock-in and weakness outside the home stack — especially SAP Signavio, which is 'focused on SAP modules, limiting insights for non-SAP environments'; 'connecting to non-SAP source systems may be difficult'; reporting/analytics are 'very weak.' Microsoft similarly has 'limited flexibility for non-Microsoft integrations.' A carve-out's whole problem is a messy multi-vendor heterogeneous landscape.

_Evidence:_ Gartner/PeerSpot SAP Signavio: 'process mining capabilities are focused on SAP modules, limiting insights for non-SAP environments'; 'Connecting to non-SAP source systems may be difficult'; 'The data and reporting side of SAP Signavio is very weak.' Microsoft: 'limited flexibility for non-Microsoft integrations compared to other platforms.'

_Source:_ Gartner Peer Insights SAP Signavio likes/dislikes (https://www.gartner.com/reviews/market/process-mining-platforms/vendor/sap/product/sap-signavio-process-intelligence/likes-dislikes); PeerSpot SAP Signavio (https://www.peerspot.com/products/sap-signavio-process-intelligence-reviews); Gartner Power Automate Process Mining reviews (https://www.gartner.com/reviews/product/power-automate-process-mining)

**How we address it:** Runs on ANY domain's documents and any system's CSV exports with zero config — it is deliberately stack-agnostic. For exactly the heterogeneous, mixed-vendor environments a carve-out leaves behind, this avoids the single-ERP blind spot that hobbles SAP- or Microsoft-anchored process mining.

### No carve-out / TSA-exit specificity. Process mining tools are general operational-monitoring platforms; they don't speak to divestiture realities (stranded IT cost, TSA-exit deadlines, application rationalization), and in a carve-out the historical event data is often poorly planned, incomplete, or locked behind the seller — which 'extends TSAs, increasing infrastructure costs, and delaying operational independence.' This is precisely when reliable event logs don't exist yet.

_Evidence:_ Archon / PE-Insights / Deloitte: 'Poor historical data planning often extends Transition Service Agreements (TSAs), increasing infrastructure costs, and delaying operational independence'; after TSA exit the seller is left with 'stranded IT costs.' Carve-outs require 'discovery, extraction, validation, archive access' work — the kind of unstructured, partial, transitional state where event-log-dependent tools are weakest.

_Source:_ Archon Data Store SAP Carve-Out strategy (https://www.archondatastore.com/blog/sap-carve-out-strategy/); PE-Insights divestment & carve-out challenges (https://pe-insights.com/divestment-carveout-challenges-pmi/); Deloitte 'The Art of Speed: Accelerating the exit from IT Transition Service Agreements' (https://www.deloitte.com/ch/en/services/consulting-financial/research/the-art-of-speed.html)

**How we address it:** Purpose-positioned for consulting-led, post-carve-out / TSA-exit application and process rationalization. Because it derives findings from documents plus partial data exports rather than a mature, clean event-log pipeline, it works in exactly the data-poor, time-boxed transitional environment where process mining cannot yet be stood up. Output is the consulting deliverable suite (Current State, Pain Points, Transformation Recommendation, AI Opportunity Portfolio, Roadmap, Supporting Artefacts) needed to drive a rationalization decision.
