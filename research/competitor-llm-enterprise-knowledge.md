# Competitor Dossier — LLM/Agentic Enterprise Knowledge & Discovery (knowledge graphs from docs, agentic-RAG, ontology-grounded agents, data-intelligence)

_Market research generated 2026-06-02 via a multi-agent web-research workflow (11 agents, deep web search + analyst/review mining). Cited throughout. This is a standing reference — read it instead of re-searching._


## Category summary

This category covers platforms that turn an enterprise's unstructured/semi-structured content (docs, tickets, chats, exports) into machine-usable knowledge and then let LLMs/agents search, answer, or act over it. Four sub-segments matter for us:

(1) HORIZONTAL KNOWLEDGE/SEARCH + AGENT PLATFORMS (Glean, Microsoft 365 Copilot). They build a knowledge graph by automated entity/noun extraction + relationship (predicate) inference across 100+ connectors, attach edge metadata (timestamp, ACL, confidence, provenance), and use it to ground retrieval and, since fall/winter 2025, autonomous agents (Glean Enterprise Graph + autonomous agents Dec 2025; Microsoft Graph Semantic Index + Copilot APIs/connectors). Their graph is a RETRIEVAL/CONTEXT graph (Content-People-Activity) — it maps who-owns/relates-to-what to answer questions and route agent actions. It does NOT compute over the numeric content of CSVs/system exports, does not adjudicate documented-process-vs-actual-data contradictions, and does not emit a grounded, provenance-tiered consulting deliverable. Sold as per-seat SaaS at scale.

(2) ONTOLOGY-GROUNDED AGENT PLATFORM (Palantir AIP/Foundry). The closest philosophical match to us: it explicitly prevents hallucination via Ontology-Augmented Generation and uses deterministic tools to complement probabilistic LLM reasoning (LLMs are poor at math, so optimizers/forecasters do the computation) — exactly our code-does-the-math, agent-does-the-reasoning split. BUT it requires a substantial upfront ontology-modeling + data-integration project, typically delivered by Forward Deployed Engineers on-site for months. It is NOT zero-config on raw heterogeneous docs.

(3) VERTICAL AGENTIC DOCUMENT-REASONING (Hebbia Matrix). Multi-agent, full-document (not chunked) reasoning that produces decision artifacts (memos, diligence summaries, decks) at ~92% benchmark accuracy vs ~68% naive RAG. Tightly aimed at finance/legal, very high per-seat price, document-centric — it reasons over documents, it does not discover contradictions between documented process and live system data, and has no formal grounding gate forcing every number to trace to source data.

(4) DATA-INTELLIGENCE / DSPM (Cyera). AI-native, agentless discovery + LLM-based classification of where SENSITIVE data lives and how it is accessed (DSPM, >95% classification precision, Access Trail). Adjacent, not competitive on the discovery job-to-be-done — it inventories/classifies data and access risk; it does not do business-process rationalization, pain-point/transformation analysis, or a consulting report suite.

Adjacent but worth flagging in any eval: Celonis (data-driven process discovery) — but it requires structured event logs from ERP/CRM, not heterogeneous documents, and produces process models/conformance, not a value-feasibility/AI-opportunity transformation suite.

The structural gap across the whole category: knowledge-graph/RAG entity & relationship extraction is reliable for NER (precision often in the 90s%) but relationship/predicate extraction and canonicalization are materially weaker and prone to hallucinated/co-mention relationships; production systems mitigate to <2% only with heavy graph grounding. None of the horizontal incumbents (Glean/Copilot) close the loop from extracted-knowledge to a CONSISTENT-NOT-FABRICATED, confidence-tiered, decision-grade rationalization deliverable with every number traced to source — which is precisely our wedge, especially for post-carve-out / TSA-exit application & process rationalization where the docs are messy and zero-config matters.

## Vendors

### Glean (Work AI / Enterprise Graph + Autonomous Agents)

**What it does:** Horizontal enterprise search + Work-AI assistant + (since Dec 2025) autonomous agents, all grounded on a per-customer knowledge graph built from connected enterprise apps. Answers questions, surfaces context, and runs end-to-end agent tasks across tools like Salesforce, Jira, Confluence, GitHub.

**Approach:** Builds the knowledge graph by ML with no human inspection: automated noun/entity extraction + frequency/prominence filtering, then extracts descriptive terms and possible relationships (predicates), prioritizing strongly-evidenced facts (authorship, project leadership). Organized around Content-People-Activity with edge metadata (timestamp, ACL, confidence, provenance). Fall-2025 Enterprise Graph adds higher-value entities (projects, customers, products); Glean Enterprise Context (memory+connectors+indexes+graphs+governance) powers agents that interpret intent, sequence 100+ built-in actions, adapt, and verify against governance.

**Inputs required:** Live connections to enterprise SaaS via 100+ connectors; ongoing crawl/index; identity/permissions sync. Runs as a continuously-updated layer over your stack.

**Pricing:** Sales-led, no public price. ~$45-50/user/mo base + ~$15/user/mo AI add-on; ~100-seat minimum (~$60k/yr floor). FlexCredits consumption for premium features. Fully-loaded TCO ~$350k-$480k/yr for mid-large (incl. ~10% support, BYOC infra, $20k-$50k onboarding).

**Differentiator:** The most mature horizontal enterprise knowledge graph + the broadest connector footprint, now extended into enterprise-grade autonomous agents. KEY LIMIT vs us: by its own materials the graph centers on document retrieval & relationship mapping, NOT numerical computation — no decision-grade quantitative rationalization, no grounded-numbers gate, no documented-vs-system contradiction discovery, no consulting report suite.

**Sources:**
- https://www.glean.com/blog/knowledge-graph-agentic-engine
- https://www.glean.com/product/enterprise-graph
- https://www.glean.com/blog/live-fall-25-main
- https://www.businesswire.com/news/home/20251210210198/en/Glean-Launches-the-Work-AI-Institute-Unveils-Autonomous-Agents-Built-on-Glean-Enterprise-Context-to-Operationalize-AI-at-Work
- https://www.gosearch.ai/blog/glean-pricing-explained/
- https://www.vendr.com/marketplace/glean

### Microsoft 365 Copilot (Microsoft Graph + Semantic Index + Copilot connectors/agents)

**What it does:** AI assistant + agent platform native to M365 that grounds answers and agents in organizational data via Microsoft Graph and the semantic index, with Copilot Studio for custom agents and Copilot connectors to index external data (Salesforce, ServiceNow, Confluence, Box, etc.).

**Approach:** Maps org data into a lexical + semantic index (Microsoft Graph Semantic Index, a continuously-updated vector representation). At query time it understands intent, retrieves from Graph + semantic index, and grounds the LLM so answers cite specific paragraphs/tables/metadata. Copilot connectors ingest and semantically index external content into Graph. New APIs (Retrieval, Interactions Export, Change Notifications, Meeting Insights, Chat) let custom agents use the same index.

**Inputs required:** Qualifying M365 base license (E3/E5/Business Standard/Premium) + tenant data in Graph; 100+ Copilot connectors for external sources; identity/permissions inherited from M365.

**Pricing:** $30/user/mo (annual) enterprise add-on on top of base license; $18/user/mo for Business (<300 users). Note base E3->$39 and E5->$60 effective Jul 1 2026, raising effective per-user cost.

**Differentiator:** Ubiquity and zero-friction grounding inside the M365 estate; semantic index over data the enterprise already holds. KEY LIMIT vs us: retrieval/grounding for Q&A and agents over indexed content; does not compute analytic findings over CSV/system-export numbers, does not adjudicate documented-vs-actual contradictions, no confidence-tiered decision-grade rationalization deliverable.

**Sources:**
- https://learn.microsoft.com/en-us/microsoftsearch/semantic-index-for-copilot
- https://learn.microsoft.com/en-us/microsoft-365/copilot/connectors/overview
- https://www.microsoft.com/en-us/microsoft-365-copilot/pricing
- https://www.eesel.ai/blog/copilot-pricing
- https://www.infoworld.com/article/4016219/working-with-microsoft-365s-new-copilot-apis.html

### Palantir AIP / Foundry (Ontology-grounded agents)

**What it does:** Enterprise AI operating layer that embeds LLMs into a governed, bidirectional ontology of business objects (Customer, Work Order, Supply-Chain Route) so agents reason and act against operational truth; AIP Chatbot/Agent Studio builds enterprise-context agents.

**Approach:** Ontology-Augmented Generation (OAG): instead of retrieving text it retrieves typed structured objects + relational edges; the LLM invokes DETERMINISTIC tools (optimizers like cuOpt, forecasters like Prophet) for math/logic because LLMs are poor at computation. Hallucination is prevented by anchoring to live ontology objects.

**Inputs required:** Substantial upfront ontology modeling + data-pipeline integration, typically delivered by Forward Deployed Engineers on-site for months; not zero-config on raw documents. (AI-FDE beta from Nov 2025 assists ontology dev.)

**Pricing:** Negotiated by scope (use cases, data volume, users, customization); not a per-seat SKU. Enterprise-scale: Q3-2025 had 204 deals >$1M and 53 deals >$10M; engagements often start with a bootcamp + limited licenses then expand.

**Differentiator:** Deepest operational grounding: governed ontology + deterministic-tools-for-math (same anti-hallucination principle as our code-does-the-math) with the ability to act on live systems. KEY LIMIT vs us: does not run zero-config on heterogeneous docs; needs a months-long ontology/data-integration project and heavy services — optimized for ongoing operations, not a fast, bounded, document-driven discovery/rationalization deliverable.

**Sources:**
- https://www.palantir.com/platforms/aip/
- https://anandbg.com/blog/palantir-aip-end-to-end-agentic-architecture
- https://towardsai.net/p/machine-learning/inside-palantir-aip-how-the-worlds-most-controversial-ai-platform-actually-works
- https://www.palantir.com/docs/foundry/ai-fde/overview
- https://www.everestgrp.com/palantir-inside-the-category-of-one-forward-deployed-software-engineers-blog/

### Hebbia (Matrix)

**What it does:** Agentic document-reasoning platform for finance/legal that interrogates large document sets and generates decision artifacts (investment memos, diligence summaries, board decks). Serves 40%+ of largest asset managers; processed 1B+ pages; clients incl. BlackRock, KKR, Carlyle, MetLife.

**Approach:** Matrix decomposes a query into structured steps and runs multiple agents in parallel, routing subtasks to best-fit models (semantic search, tabular extraction, legal-term ID) and processing full documents (not chunks) for an infinite effective context window. ~92% accuracy on rigorous fin/legal benchmarks vs ~68% naive RAG. FlashDocs acquisition (Jun 2025) adds automated deck/memo generation.

**Inputs required:** Upload/connect document corpora + premium data sources (PitchBook, CapIQ, broker research); document-centric, no enterprise-wide graph or ERP integration required.

**Pricing:** Custom enterprise, mid-to-high six figures/yr typical. Reported ~$10k/seat/yr Professional (unlimited reasoning), ~$3k-$3.5k/seat/yr Lite; chatter of up to ~$20k/user/yr. Rigid long-term contracts.

**Differentiator:** Highest-accuracy deep multi-agent reasoning over very large document sets, with output-generation (memos/decks) — the leader for finance/legal deep research at volume. KEY LIMIT vs us: reasons over DOCUMENTS to produce research outputs; does not discover contradictions between documented process and live system data, has no formal grounding gate forcing every number to trace to source, is vertical (finance/legal) not domain-agnostic process discovery, and is not a transformation/value-feasibility/AI-opportunity rationalization suite.

**Sources:**
- https://www.hebbia.com/
- https://openai.com/index/hebbia/
- https://financefeeds.com/the-ai-platform-wall-street-cant-ignore-inside-hebbias-breakout-2025/
- https://www.eesel.ai/blog/hebbia-ai-pricing
- https://en.wikipedia.org/wiki/Hebbia

### Cyera (AI Data Security / DSPM)

**What it does:** AI-native data security posture management: agentless discovery + classification of sensitive data across cloud/SaaS/on-prem/hybrid, plus identity/access context and AI-usage visibility (Access Trail, launched Nov 2025).

**Approach:** Agentless scanning at petabyte scale; LLM-powered classification (FLAN-T5 + Mistral) plus clustering + learned intelligence for contextual understanding (>95% classification precision), continuously learning new data classes. Unifies classification + context + identities + usage/movement into data-risk intelligence.

**Inputs required:** Cloud/SaaS/on-prem connections for agentless scanning; identity sources for access mapping.

**Pricing:** Enterprise, custom/sales-led (no public per-seat price); positioned as platform for large enterprises.

**Differentiator:** Best-in-class agentless sensitive-data discovery & classification at massive scale with access/AI-governance lineage. KEY LIMIT vs us: solves data-SECURITY posture, not business-process discovery — inventories/classifies sensitive data and access risk; no process rationalization, no documented-vs-actual contradiction findings, no transformation/AI-opportunity report suite. Adjacent, not head-to-head.

**Sources:**
- https://www.cyera.com/platform/dspm
- https://www.cyera.com/glossary/data-security-posture-management-dspm
- https://www.businesswire.com/news/home/20251112242260/en/Cyera-Introduces-Access-Trail-to-Uncover-Details-Behind-Every-Data-Touchpoint-Across-Humans-and-AI
- https://netwrix.com/en/resources/blog/cyera-alternatives/

### Celonis (Process Mining / Process Intelligence) — adjacent benchmark

**What it does:** Data-driven process discovery and conformance: builds process models from system event data (ERP/CRM/logs), reveals bottlenecks, deviations, and compliance/execution gaps, and recommends/automates fixes.

**Approach:** Mines event logs extracted from business systems to reconstruct how processes actually run (vs subjective workshop-based maps), then surfaces conformance gaps and AI-enhanced recommendations.

**Inputs required:** Structured event logs / system data from ERP, CRM, and logs — NOT heterogeneous documents (SOPs/policies/notes).

**Pricing:** Enterprise, custom/sales-led.

**Differentiator:** Gold standard for data-driven, conformance-grade process discovery directly from transactional system data. KEY LIMIT vs us: requires structured event logs and system integration; does not ingest unstructured SOPs/policies/RACIs/notes, does not adjudicate the documented-process narrative against the data, and does not output a value-feasibility / AI-opportunity / roadmap consulting suite. Complementary on event data, weak on the document side where we are strong.

**Sources:**
- https://www.celonis.com/blog/how-process-mining-modernizes-process-discovery
- https://www.celonis.com/blog/automated-process-discovery
- https://www.celonis.com/blog/ai-enhanced-process-mining

## Where they beat us (be honest)

SCALE, BREADTH & ECOSYSTEM. (1) Connector breadth & live operations: Glean (100+ connectors, continuously-updated graph) and Microsoft Copilot (Microsoft Graph + 100+ connectors, native in M365) index the entire enterprise continuously and serve thousands of users in production; our product is a point-in-time, domain-scoped discovery accelerator, not a live enterprise-wide knowledge layer. (2) Action/agent execution: Glean's Dec-2025 autonomous agents and Palantir AIP actually EXECUTE tasks across Salesforce/Jira/ServiceNow and write back to operational systems; we discover and recommend, we don't operate. (3) Vertical reasoning depth: Hebbia processes 1B+ pages, full-document parallel multi-agent reasoning at ~92% accuracy, trusted by BlackRock/KKR — for deep finance/legal document interrogation at volume it outclasses a generalist discovery agent. (4) Operational-truth ontology: Palantir's governed ontology + deterministic tools give it stronger, continuously-live grounding to real operational objects (you cannot hallucinate a customer order number) and a defensible enterprise-OS footprint, backed by 200+ $1M and 50+ $10M deals/quarter. (5) Procurement comfort & references: all are funded, category-leading, SOC2/governance-mature, with marquee logos and analyst coverage; a consulting accelerator from a smaller vendor carries more buyer/procurement risk. (6) Data-security adjacency: Cyera's agentless classification at petabyte scale + Access Trail gives it sensitive-data/AI-governance coverage we don't attempt.

## Where we beat them

DECISION-GRADE, GROUNDED, ZERO-CONFIG DISCOVERY — the job none of them actually do. (1) Compute over the data, not just retrieve it: incumbents' graphs are retrieval/context graphs (Glean's own materials say the graph centers on document retrieval & relationship mapping, NOT numerical computation). We call generic describe/group_by/join_diff/filter_count tools so CODE computes the math over ANY CSV/system export and the agent reasons over the results — surfacing contradictions between documented process and actual system data, undocumented/unowned processes, and control gaps that a search/RAG layer cannot find. (2) Consistent-not-fabricated grounding gate: every client-facing number is structurally checked against an allow-list traced to source data before it can render; no incumbent enforces a hard grounding gate on numeric claims (even Hebbia/Copilot can surface plausible-but-ungrounded figures; academic + production evidence shows relationship extraction and numeric grounding remain the failure modes). (3) Zero-config on raw heterogeneous docs: we run on SOPs/policies/RACIs/CSVs/notes with no ontology build — Palantir AIP, by contrast, needs months of Forward-Deployed-Engineer ontology + pipeline work, and Celonis needs structured ERP event logs. Our time-to-finding is days, not a quarter-long integration. (4) Decision-grade output as the product: we ship a 6-report consulting suite (Current State, Pain Points, Transformation Recommendation with value-feasibility matrix, AI Opportunity Portfolio with before/after per opportunity, Roadmap, Supporting Artefacts) with confidence/provenance tiering and NO tool jargon in client output — incumbents output search answers, agent actions, or generic memos, not a value-feasibility-and-roadmap rationalization deliverable. (5) Domain-agnostic, zero-config across O2C/P2P/etc.; SME-in-the-loop. (6) Commercial fit for the exact use case: a consulting accelerator (not per-seat SaaS) priced for a bounded engagement is far cheaper and faster for post-carve-out/TSA-exit application & process rationalization than Glean (~$50/user/mo, ~$350k-$480k TCO, 100-seat min), Copilot ($30/user/mo add-on on top of rising E3/E5), Hebbia (~$10k-$20k/seat/yr), or a multi-month Palantir deployment.

## Documented weaknesses / complaints (and how we address them)

### High, opaque, sales-led pricing with steep seat minimums and built-in annual price hikes (Glean ~$50/user/mo, 100-seat / ~$50-60k minimum, fully-loaded TCO $350k-$480k/yr; mandatory ~10% support fee; renewals default to 7-12% annual increases).

_Evidence:_ Workativ/GoSearch pricing breakdowns and G2 reviews report Glean does not publish pricing, uses custom quotes with contract minimums, and bakes 7-12% annual increases into standard terms; G2 reviewers note pricing is 'higher than many competitors.'

_Source:_ G2 Glean Reviews 2026 (g2.com/products/glean-technologies-glean/reviews); Workativ 'Glean Pricing: Costs, Hidden Fees & TCO Breakdown 2026' (workativ.com/ai-agent/blog/glean-pricing); GoSearch 'Glean Pricing Explained' (gosearch.ai/blog/glean-pricing-explained)

**How we address it:** We are delivered as a consulting accelerator on a per-engagement basis, not a per-seat SaaS subscription. There is no 100-seat minimum, no recurring per-user license to renew, and no built-in annual price escalator. Cost scales with the discovery engagement, not headcount.

### Hebbia Matrix is 'insanely expensive' enterprise per-seat pricing (~$3k-3.5k/user/yr Lite, ~$10k/user/yr Pro) with an old-school sales model, required demos, long negotiations, rigid contracts, no free trial and no self-serve.

_Evidence:_ eesel AI Hebbia review and pricing analysis cite tiered per-user pricing and describe the 'old-school sales model and hidden, sky-high pricing'; users on Reddit call it 'insanely expensive.'

_Source:_ eesel AI 'An honest Hebbia AI review' (eesel.ai/blog/hebbia-ai-review); eesel AI 'Hebbia AI pricing 2025' (eesel.ai/blog/hebbia-ai-pricing); Hebbia G2 reviews (g2.com/products/hebbia/reviews)

**How we address it:** Same wedge as above: engagement-based consulting delivery rather than high per-seat licenses aimed at finance/legal individuals. The buyer is a transformation/consulting program, not a roster of named seats, so cost is tied to deliverables produced.

### Long, expensive implementations requiring structured/clean event logs and per-system integrations (Celonis): 12-24 months and multiple FTEs to stand up, ~$50-100k of work per process in year one, plus hiring data scientists/process analysts and 3-year contracts.

_Evidence:_ ProcessMaker pricing guide and aimultiple report Celonis requires integrating each source system separately to extract event logs, 12-24 month implementations, multiple FTEs, and significant indirect cost; Gartner Peer Insights cites steep learning curve, 'very expensive,' and 'time to value slower than expected.'

_Source:_ ProcessMaker 'How much does process mining cost? 2024 pricing guide' (processmaker.com/blog/how-much-does-process-mining-cost-2024-pricing-guide); aimultiple Celonis research (research.aimultiple.com/celonis); Gartner Peer Insights Celonis likes/dislikes (gartner.com/reviews/market/process-mining-platforms/vendor/celonis)

**How we address it:** We do NOT require clean structured event logs or per-system ETL pipelines. We ingest heterogeneous raw business documents (SOPs, policies, RACIs, system CSV exports, working notes) with zero config and compute over them with generic tools. This removes the event-log dependency that gates process-mining tools and collapses the multi-month data-engineering runway.

### Palantir Foundry/AIP requires a substantial upfront ontology-modeling + data-integration project delivered by Forward Deployed Engineers, often on-site for months; FDE support is typically capped at 12-18 months and extensions run ~£1,500-£3,500/person/day; TCO reaches millions/yr.

_Evidence:_ Redress Compliance negotiation guide details bundled professional services, FDE periods of 12-18 months, and day rates of £1,500-£3,500; Medium/TowardsAI analysis calls deployments 'service-intensive and costly' with TCO 'into millions annually.'

_Source:_ Redress Compliance 'Palantir AIP and Foundry: The Enterprise Buyer's Negotiation Guide' (redresscompliance.com/palantir-aip-foundry-guide.html); 'Palantir Foundry Ontology... Where It Falls Short' (pub.towardsai.net / medium @cloudpankaj)

**How we address it:** We are zero-config on raw heterogeneous docs - no upfront ontology-modeling project and no months of FDE on-site integration before value appears. The agent discovers findings by computing over whatever documents/CSVs are provided, so the buyer gets a discovery deliverable in an engagement timeframe rather than after a multi-quarter platform build.

### Persistent hallucination / fabrication in production: Copilot still invents meeting attendees, nonexistent product codes, and mangles docs; 68% of SMB early adopters hit at least one significant error; a Microsoft lead admitted the 'confabulation rate' is too high for unattended automation.

_Evidence:_ Windows News 'Microsoft Copilot Backlash' and Windows Forum report invented attendees/product codes, the 68% error-rate survey, and the engineering-lead admission that confabulation is a multi-year research problem; Glean's own chat is noted to 'hallucinate answers' in G2 reviews.

_Source:_ Windows News 'Microsoft Copilot Backlash: Trust vs AI Automation Promises in 18 Months' (windowsnews.ai); Windows Forum 'Microsoft Copilot Under Strain: Enterprise ROI and Reliability' (windowsforum.com/threads/...400271); G2 Glean Reviews 2026

**How we address it:** Every number in our output must trace to the source data and is checked by a grounding gate (consistent-not-fabricated). Code does the math; the agent only reasons. This directly targets the fabrication failure mode that makes generic copilots unsafe for decision-grade financial/process outputs.

### Outputs require manual verification against source files because they aren't trustworthy enough - defeating the tool's purpose. Hebbia users said it was 'not reliable enough to come up with trustworthy answers,' they 'still had to go read source files to confirm,' and it produced 'AI slop' from 'bad sources.'

_Evidence:_ eesel AI review aggregating Reddit/G2 feedback: 'not reliable enough,' 'still had to go read source files to confirm,' 'AI slop and leverage bad sources,' custom AI layer 'a lot worse than ChatGPT.'

_Source:_ eesel AI 'An honest Hebbia AI review' (eesel.ai/blog/hebbia-ai-review); Hebbia G2/Reddit aggregation

**How we address it:** We attach confidence and provenance to every finding and enforce a grounding gate, so a reviewer can verify a number against its traced source without re-reading the whole corpus. Human-SME-in-the-loop is built into the workflow rather than being an unplanned cleanup step.

### Black-box outputs with no per-step provenance or decision traces erode trust and block enterprise/security sign-off; in high-stakes domains hallucination is the single biggest driver of agent abandonment, and courts sanctioned attorneys $145k in Q1 2026 for AI-fabricated citations.

_Evidence:_ Arthur.ai, Seekr 'Hallucination Tax,' and Microsoft Research VeriTrail (early 2026) argue agentic workflows need per-step provenance because errors propagate; sourced systems made users measurably more confident; Stanford RegLab measured 69-88% hallucination on legal queries.

_Source:_ Arthur.ai 'AI Agent Security Best Practices for Enterprise Trust' (arthur.ai/column/...); Seekr 'The Hallucination Tax' (seekr.com/resource/...); Microsoft Research VeriTrail (early 2026); Stanford RegLab (cited in Seekr/Arthur)

**How we address it:** Findings carry confidence and provenance (every number traceable to source data), giving the auditable decision trail these analyses say is required for trust and sign-off. Our wedge is precisely a consistent-not-fabricated, confidence-tiered deliverable rather than an unsourced black box.

### RAG/retrieval-centric copilots are good at factual lookup but not deep analytical reasoning or quantitative computation over structured data; Copilot has no native record retrieval for Databricks/Workday/BigQuery and is focused on text generation, not data analysis.

_Evidence:_ Medium RAG analyses state 'RAG works best for factual questions and answers, not deep document analysis'; Glean's own comparison notes Copilot 'has no native support for record retrieval in Databricks, Workday, or BigQuery.'

_Source:_ Medium 'RAG in Microsoft 365 Copilot' (medium.com/@praneetsy/...); Glean 'Glean vs Microsoft 365 Copilot' comparison (glean.com/compare/glean-vs-copilot)

**How we address it:** Our core mechanic is computing over the data: the agent calls generic tools (describe / group_by / join_diff / filter_count) over any CSV so code does the math. That lets us adjudicate documented-process-vs-actual-data contradictions and quantify control/ownership gaps - the quantitative reasoning retrieval copilots cannot do.

### No carve-out / TSA-exit specificity: a typical IT TSA exit needs 1,500+ interdependent design decisions across ~8 workstreams, yet there is no broadly recognized specialized tooling - it is consulting-and-spreadsheets heavy, and early exit is worth ~5-7% deal value uplift.

_Evidence:_ M&A Leadership Council, Umbrex carve-out playbook, and Deloitte 'Art of Speed' describe the 1,500+ interdependent decisions and workstream load; PwC quantifies 5-7% value uplift from expedited TSA exits; coverage notes only point tools (e.g., Archon for SAP) with no broad rationalization tooling.

_Source:_ M&A Leadership Council 'Structuring and Management of TSAs in Carve-Outs' (macouncil.org); Umbrex 'Exit Strategy and TSA Sunset Provisions' (umbrex.com); Deloitte 'The Art of Speed' (deloitte.com/ch); PwC 'How expediting TSA exits can unlock deal value' (pwc.com/us)

**How we address it:** We are explicitly positioned for post-carve-out / TSA-exit application and process rationalization, running on the messy heterogeneous docs these programs actually have (often no clean event logs), with zero config. We surface undocumented/unowned processes and control gaps and produce the 6-report transformation suite that informs the rationalization and exit-sequencing decisions.

### Proprietary closed architecture and vendor lock-in (Palantir): ontologies live in Palantir's own object framework, binding customers to the ecosystem and sacrificing flexibility/openness and access to their own semantic models; engineers 'still struggle to explain when Foundry's ontology actually works or is overkill.'

_Evidence:_ Timbr.ai and TowardsAI/Medium analyses describe Foundry's ontology as 'proprietary and closed by design,' creating dependencies that 'bind customers to the Palantir ecosystem,' with a March 2026 piece noting engineers can't articulate when it's the right choice vs overkill.

_Source:_ Timbr.ai / Medium 'Closed or Open Architectured Ontologies' (medium.com/timbr-ai/...); 'Palantir Foundry Ontology... Where It Falls Short' (pub.towardsai.net)

**How we address it:** We do not require committing the enterprise's knowledge into a proprietary ontology platform to get value. We run on the client's existing documents and CSVs as a discovery accelerator and emit standard consulting reports/artefacts, so the engagement is not a multi-year platform lock-in.

### Manual data upkeep / staleness and rollout fragility: Glean users want an easy way to flag deprecated/outdated content, hit VPN slowdowns and still-evolving integrations; Copilot deployments show inconsistent usage, 'operational fragility,' and unclear ROI with declining primary-tool share.

_Evidence:_ G2 Glean reviews cite the desire to flag outdated content, VPN response slowdowns, and 'integrations still evolving / not fully seamless'; Windows Forum reports Copilot 'operational fragility, inconsistent outputs, and unclear ROI' and declining primary-tool share.

_Source:_ G2 Glean Reviews 2026 (g2.com/products/glean-technologies-glean/reviews); Windows Forum 'Microsoft Copilot Under Strain: Enterprise ROI and Reliability' (windowsforum.com)

**How we address it:** We run as a point-in-time discovery over the documents supplied for an engagement, so there is no always-on connector graph to keep continuously fresh or manually de-duplicate. The deliverable is grounded in the snapshot analyzed, with provenance, rather than depending on a live index that drifts stale.

### Slow initial scanning and scale limits in data-intelligence tools (Cyera DSPM): largest enterprises report a 50-scan/day cap for global deployments, slow first scans, and one customer faced a 2+ month estimate for a first comprehensive scan; industry-wide DSPM false positives drive alert fatigue.

_Evidence:_ Gartner Peer Insights and CheckThat.ai reviews note the 50-scan/day limit, slow initial scanning, and a 2+ month first-scan estimate at one large enterprise; Cyera's own blog acknowledges classification maintenance and false-positive/alert-fatigue challenges across DSPM.

_Source:_ Gartner Peer Insights Cyera Platform reviews (gartner.com/reviews/market/data-security-posture-management/vendor/cyera); CheckThat.ai 'Cyera Reviews 2026' (checkthat.ai/brands/cyera/reviews); Cyera 'Common DSPM Implementation Challenges' (cyera.com/blog/common-dspm-implementation-challenges)

**How we address it:** Adjacent rather than head-to-head (DSPM classifies where sensitive data lives; we rationalize business process), but where it overlaps we avoid the boil-the-ocean full-estate scan: we scope to a business domain's document set (e.g., Order-to-Cash) and produce reasoned findings with confidence/provenance instead of a large flat classified inventory that generates alert fatigue.

### Format/document-variation brittleness: Hebbia Matrix pulls the wrong data when a document's form varies over time even if the topic is identical, forcing users to audit outputs and carefully craft prompts; limited customization, no chat history, no Word/PDF export.

_Evidence:_ eesel AI / opentools.ai note that 'variations in form can cause the wrong data to be pulled,' plus limited customization, no chat history, and inability to export to Word or PDF.

_Source:_ eesel AI Hebbia review (eesel.ai/blog/hebbia-ai-review); opentools.ai Hebbia (opentools.ai/tools/hebbia)

**How we address it:** We are built for heterogeneous, inconsistent enterprise docs by design and compute over them with generic tools rather than relying on a fixed template match, and we produce a structured 6-report client suite (an actual consulting deliverable) rather than ephemeral chat answers, addressing both the brittleness and the export/output-format gap.

### No tool/RAG jargon abstraction and limited fine-tuning of relevance: Glean results can be 'too broad' or irrelevant, with limited ability to fine-tune relevance for specific teams/use cases and an occasionally unintuitive UI.

_Evidence:_ G2 reviews report results 'occasionally include irrelevant information,' 'too broad,' 'limitations in fine-tuning search results, filters, or relevance behavior for specific teams,' and complaints that the UI is 'unintuitive.'

_Source:_ G2 Glean Reviews 2026 (g2.com/products/glean-technologies-glean/reviews); SelectHub Glean reviews (selecthub.com/p/knowledge-management-software/glean-com)

**How we address it:** Our output is a client-ready report suite with no tool jargon - the reasoning is packaged into Current State, Pain Points, Transformation Recommendation (value-feasibility matrix), AI Opportunity Portfolio (before/after), Roadmap, and Supporting Artefacts - so consumers get domain-specific, decision-grade narrative rather than a generic search surface they must tune and filter themselves.
