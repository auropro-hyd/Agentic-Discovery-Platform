# Competitor Dossier — consulting-accelerators

_Market research generated 2026-06-02 via a multi-agent web-research workflow (11 agents, deep web search + analyst/review mining). Cited throughout. This is a standing reference — read it instead of re-searching._


## Category summary

The "consulting discovery accelerator" category is dominated by the Big 4 / Big tech-consulting (Accenture, Deloitte, PwC, Capgemini) and the India-heritage majors (TCS, Infosys, Wipro). Across all of them the dominant model is "methodology + people, accelerated by proprietary IP" rather than a true autonomous-discovery product. Their accelerators (Accenture GenWizard/AI Refinery, Deloitte Ascend + Process Bionics, PwC agent OS + Process Intelligence, Capgemini eAPM/RAISE, Infosys Topaz, TCS MasterCraft, Wipro ai360) are real platforms, but they cluster into three archetypes: (1) AGENT-ORCHESTRATION / DELIVERY platforms (Ascend, agent OS, AI Refinery, GenWizard) that build/deploy AI agents and codify delivery workflows but do NOT autonomously discover findings from a client's raw business docs; (2) PROCESS-MINING platforms (Deloitte Process Bionics, PwC/Capgemini Celonis & Signavio reselling) that require structured event logs/system timestamps and visualize the as-is process — powerful but data-hungry and blind to the gap between what documents SAY and what data DOES; (3) APP-PORTFOLIO assessment tools (Capgemini eAPM, GenWizard rationalization, reverse-engineering modules) that score applications for rationalization using TCO + portfolio characteristics, relevant to carve-out/TSA exit but focused on the IT estate, not the business process narrative.

Three structural facts shape competition. First, these are NOT off-the-shelf products you buy; they are consulting accelerators wrapped inside fixed-fee or team-based engagements. Enterprise AI engagements from Big 4 firms run roughly $500K-$5M (MBB strategy mandates $500K-$1M+), with team bundles of 1+2 to 1+5 consultants, day rates of $300-$500/hr for mid-level and far higher for partners, and a 2025 shift toward outcome-based fees (about 1 in 4 of McKinsey's fees are now outcome-tied). The IP exists primarily to make billable people faster, not to be sold standalone. Second, transparency/auditability is a known soft spot: the 2025 Foundation Model Transparency Index averaged 40/100, and there is a clear enterprise-consulting move toward "grounded" (traceable, provenance-bearing) AI because black-box outputs fail audit and risk requirements — but the big firms wrap this in "Trustworthy AI" / "Responsible AI" governance framing rather than a per-finding data-traceable grounding gate. Third, the heavy ones (Process Bionics, eAPM, Topaz) need structured data (event logs, portfolio inventories, ERP connectors) and configuration/integration to land — they are not "point at a folder of messy SOPs, RACIs and CSVs and get findings" tools.

How a smaller firm competes: not on brand, headcount or breadth of pre-built agents (you will lose all three), but on a sharply different PRODUCT mechanic — autonomous discovery of CONTRADICTIONS between documented process and actual system data, computed by generic tools over any heterogeneous docs with zero config, every number traced to source and gated for grounding, output in client language with confidence/provenance, SME-in-the-loop, on ANY domain. The incumbents' accelerators either need clean structured logs (process mining), or focus on agent deployment / code reverse-engineering / app scoring — none of them is purpose-built to ingest the messy document-plus-CSV reality of a discovery phase and autonomously surface "the SOP says X but the data shows Y, and nobody owns this process." That is the wedge.

## Vendors

### Accenture (GenWizard / AI Refinery / myWizard)

**What it does:** GenWizard is a full-suite generative-AI platform for technology delivery, built on myWizard/myNav/myConcerto, with modules for code reverse-engineering (uses existing application code to auto-generate documentation into a 'living knowledge base'), migration, modernization and enterprise rationalization. AI Refinery is the broader agentic-AI platform (Agents, Knowledge, Models, Governance pillars) and AI Refinery for Industry shipped 12 pre-built industry agent solutions (e.g. Revenue Growth Management, Clinical Trial Companion, Asset Troubleshooting, B2B Marketing). myWizard is the underlying intelligent-automation/IT-ops platform.

**Approach:** Productized platform layered under consulting engagements. GenWizard is genuinely software-heavy (claimed 5-8x faster speed to market, 50-75% IT cost reduction). AI Refinery for Industry is hybrid: pre-built agents + customization with the client's data, deployable on any public/private cloud. Discovery is code/IT-estate-centric (reverse-engineering apps) plus agent deployment, NOT autonomous discovery of contradictions across business documents.

**Inputs required:** Existing application code, institutional knowledge, and connectors to enterprise systems (SAP, Oracle, Salesforce, Workday); AI Refinery agents integrate to real-time data sources (20+ in Accenture's own pilot). Heavily oriented to structured systems and code rather than loose SOPs/policies/RACIs.

**Pricing:** Not disclosed. Delivered inside Accenture consulting/managed-service engagements; built on NVIDIA AI Enterprise (NeMo, NIM, AI Blueprints) for AI Refinery. Effectively priced as part of multi-million-dollar transformation programs, not as a standalone seat.

**Differentiator:** Scale + the world's largest agent/blueprint library + deep NVIDIA/Dell infrastructure partnerships + code-level reverse-engineering for app modernization. Strongest where the job is large-scale IT modernization/rationalization with code as the primary artifact.

**Sources:**
- https://www.accenture.com/us-en/services/cloud/application-transformation/genwizard
- https://www.accenture.com/us-en/services/ai-data/ai-refinery
- https://newsroom.accenture.com/news/2025/accenture-launches-ai-refinery-for-industry-to-reinvent-processes-and-accelerate-agentic-ai-journeys
- https://www.enterpriseitworld.com/accenture-enhances-advanced-data-and-ai-capabilities-of-mywizard/
- https://www.accenture.com/us-en/insights/strategy/seizing-value-from-divestitures

### Deloitte (Ascend + Process Bionics)

**What it does:** Deloitte Ascend is an 'agentic-AI-infused delivery platform' that integrates specialized agents, AI tools and proprietary data into client-project workflows, codifying tested delivery methods (includes AI Assist for SDLC, GenAI Lab, client portal). Process Bionics is Deloitte's process-mining/process-modeling capability (runs on AWS) that discovers, maps and visualizes the as-is process from enterprise-system 'digital footprints' and quantifies bottleneck impact. Deloitte also touts a library of 1000+ pre-built industry-specific AI agents.

**Approach:** Hybrid, leaning methodology+people. Ascend is a single-entry delivery system for Deloitte professionals (accelerates consultants, not a self-serve product). Process Bionics is classic process mining: it needs event logs and timestamps and produces a process map - it does not autonomously reason over messy documents to find contradictions. Governance via Deloitte's 'Trustworthy AI' framework. Also building a dedicated agentic practice on Google Cloud / Gemini Enterprise.

**Inputs required:** Process Bionics requires raw transactional/operational event-log data uploaded (e.g. to S3 -> MSSQL on AWS) - i.e. structured system data with case IDs, activities, timestamps. Ascend taps clients' existing infrastructure plus Deloitte's proprietary assets/templates. Document-centric autonomous discovery is not the design point.

**Pricing:** Not disclosed; delivered within Deloitte consulting engagements (Big 4 enterprise AI engagements broadly $500K-$5M). Tied to advisory/implementation fees, not a product license.

**Differentiator:** Audit/finance/ERP credibility + Process Bionics quantification of process bottlenecks + Trustworthy AI governance framing + 1000+ agent library. Strong for ERP-transformation current-state quantification where clean event logs exist.

**Sources:**
- https://www.deloitte.com/global/en/services/consulting/services/deloitte-ascend.html
- https://www2.deloitte.com/us/en/pages/consulting/articles/process-bionics.html
- https://aws.amazon.com/blogs/industries/process-mining-deloitte-process-bionics-on-aws-achieving-operational-excellence/
- https://www.deloittedigital.com/us/en/accelerators/ai-assist.html
- https://www.googlecloudpresscorner.com/2026-04-22-Deloitte-Accelerates-AI-Transformation-on-Gemini-Enterprise-With-Dedicated-Google-Cloud-Agentic-Transformation-Practice

### PwC (agent OS + Process Intelligence + ChatPwC)

**What it does:** PwC's agent OS is a vendor-agnostic AI-agent orchestration platform that connects and scales agents (including third-party agents) into enterprise workflows with oversight built in (claims up to 10x faster than traditional methods). PwC Process Intelligence delivers process assessments using 100+ metrics with standard outputs to surface high-benefit/low-investment opportunities (largely a Celonis/SAP Signavio-enabled offering). ChatPwC is the internal GenAI tool that accelerates staff.

**Approach:** Methodology+people, accelerated by an orchestration layer. agent OS is about deploying and governing agents, not autonomously discovering findings from raw docs. Process Intelligence is process-mining-driven assessment. PwC is investing in 'reimagining the audit' with AI, reinforcing a grounding/evidence posture, but discovery is metric/event-log-based, not document-contradiction-based.

**Inputs required:** agent OS needs the client's systems/agents to orchestrate. Process Intelligence needs system event data / process logs (Celonis/Signavio-style). ChatPwC operates on internal/curated content. Not designed to ingest a domain's loose SOPs+CSVs and autonomously compute contradictions.

**Pricing:** Not disclosed; delivered through PwC advisory engagements. Big 4 / MBB benchmarks: strategy mandates $500K-$1M+, enterprise AI engagements up to ~$5M; day rates ~$300-$500/hr mid-level, higher for partners.

**Differentiator:** Vendor-agnostic multi-agent orchestration with governance/oversight + audit and risk/controls heritage + 100+ metric process assessment library. Strongest where the client wants to orchestrate many agents across a heterogeneous tool estate under audit-grade oversight.

**Sources:**
- https://www.pwc.com/us/en/services/ai/agent-os.html
- https://www.pwc.com/us/en/about-us/newsroom/press-releases/pwc-launches-ai-agent-operating-system-enterprises.html
- https://www.pwc.com/us/en/technology/alliances/sap-implementation/process-intelligence.html
- https://www.pwc.com/us/en/about-us/newsroom/press-releases/reimagining-audit-with-ai-technology.html
- https://www.pwc.co.uk/services/technology/generative-artificial-intelligence/pwc-accelerated-its-genai-journey-to-help-clients-reach-value-at-speed.html

### Capgemini (eAPM + RAISE + Process Performance)

**What it does:** eAPM (economic Application Portfolio Management) is a proprietary SaaS platform (AI + a catalogue of decision trees) that evaluates an application portfolio using portfolio characteristics + TCO and assigns a rationalization disposition per app, adapted from Gartner's TIME model - directly relevant to carve-out/cloud/transformation roadmaps and target operating model design. RAISE (Reliable AI Solution Engineering) plus the Resonance AI Framework (2025) is Capgemini's GenAI/agentic gallery and scaling framework. Process Performance is its Celonis-partnered process-mining offering.

**Approach:** Mix of a genuine SaaS assessment tool (eAPM) and methodology+people (RAISE/Resonance, process mining). eAPM is the closest big-firm analog to autonomous scoring, but it scores the APPLICATION estate, not business-process contradictions, and is consultant-operated. Process Performance again needs event logs.

**Inputs required:** eAPM requires an application inventory plus cost/TCO data and portfolio characteristics (criticality, stability, obsolescence, spend). Process Performance needs system event data. RAISE works against the client's data/tech ecosystem. Not a zero-config, point-at-the-docs discovery engine.

**Pricing:** Not disclosed; eAPM and RAISE delivered within Capgemini engagements. Comparable Big-firm engagement economics ($500K-$5M range).

**Differentiator:** eAPM's economic/TCO-driven, TIME-model app-rationalization scoring is a mature, directly relevant accelerator for carve-out/TSA-exit IT estate decisions and cloud roadmaps; Resonance/RAISE add a scaling framework + agent gallery.

**Sources:**
- https://www.capgemini.com/be-en/solutions/economic-application-portfolio-management-eapm/
- https://www.capgemini.com/wp-content/uploads/2022/06/2021-eAPM-Brochure-V2.pdf
- https://www.capgemini.com/solutions/raise-reliable-ai-solution-engineering/
- https://www.capgemini.com/news/press-releases/capgemini-unveils-strategic-ai-framework-to-turn-enterprise-ambition-into-measurable-business-impact/
- https://www.capgemini.com/solutions/process-performance/

### TCS / Infosys / Wipro (MasterCraft / Topaz / ai360 + Holmes)

**What it does:** India-heritage majors with proprietary AI IP used to accelerate large delivery/managed-service engagements. Infosys Topaz is a generative+edge-AI services/solutions suite (80+ GenAI client projects; integrates Microsoft intelligence into Topaz Fabric/Cobalt for multi-agent workflows). TCS MasterCraft uses generative AI for automated code synthesis and legacy migration/modernization. Wipro ai360 is a $1B GenAI strategy/platform; Wipro HOLMES is its AI-automation platform spanning cybersecurity, compliance and BPM.

**Approach:** Overwhelmingly methodology+people + delivery-accelerating IP, oriented to modernization, migration, code synthesis and BPM/automation at scale. Microsoft named Cognizant, Infosys, TCS, Wipro as 'Frontier Firms' for Copilot/agentic deployment. Discovery here means code/legacy discovery for migration, not autonomous contradiction-finding across business documents.

**Inputs required:** Primarily codebases, legacy system artifacts and enterprise system connectors (MasterCraft/migration), plus the client's data/process estate for Topaz/ai360 agentic workflows. Not designed for zero-config ingestion of heterogeneous SOPs/policies/RACIs/CSVs to surface process contradictions.

**Pricing:** Not disclosed; bundled into large multi-year delivery/managed-service deals where these majors compete primarily on blended-rate cost and scale rather than premium advisory fees.

**Differentiator:** Lowest-cost-at-scale delivery + very large code-modernization/migration tooling (MasterCraft) + broad agentic platforms (Topaz, ai360) backed by $1B+ AI investments and Microsoft alliance. Strongest on industrialized, high-volume modernization/run engagements.

**Sources:**
- https://www.constellationr.com/research/ai-global-services-wipro-ai360-services
- https://www.gartner.com/reviews/product/wipro-holmes
- https://news.microsoft.com/source/asia/2025/12/11/cognizant-infosys-tcs-and-wipro-emerge-as-frontier-firms-with-microsoft-deploying-copilot-and-agentic-ai-across-the-enterprise/
- https://www.poniaktimes.com/india-it-ai-leaders-2025/
- https://www.zeebiz.com/technology/news-as-tcs-infosys-and-wipro-announce-their-ai-initiatives-what-are-they-working-on-their-target-and-more-stst-245252

### Adjacent benchmark: Process-mining platforms (Celonis / SAP Signavio)

**What it does:** Not consultancies, but the engines the Big firms resell/embed for 'discovery.' Celonis Process Intelligence Platform uses process mining + AI to build a 'living digital twin' of operations, revealing bottlenecks, inefficiencies and value-capture opportunities. SAP Signavio (a 2025 Gartner Magic Quadrant Leader for Process Mining) maps end-to-end processes with deep SAP/ERP integration.

**Approach:** Productized SaaS, but fundamentally event-log-driven: they need structured digital footprints (case ID, activity, timestamp) to discover the as-is process. They are best-in-class at quantifying HOW a process actually runs, but cannot reason about whether documented policy contradicts that reality, nor ingest unstructured SOPs/RACIs/notes with zero config.

**Inputs required:** Structured event logs / transactional data extracted from ERP/CRM/ITSM systems; connectors and data engineering to build event logs. Significant setup and clean structured data are prerequisites.

**Pricing:** Enterprise SaaS licensing (six- to seven-figure annual subscriptions for large enterprises, exact figures negotiated/undisclosed); often layered with consulting implementation fees.

**Differentiator:** Gold standard for data-grounded as-is process quantification when clean event logs exist. This is precisely the capability that exposes the category gap: nobody in this set autonomously reconciles unstructured documented process against system data to surface contradictions and ownership gaps.

**Sources:**
- https://www.signavio.com/products/process-intelligence/
- https://processmind.com/resources/blog/the-best-process-mining-tools-of-2026
- https://www.processexcellencenetwork.com/process-mining/articles/11-top-process-intelligence-tools-for-business-transformation

## Where they beat us (be honest)

1) BRAND, TRUST AND DELIVERY MUSCLE. Accenture/Deloitte/PwC/Capgemini and TCS/Infosys/Wipro carry the board-level trust, references, and the thousands of consultants needed to actually implement what discovery uncovers. A discovery finding from us still needs an army to execute; they own the whole value chain from finding to delivery. In a CxO bake-off, 'we used AuroPro's tool' is weaker than 'Deloitte stands behind this.'

2) BREADTH OF PRE-BUILT IP AND AGENTS. Deloitte's 1000+ pre-built industry agents, Accenture's NVIDIA-backed agent/blueprint library and AI Refinery for Industry, PwC's agent OS orchestration, and Capgemini's RAISE gallery are vastly broader than a single discovery engine. They cover post-discovery build/run; we only cover discovery.

3) STRUCTURED-DATA PROCESS QUANTIFICATION. Where clean ERP event logs exist, Process Bionics / Celonis / Signavio (and PwC's 100+ metric Process Intelligence) produce hard, real-time process-conformance and cycle-time metrics and a 'living digital twin' - a depth of quantitative process measurement our tool-over-CSV approach does not match when high-fidelity event logs are available.

4) APP-PORTFOLIO ECONOMICS FOR CARVE-OUT. Capgemini eAPM (TCO + TIME-model disposition) and Accenture GenWizard reverse-engineering/rationalization are mature, specifically built to make application-rationalization/divestiture decisions on the IT estate - a complementary but adjacent capability we do not natively provide.

5) FULL-STACK INFRASTRUCTURE AND GOVERNANCE WRAP. NVIDIA/Dell/Google Cloud/Microsoft alliances, on-prem/private-cloud deployment for regulated industries, and named governance frameworks (Trustworthy AI, Responsible AI) give them an enterprise-procurement and security/compliance story that is hard for a smaller firm to match on paper.

6) COMMERCIAL ELASTICITY. They can bundle the accelerator 'free' inside a $1M-$5M engagement or move to outcome-based fees (about 1 in 4 of McKinsey's fees now outcome-tied), making the accelerator itself look like zero incremental cost to the buyer.

## Where we beat them

1) AUTONOMOUS CONTRADICTION DISCOVERY FROM MESSY DOCS - THE CORE GAP. Every incumbent either needs clean structured event logs (Process Bionics, Celonis, Signavio, PwC Process Intelligence), works off code (GenWizard reverse-engineering, MasterCraft), or deploys/orchestrates agents (Ascend, agent OS, AI Refinery). NONE is purpose-built to ingest a domain's heterogeneous SOPs, policies, RACIs, system CSV exports and working notes and AUTONOMOUSLY surface contradictions between documented process and actual data, undocumented/unowned processes, and control gaps. That is exactly the messy reality of an early discovery phase, and it is our unique mechanic.

2) ZERO-CONFIG ON ANY DOMAIN. Process mining and eAPM require data engineering (event-log construction, app inventories, TCO data, connectors) and weeks of setup. Our generic-tool approach (describe/group_by/join_diff/filter_count over any CSV, code does the math, the agent reasons) runs on any domain's docs with zero configuration - Order-to-Cash today, Procure-to-Pay tomorrow, no remodeling.

3) GROUNDED, CONSISTENT-NOT-FABRICATED FINDINGS WITH A VERIFICATION GATE. The market is explicitly moving away from black-box AI toward grounded, traceable outputs (2025 Foundation Model Transparency Index averaged 40/100; enterprise consulting is shifting to grounded models because black-box fails audit). Incumbents answer this with governance FRAMEWORKS (Trustworthy/Responsible AI) at the program level. We answer it at the FINDING level: every number traces to the source data, a grounding gate blocks fabrication, and each finding carries confidence + provenance. That is a sharper, demoable auditability story than a policy document.

4) CLIENT-READY OUTPUT, NO TOOL JARGON. We produce a complete 6-report client suite (Current State, Pain Points, Transformation Recommendation with value-feasibility matrix, AI Opportunity Portfolio with before/after per opportunity, Roadmap, Supporting Artefacts) with no tool/agent jargon. Incumbent platforms surface dashboards/process maps/agent telemetry that still need consultants to translate into a board narrative.

5) PURPOSE-BUILT FOR POST-CARVE-OUT / TSA-EXIT DISCOVERY. In a carve-out the painful truth is that documentation and system reality have diverged and ownership is ambiguous - precisely the contradictions and unowned-process findings we autonomously detect. eAPM/GenWizard score the IT estate; we reconcile the PROCESS narrative against the data, which is the missing half of TSA-exit rationalization.

6) ACCELERATOR ECONOMICS WITH HUMAN-SME-IN-THE-LOOP. Delivered as a consulting accelerator (not a SaaS seat), we compress the most labor-intensive, lowest-leverage part of discovery - reading documents and cross-checking them against exports - while keeping the SME in the loop for judgment. For a smaller firm this is the wedge: out-discover the giants on findings-per-dollar and time-to-first-finding, then partner or hand off execution, rather than competing on headcount or breadth of post-discovery IP we will never win.

## Documented weaknesses / complaints (and how we address them)

### Long implementation / slow time-to-insight. Big-4-led AI engagements run 6–12 month timelines just to deliver a strategic roadmap, by which point fast-moving AI capability has made a Q1 strategy structurally outdated by Q3. Discovery itself is slow because the value is in billable people, not a product.

_Evidence:_ Jinba blog: 'Big Four AI consulting engagements are notorious for 6–12 month timelines just to deliver a strategic roadmap... a strategy developed in Q1 can be structurally outdated by Q3.' DAS Advanced Systems: Big 4 firms failing mid-size companies because of slow, people-heavy delivery.

_Source:_ https://jinba.io/blog/ai-consulting-financial-big-four ; https://dasadvancedsystems.com/blog/why-big-4-consulting-firms-are-failing-mid-size-companies-with-ai/

**How we address it:** Our platform autonomously ingests heterogeneous docs + CSVs and produces the 6-report suite in days, not months — collapsing the data-gathering/extraction phase (the slow part) while keeping SME validation. Positioned as a 2-week, one-domain pilot vs. 8–12 weeks of structured workshops. Directly attacks the time-to-insight pain.

### Black-box, unauditable AI outputs. Big-4 implementations rely on opaque third-party generative models; results are 'difficult to trust, impossible to audit, and potentially dangerous.' AI that cannot trace outputs back to a governed source of record becomes a liability in regulated/audit contexts. Foundation models themselves remain opaque on data practices (Stanford FMTI: areas of 'sustained and systemic opacity').

_Evidence:_ VentureBeat 'Black box AI isn't enough': frontier models disconnected from authoritative repositories produce results 'difficult to trust, impossible to audit'; 'AI that cannot trace its outputs back to a governed source of record becomes a liability.' Stanford FMTI 2024: average 58/100, with persistent systemic opacity on data access/practices (37/100 in 2023).

_Source:_ https://venturebeat.com/ai/black-box-ai-isnt-enough-why-enterprise-consulting-is-moving-to-grounded ; https://crfm.stanford.edu/fmti/May-2024/index.html

**How we address it:** Core wedge. Every finding carries confidence + provenance, and every number traces to the source data, verified by a grounding gate before it reaches the client report. This is the 'glass box' the market is explicitly moving toward — not generic 'Trustworthy AI' governance framing, but per-finding data traceability.

### Fabricated / hallucinated content in deliverables. Deloitte Australia refunded part of a ~AU$439k government report after it was found 'full of fabricated references' — non-existent academic papers and a fabricated court quote — produced with Azure OpenAI GPT-4o. Seen as a wake-up call that AI deliverables can invent facts that destroy credibility.

_Evidence:_ Fortune/The Register/Business Standard (Oct 2025): Deloitte refunded the final installment after a researcher flagged hallucinated, non-existent references and a fabricated judgment quote; firm disclosed GPT-4o use. CFO Dive: 'wake-up call for corporate finance.'

_Source:_ https://fortune.com/2025/10/07/deloitte-ai-australia-government-report-hallucinations-technology-290000-refund/ ; https://www.theregister.com/2025/10/06/deloitte_ai_report_australia/

**How we address it:** Our 'consistent-not-fabricated' design and grounding gate exist precisely to prevent this failure mode: the agent computes over the client's own data with generic tools (code does the math), and no number ships unless it traces to the data. We can position directly against the Deloitte scenario — findings are derived and verifiable, not generatively invented.

### High cost / cost overruns and lock-in. Big 4 senior consultants exceed $1,000/hr; engagements are designed as managed-services dependency (targeting 20–25% of advisory revenue) rather than deliver-and-exit. Even the IP exists to make billable people faster, not to be sold as a product.

_Evidence:_ Jinba blog: 'Hourly rates for Big Four senior consultants routinely exceed $1,000/hour'; firms 'increasingly targeting managed services contracts to generate 20–25% of advisory revenue — the engagement model is designed to keep you dependent, not to deliver and exit cleanly.'

_Source:_ https://jinba.io/blog/ai-consulting-financial-big-four

**How we address it:** Delivered as a consulting accelerator that compresses the labor-intensive discovery phase, lowering the cost base of the engagement — we eliminate the data-gathering effort (the expensive part) rather than billing people for it. Partially addressed: pricing model must still be shaped, but the value mechanic is structural cost reduction, not lock-in.

### Thin deliverables — polished slide deck, implementation left to the client. The most common Big-4 output is a slide deck of 'AI opportunities,' with vendor selection, deployment and execution left to already-stretched internal teams. Clients implement consulting recommendations only ~50% of the time; strategy decks become 'shelf-ware' displaced by the next fire drill, often because no clear ROI/business case.

_Evidence:_ Jinba blog: 'the most common deliverable... is a polished slide deck outlining AI opportunities, and implementation... is left to internal teams.' Consultant's Mind: recommendations 'move to shelf-ware'; consultants believe clients implement ~50% of the time; failures when 'ownership is unclear' or 'strategic changes are not perceived as delivering immediate ROI.'

_Source:_ https://jinba.io/blog/ai-consulting-financial-big-four ; https://www.consultantsmind.com/2023/01/15/why-clients-dont-implement/

**How we address it:** Our 6-report suite is built for action, not just insight: an AI Opportunity Portfolio with explicit before/after per opportunity, a value-feasibility matrix, and a Transformation Roadmap with Supporting Artefacts. Findings carry ownership signals (e.g., 'undocumented/unowned process') — directly attacking the 'unclear ownership' and 'no ROI case' reasons recommendations stall.

### Process mining needs clean, complete event logs and per-system connectors. Celonis requires integrations to every source system to extract event logs; many business apps have no event logs; it 'relies heavily on high-quality, complete, consistent event-log data' and demands a lot of effort. ETL/event-log engineering is the first and most expensive step, consuming time that should go to analysis; connector gaps and lacking ETL functionality block landscapes of 50+ apps.

_Evidence:_ G2/PeerSpot Celonis: needs integrations to every source system; many apps lack event logs; relies on high-quality, complete, consistent logs. Springer practitioner studies: ETL of event logs is 'the first and the most expensive step'; 'so much time and effort is consumed during the ETL phase that should be devoted to analysis'; 'ETL functionality in process mining tools is lacking'; connector gaps for many systems.

_Source:_ https://www.g2.com/products/celonis/reviews ; https://link.springer.com/chapter/10.1007/978-3-031-08848-3_7 ; https://link.springer.com/article/10.1007/s10270-023-01134-0

**How we address it:** Direct differentiator. We do NOT require structured event logs or per-system connectors. The agent runs generic tools (describe/group_by/join_diff/filter_count) over ANY heterogeneous CSV/doc with zero config. We turn the most expensive, most-complained-about step (event-log/ETL engineering) into a non-step.

### Process mining is blind to undocumented workarounds and the documentation-vs-reality gap. It captures the 'happy path' but not the 'hidden factory' of manual workarounds, rework loops and informal steps; some workaround types 'leave no recognizable trace in the log.' Work in email, spreadsheets, legacy apps and manual tasks 'leaves no structured log trail and therefore stays invisible.'

_Evidence:_ Research (ResearchGate/ScienceDirect) + Skan.ai/Edana: process mining 'does not capture how work is performed inside specific activities... undocumented workarounds'; 'workaround types that leave no recognizable trace in the log'; work in 'email, spreadsheets, legacy applications, manual tasks, mainframes, and VDI... stays invisible to a traditional process mining tool.'

_Source:_ https://www.researchgate.net/publication/286939026_Business_Process_Workarounds_What_Can_and_Cannot_Be_Detected_by_Process_Mining ; https://www.skan.ai/blogs/process-mining-tool-underperforming

**How we address it:** This is our central mechanic: we autonomously surface contradictions between what documents SAY (SOPs, RACIs, working notes) and what system data DOES, and we explicitly find undocumented/unowned processes — exactly the 'hidden factory' and SOP-vs-reality gap process mining cannot see. We read the messy unstructured docs that hold the workarounds.

### Process/transformation tools assume the process landscape conforms to a vendor 'best practice' template. SAP Signavio's central design assumption is that the landscape is aligned to SAP best-practice processes; for processes that have evolved over decades and diverged, 'most of the assumptions and insights are invalid.' Users also report missing analytical features to validate the tool's own insights.

_Evidence:_ SAP Community / Gartner Peer Insights on Signavio Process Insights: foundational assumption that the process is aligned to SAP best practice; 'for processes that have evolved over decades and are no longer aligned with best practice, most of the assumptions and insights are invalid'; users 'missing certain analytical features... that would allow validation of the tool's insights.'

_Source:_ https://community.sap.com/t5/technology-q-a/signavio-process-insights-insufficient-data-collection-for-certain/qaq-p/13856605 ; https://www.gartner.com/reviews/product/sap-signavio-process-intelligence

**How we address it:** We make zero assumptions about a reference/best-practice model. The agent reasons over the client's actual documents and data as they are — divergent, decades-old, carve-out-mangled processes are the target, not an edge case. And our findings are validatable by design (provenance + SME-in-the-loop) versus tools whose insights can't be validated.

### Steep learning curve, proprietary languages and specialist dependence. Celonis needs dedicated data scientists/process analysts and partner services; PQL is a Celonis-only language with little outside/AI help; long (typically 3-year) contracts and constantly changing licensing.

_Evidence:_ G2/PeerSpot + Gartner Peer Insights: 'steep learning curve... organizations often needing dedicated specialists or relying heavily on partner services'; 'PQL is a code that only Celonis uses, so there is little help on the internet'; complaints re long 3-year contracts and 'constant changes in the licensing structure.'

_Source:_ https://www.g2.com/products/celonis/reviews ; https://www.gartner.com/reviews/market/process-mining-platforms/vendor/celonis/product/celonis-process-intelligence-platform/likes-dislikes

**How we address it:** Zero-config, runs on any domain's docs with no proprietary query language for the client to learn; the agent does the reasoning and code does the math. No standing team of specialists required to operate it — it is an accelerator the consulting team points at a folder, not a platform clients must staff.

### App-portfolio rationalization tools depend on manual, one-off, decaying data and shaky TCO/CMDB inputs. Inventory collection is a 'one-time event' with painful manual analysis and no continuity; TCO calculations are either too simplistic (dismissed) or too complex (inaccurate); 'if CMDB coverage and accuracy are weak, the confidence of APM-derived recommendations will be questioned.' Programs stall when evidence pipelines are weak and decisions can't be defended.

_Evidence:_ Apptio / Dunnixer / Oracle EA guide: inventory collection is a 'one-time event' with painful manual analysis and 'no continuity to the process, data, or analysis'; TCO too-simple-vs-too-complex tradeoff undermines buy-in; 'if CMDB coverage and accuracy are weak, the confidence of APM-derived recommendations will be questioned'; programs stall when 'evidence pipelines are weak.'

_Source:_ https://www.apptio.com/topics/application-rationalization/ ; https://www.dunnixer.com/insights/articles/automating-application-portfolio-rationalization-tools

**How we address it:** Our findings come with confidence + provenance and trace to source data, so recommendations are defensible rather than 'questioned' — and discovery is re-runnable on the actual documents/exports rather than a hand-maintained inventory that decays. We target the business-process narrative (contradictions, control gaps, ownership), complementing IT-estate TCO scoring rather than relying on a clean CMDB.

### No carve-out / TSA-exit specificity. Incumbent accelerators cluster into agent-deployment platforms, process mining (needs logs), or IT-estate app-scoring — none is purpose-built for the messy post-carve-out reality of orphaned processes, ambiguous ownership, and live TSA dependencies discovered across SOPs + system exports. Mid-size and divestiture clients report Big 4 give them generic, slow, people-heavy engagements.

_Evidence:_ Category synthesis from dossier + DAS Advanced Systems ('Why Big 4 Consulting Firms are Failing Mid-Size Companies with AI') describing generic, ill-fitted Big-4 AI engagements; process-mining/app-rationalization sources above confirm focus on logs/IT estate, not carve-out process narrative.

_Source:_ https://dasadvancedsystems.com/blog/why-big-4-consulting-firms-are-failing-mid-size-companies-with-ai/

**How we address it:** Positioned specifically for post-carve-out / TSA-exit application & process rationalisation: the platform surfaces undocumented/unowned processes and contradictions (e.g., 'the SOP doesn't mention the EDI link the TSA depends on'), the exact failure modes carve-outs create. This specificity is the wedge — no incumbent accelerator is built for it.

### Clients now expect AI-driven efficiency to be passed on as price cuts, exposing labor-arbitrage accelerators. PwC has cut prices for some services because clients argued the firm is using AI to work faster and want 'their fair share of those efficiencies' — pressuring accelerators whose value is making billable people faster rather than producing a verifiable product output.

_Evidence:_ Going Concern / FT-sourced reporting: 'PwC has cut prices for some services as clients raised the fact that the consultancy is using AI... clients want their fair share of those efficiencies' (PwC Chief AI Officer).

_Source:_ https://www.goingconcern.com/big-4-firm-discovers-that-bragging-about-ai-efficiencies-leads-clients-to-expect-a-discount/

**How we address it:** We are sold as a productized accelerator whose value is the verifiable findings output and time compression, not disguised hourly arbitrage — so the efficiency is transparent and built into the offer rather than something clients must claw back. Partially addressed: reinforces the productized, outcome-shaped commercial framing.
