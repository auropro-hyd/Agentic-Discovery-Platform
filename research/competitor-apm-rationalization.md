# Competitor Dossier — apm-rationalization (Application Portfolio Management / Rationalization & Enterprise Architecture tools)

_Market research generated 2026-06-02 via a multi-agent web-research workflow (11 agents, deep web search + analyst/review mining). Cited throughout. This is a standing reference — read it instead of re-searching._


## Category summary

This category covers Enterprise Architecture (EA) / Application Portfolio Management (APM) platforms that build a repository ("single source of truth") of an enterprise's applications, business capabilities, technologies, and dependencies, then support rationalization decisions — typically via the Gartner TIME framework (Tolerate, Invest, Migrate, Eliminate) and/or the US CIO Council Application Rationalization Playbook. Across all vendors the core architecture is the same: (1) populate a structured data model (fact sheets / CMDB CIs / metamodel objects), (2) score each app on functional fit, technical fit, business value, cost, risk, and lifecycle, (3) map redundancy against a business-capability map to find overlaps, and (4) produce TIME quadrant views, roadmaps, and cost-saving estimates.

DATA SOURCING is the central dividing line and the category's biggest weakness. Two patterns dominate: (a) SURVEY/QUESTIONNAIRE-DRIVEN (LeanIX, Ardoq, Bizzdesign/Alfabet, MEGA HOPEX) — app owners and SMEs fill in customizable surveys/assessments to provide fit, value, and cost data; (b) AUTOMATED DISCOVERY-DRIVEN (ServiceNow APM via CMDB + Discovery + Service Mapping; Apptio via general-ledger/financial integration). Most enterprise deployments are hybrid: discovery/finance integrations populate the inventory and cost, but the qualitative scoring (functional fit, business criticality, "is this documented/owned?") still relies on human surveys. This is the well-documented pain point — Gartner and practitioner sources note that APM initiatives stall on data gathering, survey fatigue, and the fact that assessment scores do not populate until app owners complete 100% of indicators; only ~25% of leaders consider EA effective.

PRICING: Universally quote-on-request and enterprise-anchored. Dominant model is per-application-per-year (LeanIX, Ardoq) or per-fulfiller-seat + module (ServiceNow), with multi-year contracts and large implementation services attached. Realistic ranges: EA pilots $5-15K/yr; mid-market 200-500 apps $50-200K/yr; large enterprise 1,000+ apps $250-750K/yr; plus $30-100K+ implementation. These are platform/license costs, not consulting deliverables.

GENAI ADDITIONS (2025-2026): Every vendor has bolted on GenAI, but almost entirely as PRODUCTIVITY/AUTHORING copilots inside the tool, NOT autonomous discovery of findings. SAP LeanIX has Joule (conversational search/navigation, "suggest 5 replacements for this app") plus an AI Agent Hub (GA Q4 2025) to inventory/govern AI agents as a new asset class. MEGA HOPEX "Aquila" goes furthest with AI-driven automatic software-product discovery, intelligent application detection, automatic capability mapping, and rationalization/cloud-migration recommendations (uses a GPT-3.5-turbo model on Azure). Bizzdesign has diagram generators, a natural-language analyzer, a "How-to Coach" chatbot, and an ArchiMate Relation Recommender. Ardoq and Apptio add AI assistants/recommendations layered on their existing data. None of them autonomously ingest raw heterogeneous business documents (SOPs, RACIs, working notes) and COMPUTE over system CSVs to surface contradictions between documented process and actual data with provenance — they assume a curated, structured repository already exists.

Consolidation note: Bizzdesign acquired Alfabet from Software AG (carve-out, combined ~2,000 customers / ~€110M revenue), so "Software AG Alfabet" and "Bizzdesign HoriZZon" are now one vendor with two product lines; "MEGA HOPEX" is independent. All are positioned as ongoing-governance SaaS platforms (a continuous EA practice), which is a different buy than a one-time consulting-led discovery engagement.

## Vendors

### SAP LeanIX (Application Portfolio Management / Application Rationalization)

**What it does:** SaaS EA platform giving a 360-degree view of applications, business capabilities, and IT components via 'fact sheets'; supports data-driven application rationalization using predefined reports, TCO/usage, lifecycle, and the Gartner TIME framework to categorize each app (Tolerate/Invest/Migrate/Eliminate).

**Approach:** Repository + fact-sheet model. Scope apps with filters and surveys, evaluate via TIME with automated recalculation, build a roadmap, track via dashboards. Now tightly woven into the broader SAP ecosystem (S/4HANA transformation, SAP Signavio process intelligence).

**Inputs required:** Customizable surveys to gather app details and cost from responsible owners; out-of-the-box integrations to import inventory and cost data from cost-management/ITSM tools; manual fact-sheet curation. Assumes a structured EA inventory is being maintained.

**Pricing:** Quote-only, priced per application per year (also a fact-sheet-based model). Reported real-world: ~$50K/yr small, ~$91K/yr for ~300 apps, $200K+/yr enterprise-wide; implementation $30-100K. Minimum 3-year contract, annual billing.

**Differentiator:** Deepest integration into the SAP estate plus the new AI Agent Hub (GA Q4 2025) that inventories and governs AI agents as a first-class asset class; Joule copilot for conversational search (claims up to 50% faster doc search, 75% faster time-to-productivity).

**Sources:**
- https://www.leanix.net/en/use-cases/application-rationalization
- https://www.leanix.net/en/products/application-portfolio-management
- https://help.sap.com/docs/leanix/ea/application-rationalization
- https://www.leanix.net/en/blog/sap-leanix-announces-launch-of-ai-agent-hub-and-key-industry-partnerships
- https://archiet.com/vs/leanix
- https://www.spendflo.com/blog/leanix-pricing-and-features

### ServiceNow APM / Enterprise Architecture (CMDB + Discovery + Service Mapping)

**What it does:** Part of ServiceNow's Strategic Portfolio Management (SPM) suite. Builds an inventory of business applications and offers four analysis lenses: Business Capability Planning, Application Migration & Rationalization, Technology Risk Management, and Information Usage; identifies redundancies to cut budget.

**Approach:** Most automation-forward in the category: leans on CMDB, Discovery, Service Mapping, Software Asset Management and cost modeling to auto-populate the application inventory and map hardware/software to application services. Qualitative scoring still done via assessments/surveys assigned to the IT Application Owner / portfolio manager.

**Inputs required:** Requires the ServiceNow platform and ideally implemented Discovery + Service Mapping + SAM to auto-map CIs to app services; assessment surveys for fit/value scoring (scores do not populate until 100% of indicators complete); integrates with Apptio for TCO.

**Pricing:** Quote-only, per-fulfiller-seat + module model. Third-party estimates: ITSM fulfiller ~$100-200/user/month; ITOM/premium ~$150-250; Now Assist AI add-on ~$25-75/fulfiller/month. APM/SPM and ITOM are separate subscription lines, so total enterprise cost is large and stacked.

**Differentiator:** Automated, discovery-sourced inventory and the deepest operational tie-in (ITSM/ITOM/ITAM/CMDB incidents, usage, lifecycle risk feed rationalization scores in near real time) — strongest when the customer already runs ServiceNow as their system of record.

**Sources:**
- https://www.servicenow.com/products/application-portfolio-management.html
- https://www.servicenow.com/content/dam/servicenow-assets/public/en-us/doc-type/resource-center/data-sheet/ds-application-portfolio-management.pdf
- https://blog.snowycode.com/post/apm-exam-study-guide-for-servicenow-developers
- https://servicenowguru.com/service-now-miscellaneous/application-portfolio-management-apm-assessment-challenges/
- https://redresscompliance.com/servicenow-pricing
- https://www.eesel.ai/blog/servicenow-pricing

### IBM Apptio (Application TCO / TBM-driven rationalization)

**What it does:** Technology Business Management (TBM) / IT financial management platform. Application rationalization is delivered via Apptio Costing: segment apps by revenue-driver / revenue-supporter / KTLO, compute defensible Application TCO, and decide keep/cut per segment to shrink the portfolio and remove duplicate business capabilities.

**Approach:** Financial-data-driven, not survey-driven. Builds a single source of truth from general-ledger and operational data, mapped to the TBM Council ATUM taxonomy; breaks Application TCO down by vendor, labor, and direct/indirect cost. Sold jointly with ServiceNow EA, feeding cost as one rationalization indicator alongside CSAT, lifecycle risk, technical debt, incidents, usage.

**Inputs required:** Financial source data (general ledger, vendor/contract spend, labor/cost-center allocations), CMDB/CSDM mapping (often via ServiceNow), and the ATUM/TBM cost model. Not a documents-in / capability-map-out tool.

**Pricing:** Quote-only; subscription based on contract duration/terms; sold via direct + AWS Marketplace (IBM Apptio Costing Standard / Costing & Planning). Enterprise-scale TBM deployments typically six figures annually; exact figures not public.

**Differentiator:** Best-in-class defensible cost transparency and unit economics — the authoritative 'what does this app actually cost' number that the EA tools depend on. Strongest on the financial/CFO side of rationalization rather than the architecture side.

**Sources:**
- https://www.apptio.com/products/ibm-apptio/costing/
- https://www.apptio.com/blog/apptio-servicenow-launch-new-application-portfolio-management-capabilities/
- https://www.ibm.com/products/apptio
- https://www.praecipio.com/resources/articles/how-to-implement-tbm-with-apptio
- https://aws.amazon.com/marketplace/pp/prodview-mdyxbluvzbcn4

### Ardoq

**What it does:** Data-driven EA platform with an out-of-the-box Application Rationalization solution to continuously decide keep/replace/retire/merge based on business value, functional fit, technical fit, purchase price, and TCO; follows the CIO Application Rationalization Playbook aligned to Gartner TIME.

**Approach:** Graph/metamodel-based, 'living' continuous rationalization rather than one-off projects; emphasizes dynamic, query-driven views and surveys to keep data fresh. Quick Start package targets fast app-rat setup; full platform for broader EA.

**Inputs required:** Surveys/broadcasts to app owners for scoring, integrations to import app/cost data, and metamodel population. Customer case: rationalized 30 apps, ~$800K/yr saved, 6-9 months faster time-to-insight.

**Pricing:** Quote-only, priced per application managed (NOT per user — unlimited users included), modular add-ons at fixed + per-app prices. Article benchmarks (Ardoq's own): pilot $5-15K/yr, 200-500 apps $50-200K/yr, 1,000+ apps $250-750K/yr.

**Differentiator:** Unlimited-users, per-application pricing and a graph-based 'continuous' model that scales with landscape complexity rather than headcount; positions itself for broad stakeholder participation in always-on rationalization.

**Sources:**
- https://www.ardoq.com/solutions/application-rationalization
- https://help.ardoq.com/en/articles/44015-getting-started-with-application-rationalization
- https://www.ardoq.com/plans
- https://www.ardoq.com/blog/enterprise-architecture-cost-in-2025

### Bizzdesign HoriZZon (incl. Alfabet, ex-Software AG)

**What it does:** End-to-end EA + Strategic Portfolio Management SaaS suite uniting strategy, architecture, and governance; ArchiMate-based modeling plus APM/rationalization. Alfabet (acquired from Software AG) adds deep IT planning/portfolio management, M&A due-diligence, GDPR/IT governance, and a US-Government Application Rationalization Accelerator aligned to the CIO Council Playbook.

**Approach:** Model-driven (ArchiMate) EA repository with portfolio scoring, scenario/roadmap modeling, and rationalization workflows. Strong on rigorous architecture modeling and governance; named a Leader in the 2025 Gartner Magic Quadrant for EA Tools.

**Inputs required:** Surveys/data capture from app owners, ArchiMate model curation, and integrations; assumes a maintained architecture repository. Alfabet's APM user journey is capture-then-assess.

**Pricing:** Quote-only, enterprise SaaS; combined Bizzdesign+Alfabet group ~2,000 customers, ~€110M revenue. Specific list pricing not public; sits in the same $50K-$750K/yr enterprise band per app count and modules.

**Differentiator:** Deepest formal modeling rigor (ArchiMate) + breadth across EA and SPM, plus a preconfigured CIO-Playbook accelerator for government/regulated rationalization; 2025-26 AI roadmap centers on diagram generation, NL analysis, relation recommender, and predictive scenario modeling.

**Sources:**
- https://bizzdesign.com/
- https://www.alfabet.com/resources/articles/application-rationalization
- https://bizzdesign.com/guides/us-government-application-rationalization
- https://www.mcdermottlaw.com/media/mcdermott-advises-main-capital-and-bizzdesign-on-the-acquisition-of-alfabet/
- https://bizzdesign.com/blog/future-enterprise-architecture-and-ai-integration
- https://www.gartner.com/reviews/market/enterprise-architecture-tools/vendor/bizzdesign/product/horizzon

### MEGA HOPEX (IT Portfolio Management / AI-driven APM, 'HOPEX Aquila')

**What it does:** Unified HOPEX platform connecting business, IT, data, and risk in one repository; HOPEX IT Portfolio Management optimizes apps for cost, lifecycle, and agility, standardizes the tech portfolio, and mitigates obsolescence risk. Aquila release adds an AI-driven APM module.

**Approach:** Repository + smart-analysis model. HOPEX Aquila is the most aggressive GenAI play in the category: automatic software-product discovery, intelligent application detection, automatic capability mapping, and automatic IT-rationalization / cloud-migration recommendations, plus a HOPEX AI Assistant (GPT-3.5-turbo on Azure).

**Inputs required:** Repository population (discovery + import), surveys/assessments for qualitative scoring, and HOPEX modeling. Aquila reduces some manual capability-mapping effort via AI but still operates within a structured HOPEX repository.

**Pricing:** Quote-only enterprise SaaS/on-prem; not publicly listed. Comparable enterprise EA band ($50K-$750K/yr by scope/modules).

**Differentiator:** Most built-out AI-automation feature set for the actual rationalization workflow (auto product discovery + auto capability mapping + auto rationalization/cloud recommendations) within a governance-grade GRC/EA platform.

**Sources:**
- https://www.securityinfowatch.com/cybersecurity/press-release/53075022/mega-international-announces-release-of-hopex-aquila
- https://www2.mega.com/en/uk/lp/wp/application-portfolio-management-improve-application-rationalisation
- https://community.mega.com/t5/Hopex-IT-Portfolio-Management/ct-p/hopex-training-itpm
- https://www.gartner.com/reviews/market/application-portfolio-management-tools

## Where they beat us (be honest)

1) PERSISTENT SYSTEM OF RECORD / ONGOING GOVERNANCE: All six maintain a live, queryable repository (fact sheets / CMDB / ArchiMate models) that stays current and supports continuous governance, lifecycle tracking, and roadmap management long after a project ends. Our platform is a consulting-led discovery accelerator producing a point-in-time 6-report suite — it does not give the client a standing EA tool, dashboards they log into daily, or audit-trailed change management of the portfolio over years.

2) AUTOMATED TECHNICAL INVENTORY & DEPENDENCY MAPPING AT SCALE: ServiceNow (Discovery + Service Mapping + CMDB) and MEGA Aquila (automatic software-product discovery + capability mapping) can auto-discover what is actually deployed across the estate — network/agent-based detection of running software and runtime dependencies. Our agent reasons over the documents and CSVs the client gives us; it does not crawl the live network to discover undocumented running software, so for the raw "what technology exists and how is it wired" inventory, discovery-based tools are more complete.

3) DEFENSIBLE FINANCIALS / TCO: Apptio (and LeanIX/ServiceNow cost integrations) tie rationalization to general-ledger-grounded, ATUM/TBM-standardized Application TCO that CFOs accept. Unless the client's cost data is in our ingested files, we cannot match that depth of audited financial allocation.

4) ECOSYSTEM LOCK-IN & ANALYST VALIDATION: SAP (S/4HANA, Joule, Agent Hub), ServiceNow (Now Platform), and IBM are incumbent enterprise standards with Gartner MQ Leader positioning, reference customers, security/compliance certifications, and procurement familiarity. A new accelerator faces 'why not just use the platform we already own' and trust/credibility hurdles in large procurement.

5) MATURE INTEGRATION CATALOGS & MULTI-USER COLLABORATION: Out-of-the-box connectors to ITSM, cost tools, SAM, HR, etc., plus role-based collaboration, survey workflow, and assessment campaigns for hundreds of app owners — institutionalized data-collection machinery we do not replicate.

6) SCALE OF THE LANDSCAPE VIEW: They are built to hold and visualize 1,000s of apps with business-capability heatmaps and portfolio quadrants as a durable artifact; we produce reports scoped to a domain's documents per engagement.

## Where we beat them

1) AUTONOMOUS DISCOVERY OF FINDINGS vs. SURVEY-FED SCORING: This is the core wedge. Every incumbent fundamentally REQUIRES humans to populate and score the model — customizable surveys to app owners (LeanIX, Ardoq, Bizzdesign), assessments that 'do not populate until 100% of indicators are complete' (ServiceNow), or financial allocations (Apptio). Their #1 documented failure mode is data-gathering stall, survey fatigue, and bad data quality (Gartner: only ~25% think EA is effective; data availability/quality is the top barrier). We invert this: the agent INGESTS the heterogeneous documents that already exist (SOPs, policies, RACIs, system CSVs, working notes) and AUTONOMOUSLY discovers findings by computing over the data — no questionnaire campaign required to get to insight.

2) CONTRADICTION DETECTION BETWEEN DOCUMENTED PROCESS AND ACTUAL SYSTEM DATA: Incumbents score apps; they do not compute whether the documented SOP/policy contradicts what the system export actually shows, nor surface undocumented/unowned processes or control gaps. Our agent calls generic tools (describe / group_by / join_diff / filter_count) over any CSV so code does the math and the agent reasons — producing process-vs-reality contradiction findings that an APM repository structurally cannot generate.

3) CONSISTENT-NOT-FABRICATED, GROUNDED NUMBERS: Every number traces to the source data and is verified by a grounding gate, with confidence + provenance on each finding. The incumbents' new GenAI is mostly productivity copilots (Joule conversational search, diagram generators, How-to chatbots) layered over a human-curated repo — they inherit whatever (often stale/incomplete) data the surveys produced, and their LLM features (e.g., HOPEX on GPT-3.5-turbo) risk ungrounded suggestions. Our grounding gate is a structural anti-hallucination guarantee they do not offer.

4) ZERO-CONFIG, ANY-DOMAIN, PROCESS-LEVEL: We run on ANY business domain's documents (Order-to-Cash, Procure-to-Pay, etc.) with zero config and operate at the PROCESS level (contradictions, ownership gaps, control gaps), not just the application-inventory level. APM tools require metamodel setup, capability-map definition, and connector configuration before producing value.

5) FIT FOR CARVE-OUT / TSA-EXIT SPEED: Post-carve-out / TSA-exit work is exactly where the structured repository does NOT yet exist and time is short — you have a pile of inherited docs and system exports and must rationalize fast before TSA charges expire. Standing up LeanIX/ServiceNow/HOPEX and running survey campaigns is too slow and assumes a clean inventory. Our accelerator produces the Current State, Pain Points, Transformation Recommendation (value-feasibility matrix), AI Opportunity Portfolio (before/after), Roadmap, and Supporting Artefacts directly from the inherited material, human-SME-in-the-loop.

6) CLIENT-READY OUTPUT, NO TOOL JARGON: We emit a consultant-grade 6-report client suite with no tool jargon, suited to a consulting-led engagement deliverable. The incumbents output dashboards/quadrants for an internal EA practice to interpret — not a board-ready transformation narrative.

7) COMMERCIAL MODEL: Delivered as a consulting accelerator, not a multi-year per-app/per-seat SaaS subscription ($50K-$750K/yr + $30-100K implementation + 3-year lock-in). For a discrete discovery/rationalization engagement, we avoid the platform license, the implementation project, and the lock-in.

## Documented weaknesses / complaints (and how we address them)

### APM/EA initiatives stall on data gathering, survey fatigue, and incomplete app-owner input. Assessment scores don't populate until owners complete 100% of indicators; info lives in stale spreadsheets or 'between the ears of application owners,' so teams analyze incomplete/inaccurate data and key insights get missed. This affects all survey-driven vendors (LeanIX, Ardoq, Bizzdesign/Alfabet, MEGA HOPEX).

_Evidence:_ Ardoq's own guidance: APM info is 'scattered across the organization—stored in Excel spreadsheets that are almost instantly out-of-date, or kept between the ears of application owners... teams are left to analyze incomplete information.' Gartner TIME assessments depend on 'surveys of business and IT owners' where data 'is often incomplete or inaccurate.' When APM delivers little actionable insight, the practice is not maintained.

_Source:_ https://www.ardoq.com/blog/successful-application-portfolio-assessment ; https://www.valueblue.com/knowledge-base/guides/why-a-traditional-application-portfolio-management-solution-is-no-longer-enough ; https://www.mobs-bd.org/gartner-time-model-effective-application-portfolio-management/

**How we address it:** Directly resolves the central category weakness. Our agent ingests the heterogeneous documents that DO exist (SOPs, policies, RACIs, system CSV exports, working notes) and AUTONOMOUSLY computes findings over them rather than waiting for app owners to complete surveys. There is no questionnaire to fatigue out on and no '100% of indicators before scores populate' gate. SME involvement is human-in-the-loop validation of discovered findings, not the data-entry bottleneck itself.

### Data must be continuously maintained by hand or it rots; without clear ownership the repository quickly goes inconsistent and stale. This is the recurring LeanIX dislike and a general EA failing (only ~25% of leaders consider EA effective).

_Evidence:_ LeanIX Gartner Peer Insights reviewers cite the main challenge as 'keeping the data complete and up to date, requiring continuous effort, and without clear ownership it can quickly become inconsistent,' and note 'dependencies from data quality where sources must be maintained continuously.' Apptio reviewers say 'initial implementation and data tagging were manual and time-consuming.'

_Source:_ https://www.gartner.com/reviews/product/leanix-enterprise-architecture ; https://community.leanix.net/the-americas-47/navigating-data-quality-challenges-in-leanix-726 ; https://www.apptio.com/topics/application-rationalization/

**How we address it:** We are a one-time, consulting-led discovery accelerator, not a repository that must be perpetually fed. The agent computes findings from a point-in-time document/data drop with zero config and zero ongoing manual upkeep. There is no metamodel to govern, no fact sheets to keep fresh, no survey to re-run each quarter — the deliverable is the 6-report suite, not a living data model the client must staff to maintain.

### Automated-discovery-driven tools (ServiceNow APM via CMDB, Apptio via GL) require clean structured source data to be useful — and that data is usually NOT clean. CMDB accuracy hovers ~60%, only ~25% of enterprises get meaningful value, and <half trust their CMDB/CSDM data; manual updates are slow, inconsistent, error-prone.

_Evidence:_ 'CMDB accuracy typically hovers around 60%, and according to Gartner, only 25% of enterprises receive meaningful value from their CMDBs.' Forrester: 'less than half report trusting the data in their CMDB and CSDM.' Implementations spend '12 to 18 months cleaning up data quality problems.' Process-mining peers (Celonis) need 'Case ID, Activity, Timestamp' event logs and 'low-quality event logs... lead to complex, unstructured models that are difficult to interpret.'

_Source:_ https://onlyflows.tech/blog/why-your-servicenow-cmdb-data-quality-initiatives-keep-failing-and-how-to-fix-them ; https://www.oomnitza.com/blog/servicenow-cmdb-data-accuracy-boost-roi/ ; https://www.mdpi.com/2076-3417/11/22/10556

**How we address it:** We do not depend on a pre-built clean CMDB or formal event logs. The agent works over whatever heterogeneous CSV/system exports and documents the enterprise actually has, using generic tools (describe/group_by/join_diff/filter_count). In fact, contradictions between messy documented process and messy actual data ARE our findings — data inconsistency is the signal we surface, not a prerequisite we demand the client fix first.

### No understanding of unstructured business documents. Every vendor assumes a curated, structured repository (fact sheets / CMDB CIs / metamodel objects) already exists. None ingests raw SOPs, policies, RACIs, and working notes to find where documented process contradicts actual system data.

_Evidence:_ Across the dossier vendors, GenAI is bolted on as authoring/search copilots over the EXISTING structured model (LeanIX Joule conversational search; Bizzdesign diagram generators / ArchiMate Relation Recommender; MEGA HOPEX Aquila auto-detects software products but operates within HOPEX's structured metamodel). Process-mining sources confirm 'some process steps don't take place in a transactional system, such as sending an email or opening a spreadsheet,' i.e. the unstructured/off-system reality is a blind spot.

_Source:_ https://www.celonis.com/insights/topics/how-does-process-mining-work ; https://www.leanix.net/en/products/application-portfolio-management ; https://bizzdesign.com/blog/what-is-application-portfolio-management-amp

**How we address it:** This is our core differentiator. The platform's primary input IS the unstructured/semi-structured corpus (SOPs, policies, RACIs, working notes) joined against system CSVs. It autonomously discovers undocumented/unowned processes and contradictions between what the docs SAY and what the data SHOWS — a class of finding the structured-repository vendors architecturally cannot produce because they never read the source documents.

### GenAI copilots are black-box and lack provenance/citation, undermining the traceability needed for architectural governance, and risk hallucinated/fabricated outputs (3-15% hallucination rates). Regulators now expect explainability, provenance and lineage as evidence.

_Evidence:_ Systematic literature review: GenAI systems are 'black boxes whose internal reasoning processes are inaccessible, which can undermine the transparency, interpretability, and traceability required for sound architectural governance,' with 'low output reliability, often stemming from hallucinations.' Hallucination rates 3-15% (Stanford AI Index 2025). 'Models should not merely generate answers, they should generate claims with provenance, each claim attached to a traceable source or an explicit uncertainty label.' MEGA HOPEX Aquila reportedly uses a GPT-3.5-turbo model with no provenance layer described.

_Source:_ https://arxiv.org/html/2510.22003v1 ; https://medium.com/@markus_brinsa/hallucination-rates-in-2025-accuracy-refusal-and-liability-aa0032019ca1

**How we address it:** We are built exactly to this emerging standard. Every number traces back to the source data, enforced by a grounding gate (consistent-not-fabricated), and findings carry confidence and provenance. Code does the math (deterministic tool calls over CSVs); the LLM does only the reasoning over verified figures — so outputs are auditable claims-with-sources, not a black-box generative answer.

### Outputs are tool-centric and not consumable by senior executives. Visualizations/standard views aren't suited to leadership presentations and users export data to build their own reports.

_Evidence:_ Ardoq Gartner Peer Insights: 'visualizations are not ideal for senior level presentations' and 'difficult getting engagement with the tool beyond EA.' LeanIX reviewers: 'the standard views are sometimes not enough, so users occasionally export data for further analysis.' MEGA HOPEX: 'the tool needs to have a viewer portal. Currently, we have to use a custom solution to display information.'

_Source:_ https://www.gartner.com/reviews/market/enterprise-architecture-tools/vendor/ardoq/product/ardoq ; https://www.gartner.com/reviews/product/leanix-enterprise-architecture ; https://www.peerspot.com/products/mega-hopex-pros-and-cons

**How we address it:** The deliverable is a client-ready 6-report suite (Current State, Pain Points, Transformation Recommendation with value-feasibility matrix, AI Opportunity Portfolio with before/after, Roadmap, Supporting Artefacts) written in business language with NO tool jargon. The output is the executive narrative consultants would otherwise hand-build, not a set of EA dashboards a partner can't put in front of a CFO.

### Steep learning curve and heavy training requirement. Tools are powerful but require extensive hands-on training before anyone is productive — a barrier especially for one-off engagements.

_Evidence:_ Bizzdesign HoriZZon: 'the learning curve is steep, requiring 500 to 1,000 hours to master, making it difficult for casual users and most architects.' MEGA HOPEX: 'high learning curve,' users 'spend 40% of the time thinking about how they would implement and use the MEGA concept'; 'training materials and learning process need improvement.' Ardoq: 'significant learning curve beyond initial onboarding.' LeanIX G2: 'steep learning curve... not very intuitive as a first-time user, requiring hands-on training.'

_Source:_ https://www.peerspot.com/products/bizzdesign-horizzon-pros-and-cons ; https://www.peerspot.com/products/mega-hopex-pros-and-cons ; https://www.g2.com/products/sap-leanix/reviews

**How we address it:** Runs on any domain's docs with zero config and is operated by the consulting team delivering the engagement, not by client staff who must first be trained on a metamodel. There is no client-side platform to learn — clients receive reports, not a tool to master. This removes the multi-hundred-hour ramp that makes incumbent tools impractical for a time-boxed discovery.

### Long, expensive implementation and slow time-to-value. Setup/configuration/data-prep can take up to a year (HOPEX) and value realization 6-24 months (LeanIX); vendors push clients toward paid professional services.

_Evidence:_ MEGA HOPEX: 'with configuration, customizing, and data preparation, implementation took about one year to set up'; 'the company tends to push people toward professional services.' LeanIX: benefits 'realized in 6-24 months'; reviewers note organizational adoption takes 'a considerable period.' ServiceNow: teams spend '12 to 18 months cleaning up data quality.'

_Source:_ https://www.peerspot.com/products/mega-hopex-pros-and-cons ; https://www.peerspot.com/products/leanix-pros-and-cons ; https://onlyflows.tech/blog/why-your-servicenow-cmdb-data-quality-initiatives-keep-failing-and-how-to-fix-them

**How we address it:** Delivered as a consulting accelerator that produces findings from a point-in-time document/data ingest — measured in the timeframe of a discovery engagement, not 6-24 months of platform stand-up and data prep. Zero config means no metamodel build, no survey rollout, no integration project before the first finding appears.

### High, enterprise-anchored, license-based cost — per-application-per-year or per-fulfiller-seat plus modules and large implementation fees. Pricing dismisses smaller scopes and inflates via seat misclassification and AI tier upgrades.

_Evidence:_ MEGA HOPEX: 'very expensive... small organizations dismiss the tool.' ServiceNow fulfiller seats $70-200/user/month; 'misclassifying users as fulfillers is the most common and most expensive licensing error'; Now Assist AI requires upgrading every fulfiller to Pro Plus — 'in a 500-fulfiller environment, the tier upgrade alone costs $240,000 to $420,000 per year before the AI capability is even switched on.' Bizzdesign: 'cost and licensing model limits wider adoption.'

_Source:_ https://www.peerspot.com/products/mega-hopex-pros-and-cons ; https://redresscompliance.com/servicenow-pricing ; https://www.gartner.com/reviews/product/bizzdesign-horizzon

**How we address it:** Sold as a consulting deliverable, not a multi-year SaaS license with per-app or per-seat metering. The enterprise does not buy and staff a platform; it buys the discovery outcome. There is no perpetual license, no seat-classification trap, and no GenAI tier-upgrade tax to unlock AI capability — the AI reasoning is the engine, not a premium add-on.

### No carve-out / TSA-exit specificity. EA/APM platforms are positioned as continuous-governance SaaS for an ongoing EA practice — a fundamentally different buy than a one-time, deadline-driven separation/rationalization engagement.

_Evidence:_ All dossier vendors are positioned as ongoing-governance SaaS (a continuous EA practice / 'single source of truth' repository). M&A sources show carve-out/TSA exits are urgent, time-boxed events driven by 'hard sunset dates, fee escalators, and crystal-clear readiness criteria' where the goal is a controlled bridge, not a standing platform; teams need fast application/process rationalization, not a perpetual repository to maintain.

_Source:_ https://umbrex.com/resources/carve-out-playbook/exit-strategy-and-tsa-sunset-provisions/ ; https://www.deloitte.com/ch/en/services/consulting-financial/research/the-art-of-speed.html ; https://www.alvarezandmarsal.com/insights/executing-carve-outs-without-it-tsas-strategic-approach

**How we address it:** Positioned specifically for post-carve-out / TSA-exit application and process rationalization as a consulting-led, one-time engagement. The zero-config, fast, document-driven discovery fits the deadline-pressured separation timeline, where standing up a continuous-governance EA repository is the wrong tool. We produce the rationalization recommendation and roadmap the deal team needs to hit the TSA sunset, then we are done — no platform residue to own.

### Weak data governance/validation inside the tools themselves — they store objects but don't cleanse or validate the data, and integration with surrounding systems is limited.

_Evidence:_ MEGA HOPEX: 'it has a data domain where we load our data objects... but doesn't provide data governance capabilities such as cleansing or validating data'; 'the data layer might be the weakest point.' 'The product must improve integration with other tools' and missing 'ITSM or CMDB' integration. Bizzdesign: limited integration — 'five integration points at a fixed price, but other things come at additional costs.'

_Source:_ https://www.peerspot.com/products/mega-hopex-pros-and-cons ; https://www.gartner.com/reviews/product/bizzdesign-horizzon

**How we address it:** Validation is intrinsic: the grounding gate verifies every reported number against the underlying data before it reaches a report, and contradictions surfaced across documents and CSVs are precisely the cleansing/validation findings these tools fail to produce. Because the agent calls generic compute tools over any CSV, it does not depend on pre-built point-to-point integrations to a specific CMDB or ITSM.
