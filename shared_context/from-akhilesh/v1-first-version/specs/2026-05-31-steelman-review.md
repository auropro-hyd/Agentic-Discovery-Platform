# Steelman External Review — Opella Demo Script & Synthetic Inputs

**Date:** 2026-05-31
**Method:** Independent subagent cold read (office-hours Phase 3.5 protocol)
**Reviewer role simulated:** Opella Head of Strategy (primary audience)
**Scope:** Both demo scenarios — Demand Planning (primary) + O2C (secondary)

---

## How the Review Was Conducted

A subagent was dispatched with a fully self-contained brief covering the Opella context, both demo scripts, the three-finding structure for each domain, and the synthetic input design principle. The subagent had no access to the conversation history — it received only a structured brief and returned a cold assessment. The output was then synthesised with a first-person review from the primary model.

---

## Audience Simulation — Scenario A: Demand Planning

**First reaction when findings surface:** Suspicion before excitement. The findings are specific enough to feel planted — 34% S&OP override rate, three-system reconciliation failure. Thought: "How did they know to look there?" This is a credibility liability that must be scripted for.

**First question asked:** "Where did this data actually come from? These numbers — are those from real Opella data or did you build these scenarios from scratch?" This question is not in AuroPro's current script and will be asked.

**Lean forward moment:** The S&OP governance finding. "Your process documentation and your actual operations are describing two different companies." Every carve-out has this problem. It's painful and specific. This line will be remembered after the meeting.

**Lean back moment:** The 12–15 day lag cross-domain insight. It sounds pre-scripted. A document ingestion platform cannot derive a causal lag relationship from reading SOPs and distribution logs. Will be challenged by any technically curious follow-up.

**Reaction at the close:** Scepticism about "a plan your board can act on" in two weeks. A Head of Strategy knows what two weeks of consulting produces. The close also has no commercial shape — no mention of what the pilot actually costs or requires from Opella.

**Key objections not scripted for:**
1. "Who owns finding validation?" — when findings are contested between functions, who adjudicates?
2. "What happens to our data?" — post-carve-out data hygiene concern, live TSA obligations
3. "What format is the output?" — a static PDF vs. a structured living document is a different value proposition
4. "What's the failure mode?" — 60 findings with 45 wrong destroys the credibility of the 15 that matter

---

## Audience Simulation — Scenario B: Order-to-Cash

**First reaction:** More immediate, more visceral than Scenario A. Credit limit discrepancies and TSA-exposed EDI connections have board-level materiality. Reaction is: "Is this happening right now?"

**First question asked:** "The CS team lead working notes — how did the platform find those?" This is the right question. The ingestion pathway for informal documents is the real differentiator if it's credible.

**Lean forward/back:** Leans forward harder than Scenario A. Financial materiality is legible within 30 seconds. The cross-domain link (escalation spike ← demand miss) is more credible here because it's framed as confirmation, not standalone discovery.

**Reaction at the close:** More likely to push for O2C as the pilot domain (CFO business case is easier to build). Different dynamic than Scenario A.

**Key objections not scripted for:**
1. "TSA finding — is this a platform finding or a legal/contractual question?" Resolution requires legal + IT negotiation, not roadmap sequencing. Is it in scope?
2. "What's the accuracy baseline?" — if numbers are directionally right but 20% off, do you trust the roadmap?

---

## Thinking Maturity Assessment

| Dimension | Rating | Notes |
|---|---|---|
| Demo narrative (Discovery Journey) | Strong | Right choice for this audience. Missing: credibility anchor for quality, not just speed. Speed without quality is worse than slow. |
| Domain selection (Demand Planning primary) | Strong | Correct call. Risk: if audience is commercially-led, Scenario A lands softly. Trigger to switch scenarios should be explicit and rehearsed. |
| Finding design — severity mix | Good | Two red, one amber is right. S&OP governance finding is the best across both scenarios. |
| Finding 1 (Forecast Ownership) | Weak lead | Reads as IT problem until the business consequence appears. Move Allegra/consequence into the finding itself. "Three systems — last Allegra season, which one did they trust?" |
| Synthetic input design principle | Invisible | "No single document reveals a finding" is correct design but the audience cannot see it. Make it visible once: "The formal SOP doesn't mention EDI at all. This only surfaced because we read the CS working notes alongside it." |
| Language discipline | Strong | Correct. The audience will notice subconsciously even if they can't articulate why. |
| The close | Needs fix | "A plan your board can act on" overclaims. See recommended revision below. |
| 80% effort reduction claim | Unprepared | Implied but not scripted. Will be challenged immediately. Needs a precise formulation. |

---

## Realism Assessment

| Claim | Assessment |
|---|---|
| 20-minute demo structure | Credible only if pre-rendered, not truly live. If live, loading states will kill momentum. Need to have an honest answer ready: "In this demo we show a pre-run; in the pilot the pipeline takes X hours." |
| 12–15 day lag cross-domain insight | Most technically exposed claim. Cannot be derived from document ingestion alone. Re-frame as structural pattern, not statistical finding. |
| DC Allocation Model amber finding | Most realistic finding. Exactly the kind of unresolved reference that appears in real carve-out discovery. Severity classification (amber vs. red) should be defensible — have a ready answer. |
| 80% effort reduction | Will be pushed on immediately. Needs precise formulation (see below). |
| Pilot close ("Two weeks, one domain") | Low-risk offer structure is right. "Board-ready plan" language is wrong. |

---

## Required Script Fixes

### Fix 1: Data provenance answer (not currently scripted)

**Trigger:** "How did you know to look there? Where did these numbers come from?"

**Answer:** "Everything you saw was built from synthetic data structured on public FMCH carve-out patterns — not anything from your organisation. The reason it looks familiar is that these problems are structural to any large carve-out. In the pilot, we'd run this on your real data. The findings would be yours, not ours."

---

### Fix 2: Finding 1 — add business consequence up front

**Current:** "Three systems hold European demand forecast data... numbers do not reconcile."

**Fix:** "Three systems are telling your demand planning team three different things. Last Allegra season — which one did they trust?"

---

### Fix 3: Cross-domain lag — re-frame from causal to structural

**Current:** "The platform found [the 12–15 day pattern] by reading the distribution logs and the order fulfilment records together."

**Fix:** "What the platform identified is a structural dependency — when forecast data doesn't reconcile between demand planning and distribution, the downstream buffer absorbs the error for a predictable window. That 12–15 day window is built into your operational lead times."

---

### Fix 4: Make the cross-reference principle visible (Scenario B only)

**Add one sentence:** "The formal Order Management SOP doesn't mention EDI at all. This finding only surfaced because we read the formal SOP alongside the CS team lead's working notes. Traditional discovery would have stopped at the SOP."

---

### Fix 5: Close — remove the overclaim

**Current:** "Two weeks. One domain. A plan your board can act on."

**Fix:** "Two weeks. One domain. Your transformation team reviews the findings — they don't produce them. We come out with something structured enough to take to your board, or we'll tell you why we don't."

---

### Fix 6: 80% claim — precise formulation ready for discussion phase

"Traditional discovery requires 8–12 weeks of structured workshops involving 15–20 of your business team members for 4–8 hours each. Our pilot requires two weeks, two SME review sessions, and access to your document repositories. The compression is in the extraction phase — we eliminate the data gathering, not the validation."

---

### Fix 7: Post-pilot path (discussion phase, not demo)

One sentence to have ready when the discussion opens: "If the pilot lands, here's what the full engagement model looks like and what we can commit to across the programme."

This doesn't need to be in the demo. It needs to be ready for the 25-minute discussion — because that's when the Head of Strategy shifts from insight mode to due-diligence mode.

---

## Overall Verdict

**Strong:** Language discipline, S&OP governance finding, Scenario B informal document moment, silence-as-close instinct, severity tiering logic, synthetic input architecture.

**Gaps:** 12–15 day lag claim is the single most technically exposed element. Close overclaims. No post-pilot path. Data provenance question unscripted.

**Thinking maturity:** High. Above the median enterprise AI pitch. The gaps are not in the demo itself — they're in the 25-minute discussion phase that follows. The demo is optimised for the insight moment. The due-diligence phase is where the script currently goes dark.

---

## Related Artifacts

- [Demo Script & Synthetic Inputs Spec](2026-05-31-demo-script-and-synthetic-inputs.md)
- [Primary Demo Script — Demand Planning](html/demo-script-v2.html)
- [Secondary Demo Script — O2C](html/demo-script-o2c.html)
- [Synthetic Inputs — Demand Planning](html/synthetic-inputs-demand-planning.html)
- [Synthetic Inputs — O2C](html/synthetic-inputs-o2c.html)
