# O2C Discovery Prototype — Build-Ready Design Spec (tech-lead merge)

Status: APPROVED FOR BUILD. Supersedes the three draft designs and folds in all three critiques.
Scope: linear CLI prototype, Python 3.14, no orchestrator. Governing principle: **code does the
math, the agent does the reasoning**; output must be **consistent** (same 3 findings every run on
the same docs) and **not fabricated** (every number computed from data, never hardcoded).

All numbers below are verified against the live data in `prototype/inputs/o2c/` (see §4 Gate A).

---

## 0. Decisions that resolve the draft contradictions (read first)

| # | Contradiction across drafts/critiques | DECISION |
|---|---|---|
| D1 | Are the load-bearing tool *calls* pinned, or does the agent choose freely? | **Both, layered.** The agent runs free for discovery, BUT the three load-bearing findings each have a **pinned scripted trajectory** (exact tool + exact args) that is the demo default (`--scripted`). The agent loop is the "show". The scripted path is the "tell". They call the *same* tool functions, so numbers are byte-identical. This kills FM-4/FM1(loop)/FM5 — determinism comes from orchestration, not from hoping temp-0 is stable across provider drift. |
| D2 | `join_diff` "the €600K delta" vs "307-row haystack" | `join_diff` **ranks matched rows by `abs(numeric delta of rank_by)` desc, key asc tie-break**, returns top_n + summary stats (`rows_with_any_difference`, per-column `n_mismatch`, `sum_delta`). FR001 is row #1 deterministically. The finding headline is "**307 accounts disagree; largest is FR001 Carrefour +€600,000**" — stronger and true. The original spec's `sum_delta=78,550,000 / n_nonzero=307` was **fabricated**; real is **sum_delta=5,325,000 / n_nonzero=267**. |
| D3 | F2 "volume" = count or value? | **Count is canonical.** `group_by(count)` → EDI = 5667/8420 = **67.3%**. The finding cites the **count** as primary. `group_by` returns BOTH `pct_of_rows` and (when `value_col` given) `pct_of_value`, and the emit schema forces a `basis` label, so the 67.3%-by-count vs 66.8%-by-value ambiguity can never silently flip the headline. |
| D4 | F3: hand-transcribe a CSV sidecar, or read prose? | **Read frozen prose + a deterministic text primitive.** Verified: the EDI register PDF extracts the "8 / 6 / 14" split in **clean prose** ("8 under Opella Digital management (connections 1-8) and 6 remaining under Sanofi Shared Services... (connections 9-14)", "these six trading partners", "All 14 active production EDI connections"). The table *rows* mangle (the `#` column splits "10"→"1\n0"), so **do not count table rows**; count via the prose + a `find_mentions` text tool over the pinned 6-entity list. No hand-built CSV — that would re-introduce a hand-authored answer (anti-principle). |
| D5 | F2 "undocumented" = prove a negative over a mangled RACI table? | **No — it is a positive statement.** Verified the RACI says, in clean prose: *"This RACI covers Manual (telephone) and Email order channels only. EDI channel process steps are not included in this version of the RACI"* and *"EDI-related rows excluded pending formal EDI process [SOP]"*. F2's "undocumented/unowned" is grounded by **quoting that line**, via `find_mentions`, not by asserting an absence. |
| D6 | pypdf installed? extraction stable? | **Installed (6.12.2 in `prototype/.venv`); extraction is byte-stable** across repeated runs (verified, all 3 PDFs). Still **pin the version** (`pypdf==6.12.2`) and **freeze extracted text to committed sidecars** for portability/audit, but the "not installed / garbage" premise is false. |
| D7 | `filter_count` predicate: string DSL vs JSON-AST vs flat? | **Flat structured leaf for the prototype** `{col, op, value}` with closed `op` enum + optional `all/any/not` nesting (cap depth 6). No `eval`, no free-text. Unicode **NFC-normalized, case-insensitive** compare (the root_cause has a U+2014 em-dash; ASCII `-` would silently return 0). |
| D8 | Channel vocabulary | Verified: order-flow channels are **`EDI / Manual / Fax / Email`** (NO "Phone"; "Phone" exists only in the escalation log's `channel` column). All draft prose saying "Phone/email" is wrong. The agent must read channels from `group_by`, never from prose or a 5-row sample. |
| D9 | Finding count 1–5? | **Exactly 3.** `emit_findings` schema `minItems:3, maxItems:3`. System prompt instructs "rank by business consequence; emit the top 3." Report renderer stable-sorts by `(severity_rank, id)`. Stops the 3-vs-4-vs-5 drift (the 34-incident stat and the 307-account stat are folded into F3 and F1 respectively, not split into new findings). |

---

## 1. Final tool list — Python signatures + LLM tool-definition JSON

Six tools. Five compute over **any** CSV (operation-named, generic — not `compute_channel_share`,
not one mega-tool, not `run_python`). One reads **frozen document text** (needed for F2/F3
qualitative halves). One terminator. All live in `discovery/tools.py` — the *only* module where
arithmetic exists.

### 1.0 Shared invariants (enforced for every tool)
- **Pure stdlib + pypdf-frozen-text only**: `csv`, `json`, `hashlib`, `pathlib`, `decimal`, `unicodedata`. No pandas/numpy. CSVs streamed via `csv.DictReader` (the 8420-row file never materializes beyond accumulators).
- **Pure function of (file bytes, args)**: no clock, RNG, network, or global mutable state.
- **Total-ordered output**: every list sorted by an explicit documented key; every set `sorted()` before returning; every serialized dict dumped `sort_keys=True`. (PYTHONHASHSEED-proof.)
- **Code pre-rounds via one policy** (`Decimal` + `ROUND_HALF_EVEN`): money/sums → 2 dp, percentages → 1 dp, averages → 4 dp.
- **Provenance on every result**: `{file, sha256_12, row_count}` plus the keys/row indices/predicate that produced any pointed-at value, so a finding can cite "FR001 in sap-s4…, row 1".
- **Safe file ids, not paths**: `file` args are logical ids resolved through a server-side `FILE_REGISTRY: dict[str, Path]`; unknown id → typed error. Enums in the JSON schemas are generated from the registry at startup.
- **Typed errors, returned not raised**: `{"error": {"code", "message", "tool"}}` with `code ∈ {unknown_file, unknown_column, bad_predicate, bad_arg, type_mismatch}`; messages list available columns/ids so the agent self-corrects deterministically.

### 1.1 Shared helpers
```python
from __future__ import annotations
import csv, hashlib, json, unicodedata
from decimal import Decimal, ROUND_HALF_EVEN
from pathlib import Path

FILE_REGISTRY: dict[str, Path] = {}   # populated at startup from inputs/<domain>/

def _q(x, places):                      # one rounding policy, platform-stable
    return None if x is None else float(Decimal(str(x)).quantize(Decimal(10) ** -places,
                                                                  rounding=ROUND_HALF_EVEN))
def _round_money(x): return _q(x, 2)
def _round_pct(x):   return _q(x, 1)
def _round_avg(x):   return _q(x, 4)

def _norm(s: str) -> str:               # D7: NFC + casefold so em-dash/casing never bite
    return unicodedata.normalize("NFC", str(s)).strip().casefold()

_NULLS = {"", "na", "n/a", "null", "none", "-"}
def _to_number(raw):                    # (ok, value); strips €,$,commas,%
    if raw is None: return False, None
    s = str(raw).strip().replace(",", "").replace("€", "").replace("$", "").replace("%", "")
    if s.lower() in _NULLS: return False, None
    try: return True, float(s)
    except ValueError: return False, None

def _resolve(file): ...                 # FILE_REGISTRY lookup or raise ToolError(unknown_file)
def _provenance(file): ...              # {file, sha256_12, row_count}
def _iter_rows(path):                   # yields (1-based_index, dict-row); utf-8-sig
    ...
```

### 1.2 `describe(file)`
```python
def describe(file: str, *, sample_rows: int = 5) -> dict
```
One streaming pass. Returns schema, row_count, per-column `{dtype, nulls, distinct_count,
numeric_parse_rate}`, a head sample (≤10, file order), and — **the FM-2/FM-7 fix** — for any
**low-cardinality column (distinct ≤ 25) the FULL distinct value list with counts**, sorted
`(count desc, value asc)`. This is what surfaces the rare load-bearing values
(`migration_source="Sanofi Legacy System"` is 6/340 rows; the exact em-dash `root_cause` string)
that a 5-row sample would miss. dtype inferred try int→float→date→str over up to 1000 values.
```json
{"name":"describe",
 "description":"Inspect a CSV before computing on it: schema, row_count, per-column dtype/null/distinct counts, a small head sample, and for low-cardinality columns (<=25 distinct) the FULL list of distinct values with counts. ALWAYS call this on a file before group_by/aggregate/filter_count/join_diff so you reference real column names and exact category values. Does not load the whole file.",
 "input_schema":{"type":"object","properties":{
   "file":{"type":"string","description":"Logical CSV id from the manifest.","enum":["sap-s4-customer-master-export","sap-crm-customer-export","order-flow-analysis-export-2025","customer-service-escalation-log-2025"]},
   "sample_rows":{"type":"integer","minimum":1,"maximum":10,"default":5}},
  "required":["file"]}}
```

### 1.3 `group_by(file, by, agg, value_col=None)` — F2 workhorse
```python
def group_by(file: str, by: list[str], agg: str = "count",
             value_col: str | None = None, *, top_n: int = 20) -> dict
```
Per-group `count` and, when `value_col` given, `sum`. **Always returns `pct_of_rows`; when
`value_col` given also returns `pct_of_value`** (D3 — kills count-vs-value ambiguity).
Non-numeric cells in `value_col` skipped and counted in `excluded_nonnumeric`. Groups sorted by
metric desc, then group-key asc. Percentages computed over ALL groups; `top_n` only truncates the
returned list (`total_groups`, `truncated` flags present).
```json
{"name":"group_by",
 "description":"Group a CSV by column(s) and aggregate. Returns per group: count, pct_of_rows, and (if value_col given) sum + pct_of_value. Percentages cover ALL groups even if only top_n returned. Use to find how a categorical column (channel, status, root_cause) distributes.",
 "input_schema":{"type":"object","properties":{
   "file":{"type":"string","enum":["sap-s4-customer-master-export","sap-crm-customer-export","order-flow-analysis-export-2025","customer-service-escalation-log-2025"]},
   "by":{"type":"array","items":{"type":"string"},"minItems":1,"maxItems":3},
   "agg":{"type":"string","enum":["count","sum"],"default":"count"},
   "value_col":{"type":["string","null"],"default":null,"description":"Numeric column; required when agg='sum'."},
   "top_n":{"type":"integer","minimum":1,"maximum":100,"default":20}},
  "required":["file","by"]}}
```
Verified return for `group_by("order-flow-analysis-export-2025",["channel"],"count")`:
`EDI count=5667 pct_of_rows=67.3 | Manual 1802/21.4 | Email 767/9.1 | Fax 184/2.2`, `grand_total_rows=8420`.

### 1.4 `join_diff(file_a, file_b, key, compare_cols, rank_by=None)` — F1 workhorse
```python
def join_diff(file_a: str, file_b: str, key: str, compare_cols: list[str],
              *, top_n: int = 20, rank_by: str | None = None,
              context_cols_a: list[str] | None = None,
              context_cols_b: list[str] | None = None) -> dict
```
Outer join on `key`. For matched keys: per compare-col, if both parse numeric → `{type:numeric,
a, b, delta:b-a, changed}`; else `{type:text, a, b, changed}`. **Ranks matched rows by
`abs(delta of rank_by)` desc (default = first numeric compare_col), key asc** (D2 — FR001 is row
#1 deterministically). **The dropped `context_cols_a/b` extension is SHIPPED** (FM-3): single-file
columns with *different names* in each file (ERP `migration_source` vs CRM `source`) ride along as
raw `{a_val|b_val}` per matched key, with no delta — so FR001 can cite "ERP migration_source='Sanofi
Legacy System', CRM source='manually updated by account manager post-carve-out'" **from a tool**,
not free-text. Unmatched keys go to `only_in_a/only_in_b` (sorted, capped lists + counts) and are
**never numerically coerced** (H2). Summary: `matched_keys`, `only_in_a_count`, `only_in_b_count`,
`rows_with_any_difference`, per-column `{n_mismatch, sum_delta}` (n_mismatch = rows where *that*
column differs — never reuse `rows_with_any_difference`; FM-1).
```json
{"name":"join_diff",
 "description":"Outer-join two CSVs on a shared key and report per-row differences. Returns: matched_keys, keys only_in_a, keys only_in_b, and matched rows ranked by largest absolute numeric delta (file_b minus file_a). Each compare_col yields a numeric delta or a text changed-flag with both values. context_cols carry along single-file columns (even with different names) as raw values for narrative. Use to find data conflicts across two system exports of the same entities.",
 "input_schema":{"type":"object","properties":{
   "file_a":{"type":"string","enum":["sap-s4-customer-master-export","sap-crm-customer-export","order-flow-analysis-export-2025","customer-service-escalation-log-2025"]},
   "file_b":{"type":"string","enum":["sap-s4-customer-master-export","sap-crm-customer-export","order-flow-analysis-export-2025","customer-service-escalation-log-2025"]},
   "key":{"type":"string"},
   "compare_cols":{"type":"array","items":{"type":"string"},"minItems":1,"description":"Columns present in BOTH files."},
   "context_cols_a":{"type":["array","null"],"items":{"type":"string"},"default":null,"description":"file_a-only columns to attach as raw values (no delta)."},
   "context_cols_b":{"type":["array","null"],"items":{"type":"string"},"default":null},
   "rank_by":{"type":["string","null"],"default":null,"description":"Numeric compare_col to sort by |delta| desc. Defaults to first numeric compare_col."},
   "top_n":{"type":"integer","minimum":1,"maximum":100,"default":20}},
  "required":["file_a","file_b","key","compare_cols"]}}
```
Verified pinned F1 call → `matched_keys=318, only_in_a_count=22, only_in_b_count=0,
rows_with_any_difference=307, credit_limit_eur:{n_mismatch:267, sum_delta:5325000.00},
payment_terms:{n_mismatch:228}`; matched_rows[0] = FR001 `{credit_limit_eur:{a:1800000,b:2400000,
delta:600000}, payment_terms:{a:NET45,b:NET30}}`, context = `{migration_source:"Sanofi Legacy
System" | source:"manually updated by account manager post-carve-out"}`.

### 1.5 `filter_count(file, predicate)`
```python
def filter_count(file: str, predicate: dict) -> dict
```
Predicate = leaf `{col, op, value}` or boolean node `{all:[...]}|{any:[...]}|{not:...}`; depth ≤6,
≤50 nodes. `op ∈ {eq,ne,lt,le,gt,ge,contains,not_contains,starts_with,ends_with,in,not_in,is_empty,
not_empty}`. **Tiny recursive interpreter, no eval.** String ops compare on **NFC-normalized,
casefolded** text (D7/C2). Numeric ops coerce via `_to_number`; non-numeric → leaf False (no crash).
Returns `matched, total, pct_of_total, example_row_indices (≤5, file order)`.
```json
{"name":"filter_count",
 "description":"Count rows matching a SAFE structured predicate (no code). Leaf {col,op,value} combined with {all:[]}/{any:[]}/{not:}. String comparisons are Unicode-normalized and case-insensitive. Returns matched count, total, pct, and example row indices. Use to quantify how often a labeled condition occurs (e.g. a specific root_cause).",
 "input_schema":{"type":"object","properties":{
   "file":{"type":"string","enum":["sap-s4-customer-master-export","sap-crm-customer-export","order-flow-analysis-export-2025","customer-service-escalation-log-2025"]},
   "predicate":{"$ref":"#/$defs/predicate"}},
  "required":["file","predicate"],
  "$defs":{"predicate":{"oneOf":[
    {"type":"object","properties":{"col":{"type":"string"},"op":{"type":"string","enum":["eq","ne","lt","le","gt","ge","contains","not_contains","starts_with","ends_with","in","not_in","is_empty","not_empty"]},"value":{}},"required":["col","op"],"additionalProperties":false},
    {"type":"object","properties":{"all":{"type":"array","items":{"$ref":"#/$defs/predicate"},"minItems":1}},"required":["all"],"additionalProperties":false},
    {"type":"object","properties":{"any":{"type":"array","items":{"$ref":"#/$defs/predicate"},"minItems":1}},"required":["any"],"additionalProperties":false},
    {"type":"object","properties":{"not":{"$ref":"#/$defs/predicate"}},"required":["not"],"additionalProperties":false}]}}}}
```
Verified pinned call `{col:"root_cause", op:"contains", value:"EDI order not processed"}` on
`customer-service-escalation-log-2025` → `matched=34, total=142`. (Substring chosen to be em-dash-safe.)

### 1.6 `aggregate(file, col, fn)`
```python
def aggregate(file: str, col: str, fn: str) -> dict   # fn in {sum,avg,min,max,distinct_count}
```
Single scalar; non-numeric/empty excluded from sum/avg/min/max and reported in `n_excluded`.
Reports `n_considered`. Rounding per policy.
```json
{"name":"aggregate",
 "description":"Compute one scalar over one column: sum|avg|min|max|distinct_count. Non-numeric/empty cells excluded from sum/avg/min/max (reported as n_excluded). Use for totals and cardinalities.",
 "input_schema":{"type":"object","properties":{
   "file":{"type":"string","enum":["sap-s4-customer-master-export","sap-crm-customer-export","order-flow-analysis-export-2025","customer-service-escalation-log-2025"]},
   "col":{"type":"string"},"fn":{"type":"string","enum":["sum","avg","min","max","distinct_count"]}},
  "required":["file","col","fn"]}}
```

### 1.7 `find_mentions(doc, terms)` — the F3/F2-qualitative text primitive (NEW)
```python
def find_mentions(doc: str, terms: list[str]) -> dict
```
Deterministic substring scan over **frozen extracted PDF/TXT text** (NFC-normalized,
case-insensitive). For each term returns `{count, line_indices:[...], snippets:[...]}` (snippets =
the matching lines, ≤3, with line numbers for citation). This is the text analogue of the CSV
tools — "code does the deterministic matching, agent does the reasoning" — and is what makes F3's
6-entity tally and F2's "EDI excluded from RACI" quote **reproducible and tool-sourced** instead of
LLM-counted over prose (D4/D5, FM3, C1/H4). It reads from the committed `pdftext/<doc>.txt`
sidecars (§4 Gate B), never the live PDF.
```json
{"name":"find_mentions",
 "description":"Search the frozen text of a narrative document (PDF/TXT) for each term; return per-term count, line numbers, and matching-line snippets for citation. Case-insensitive, Unicode-normalized substring match. Use to locate and quote where the documents discuss a concept (e.g. which EDI connections are named, whether the RACI mentions EDI).",
 "input_schema":{"type":"object","properties":{
   "doc":{"type":"string","description":"Logical narrative-doc id.","enum":["edi-integration-register-opella-europe","o2c-process-raci-opella-europe","order-management-sop-opella-europe","edi-dispute-resolution-cs-working-notes","sanofi-consumer-healthcare-o2c-sop-2023"]},
   "terms":{"type":"array","items":{"type":"string"},"minItems":1,"maxItems":25}},
  "required":["doc","terms"]}}
```
Verified: `find_mentions("edi-integration-register-opella-europe", ["Carrefour France","Boots
UK","dm","E.Leclerc","Lidl","Coop","All 14 active","6 remaining","connections 1-8","connections
9-14"])` returns hits for all (the register prose contains the 8/6/14 split verbatim); the RACI doc
returns a hit for `"EDI channel process steps are not included"`.

### 1.8 `emit_findings(...)` — terminator + anti-fabrication gate
Maps 1:1 onto `Finding`/`SourceRef`/`ConfidenceTier` in `discovery/models.py` (report renderer
reused unchanged). **Exactly 3 findings.** Two grounding ledgers (D4/FM3): `computed_values`
(must match a number from a tool_result) and `narrative_values` (must carry a verbatim `quote` from
a `find_mentions` snippet) — so qualitative numbers (F3's "6", "14") are first-class and don't fail
the fabrication gate.
```json
{"name":"emit_findings",
 "description":"Call EXACTLY ONCE when investigation is complete; then stop. Emit exactly 3 findings, ranked by business consequence. Every number in computed_values MUST be a value you received from a prior CSV-tool result; every number in narrative_values MUST be backed by a verbatim quote from a find_mentions snippet. Do not introduce any number you did not obtain from a tool.",
 "input_schema":{"type":"object","properties":{"findings":{"type":"array","minItems":3,"maxItems":3,"items":{"type":"object","properties":{
   "id":{"type":"string","enum":["F1","F2","F3"]},
   "title":{"type":"string"},
   "severity":{"type":"string","enum":["high","amber","info"]},
   "confidence":{"type":"string","enum":["verified","amber","gap"]},
   "description":{"type":"string"},
   "business_consequence":{"type":"string"},
   "computed_values":{"type":"array","items":{"type":"object","properties":{"label":{"type":"string"},"value":{"type":"number"},"from_tool":{"type":"string","enum":["group_by","join_diff","filter_count","aggregate"]}},"required":["label","value","from_tool"]}},
   "narrative_values":{"type":"array","items":{"type":"object","properties":{"label":{"type":"string"},"value":{"type":["number","string"]},"doc_id":{"type":"string"},"quote":{"type":"string"}},"required":["label","doc_id","quote"]}},
   "sources":{"type":"array","minItems":2,"items":{"type":"object","properties":{"doc_id":{"type":"string"},"locator":{"type":"string"},"quote":{"type":"string"}},"required":["doc_id"]}}},
  "required":["id","title","severity","confidence","description","business_consequence","sources"]}}},
  "required":["findings"]}}
```

---

## 2. Agent loop pseudo-code + key system-prompt text

### 2.1 Loop (`discovery/agent_loop.py`)
```python
MAX_TURNS = 24
def run_discovery(llm, file_registry, narrative_text, model="claude-opus-4-8") -> dict:
    system   = build_system_prompt(file_registry, narrative_text)   # §2.2
    messages = [{"role":"user","content":
                 "Investigate this Order-to-Cash landscape and emit exactly 3 findings. "
                 "Begin by orienting on each data file per the protocol."}]
    calls_seen, findings = set(), None
    for _ in range(MAX_TURNS):
        resp = llm.messages_with_tools(system=system, messages=messages,
                                       tools=T.SCHEMAS, model=model)   # §2.3, cached, temp 0
        messages.append({"role":"assistant","content":resp.content})
        tool_uses = [b for b in resp.content if b.type == "tool_use"]
        if resp.stop_reason != "tool_use" or not tool_uses:
            messages.append({"role":"user","content":
                "You must finish by calling emit_findings exactly once. Do that now."})
            continue
        results = []
        for tu in tool_uses:
            if tu.name == "emit_findings":
                findings = validate_and_ground(tu.input, transcript=messages)  # §2.4
                results.append(ok(tu.id, "received")); continue
            sig = (tu.name, canonical_args(tu.input))      # sort by[], compare_cols[], terms[]
            note = "(repeat call — identical result as before)" if sig in calls_seen else None
            calls_seen.add(sig)
            results.append(tool_result(tu.id, T.dispatch(tu.name, tu.input), note=note))
        messages.append({"role":"user","content":results})
        if findings is not None:
            return findings
    raise AgentBudgetExceeded(messages)   # -> §5 fallback
```
Five loop guards (cheapest first): `emit_findings`-as-terminator; `MAX_TURNS=24` (~2× the ~12-call
happy path); **dedup** (`canonical_args` sorts list args so "EDI"/order doesn't fork the cache —
fixes FM4/C3); structured-enum tool args (few malformed calls); one forced-finish nudge then fail
over.

### 2.2 System prompt (key text — note the rewrite that fixes the H1 conflict)
```
You are an enterprise process-discovery analyst examining an Order-to-Cash document set for a
company recently carved out from a parent organization. You have generic data tools and a text-
search tool. Discover what is wrong, undocumented, or inconsistent — findings that no single
document states outright. You surface them by COMPUTING over data and CROSS-REFERENCING files.

Documentation says how things are SUPPOSED to work; system exports show how they ACTUALLY work.
The findings live in the GAP between the two. You do not know the findings in advance — derive them.

PROTOCOL (in order):
1. ORIENT. For every data file, call describe() before computing on it. Never reference a column
   or category value you have not seen in a describe() result. Category/channel value SETS come
   from group_by or describe's full-distinct list — NEVER from a sample row or from prose.
2. FORM QUESTIONS from what describe reveals:
   - Two files describing the SAME entities by the SAME key (e.g. customer_id) — do they AGREE on
     commercial terms/limits? Use join_diff. Disagreement is a finding. Report the SCALE
     (how many accounts differ) and the LARGEST single discrepancy.
   - A categorical column (channel, status, root_cause) — how does it DISTRIBUTE? Use group_by.
     A dominant category (large share by COUNT) that the SOP/RACI do not document or assign an
     owner to is a finding. Confirm the documentation gap by QUOTING the relevant document line
     via find_mentions.
   - A categorical value naming a specific failure — how OFTEN? Use filter_count.
   - Named entities/ownership in the narrative docs — locate and COUNT them with find_mentions over
     the exact terms; quote the lines.
3. GROUND. Every quantitative claim MUST come from a tool result, cited by tool: a CSV number from
   group_by/join_diff/filter_count/aggregate (put it in computed_values), or a
   narrative-stated number backed by a verbatim find_mentions quote (put it in narrative_values).
   NEVER estimate a number from a sample or from prose you summarized. Each finding needs >=2
   distinct source docs.
4. STOP. When you have investigated every data file and cross-referenced the narrative docs, rank
   candidate findings by business consequence and call emit_findings with EXACTLY the top 3. Do
   not call any tool afterward.

RULES:
- Code does the math; you do the reasoning. Get every number from a tool; never compute or round
  one yourself. (This REPLACES the old "only report relationships explicitly stated in a document"
  rule, which would wrongly forbid tool-derived numbers.)
- Prefer the most specific tool. Do not repeat a call with identical args; the result won't change.
- Join only files that share the SAME key column — check describe first (order-flow keys customers
  by name, the masters by customer_id; they do NOT share a key).
- On a tool error, read it, fix the argument (usually a column typo from describe), retry once.
- Work files in the listed order for reproducibility.

DATA FILES (use tools): {numbered list}
NARRATIVE DOCS (use find_mentions; full frozen text also below): {numbered list}
NARRATIVE TEXT: {frozen sidecar text of RACI, SOP, EDI register, dispute notes}
```

### 2.3 `messages_with_tools` (new method on `LLMClient`, same cache discipline as `complete`)
- Cache key = `sha256(model ‖ system ‖ json(messages, sort_keys=True, ensure_ascii=False) ‖
  json(tool_schemas, sort_keys=True))[:32]`. **Covers the full multi-turn history** (fixes C3: the
  current `_cache_key` hashes a single prompt — insufficient for tool loops). Because every prior
  `tool_result` is in `messages` and tool results are byte-canonical, turn N is a pure function of
  turns 0..N-1 → identical replay offline/golden.
- Stores plaintext `(system, messages, tool_schemas, response)` alongside the serialized turn for
  debuggability and the Gate-D key recompute.
- `tool_choice={"type":"auto"}`, `temperature=0`, fixed `max_tokens`, pinned model id recorded in
  the run manifest (reject silent alias drift).

### 2.4 `validate_and_ground` (anti-fabrication gate, pure Python, post-emit)
```python
def validate_and_ground(payload, transcript):
    assert {f["id"] for f in payload["findings"]} == {"F1","F2","F3"}     # D9
    tool_numbers   = collect_numbers_from_csv_tool_results(transcript)    # every CSV-tool number
    snippet_texts  = collect_find_mentions_snippets(transcript)          # every returned snippet
    for f in payload["findings"]:
        assert len({s["doc_id"] for s in f["sources"]}) >= 2             # 2-source rule
        for cv in f.get("computed_values", []):
            assert close(cv["value"], tool_numbers)                       # FM3: no smuggled number
        for nv in f.get("narrative_values", []):
            assert _norm(nv["quote"]) in {_norm(s) for s in snippet_texts}# quote must be real text
    return payload
```

---

## 3. How the 3 findings are derived end-to-end (incl. the mostly-qualitative F3)

Each finding has a **pinned scripted trajectory** (the `--scripted` demo default, exact args
below) that the free agent loop mirrors. Numbers are byte-identical because both call the same
`discovery/tools.py` functions.

**F1 — Customer Master conflict (severity HIGH, confidence verified).**
1. `describe(sap-s4-customer-master-export)` and `describe(sap-crm-customer-export)` → confirm shared
   `customer_id`; full-distinct lists surface `migration_source` (Opella 334 / **Sanofi Legacy
   System 6**) and `source` (Opella CRM migration 2024 310 / **manually updated by account manager
   post-carve-out 8**).
2. `join_diff(sap-s4-…, sap-crm-…, key="customer_id", compare_cols=["credit_limit_eur",
   "payment_terms"], rank_by="credit_limit_eur", context_cols_a=["migration_source"],
   context_cols_b=["source"])`.
   → computed: `matched=318, only_in_a=22, only_in_b=0, rows_with_any_difference=307,
   credit_limit_eur n_mismatch=267 sum_delta=5,325,000; payment_terms n_mismatch=228`; row #1 FR001
   `+€600,000`, NET45→NET30; context attaches the two migration-source strings to FR001's row.
   **Headline (true & deterministic): "307 of 318 shared customer accounts disagree between S/4 and
   CRM; the largest is Carrefour FR001 (+€600,000, NET45→NET30); 22 ERP accounts are absent from
   CRM."** Sources: both CSV exports. No PDF needed; F1 is fully code-grounded.

**F2 — 67% of orders via EDI, undocumented/unowned (severity HIGH/AMBER, confidence verified).**
1. `describe(order-flow-analysis-export-2025)` → `channel` is low-cardinality; full-distinct list =
   `EDI/Manual/Fax/Email` (reads vocabulary from data, not prose — D8).
2. `group_by(order-flow-analysis-export-2025, ["channel"], "count")` → EDI **5667 / 67.3% by count**
   (primary). (Optional `value_col="order_value_eur"` shows 66.8% by value; emit cites basis=count.)
3. `find_mentions("o2c-process-raci-opella-europe", ["EDI channel process steps are not included",
   "EDI-related rows excluded", "Manual (telephone) and Email order channels only"])` → quotes the
   RACI's explicit statement that EDI is out of scope/unassigned (D5 — a positive statement, not a
   proven negative).
   **Headline: "EDI carries 67.3% of order volume (5,667 of 8,420 orders/yr) yet the O2C RACI
   explicitly excludes EDI process steps and assigns no owner."** Sources: order-flow CSV + RACI PDF.

**F3 — 6 of 14 EDI connections still Sanofi-managed (severity AMBER/INFO, confidence verified;
strategic tension, non-blocking).** *This is the mostly-qualitative one — here is exactly how it
stays consistent without fabrication:*
1. `find_mentions("edi-integration-register-opella-europe", ["All 14 active", "8 under Opella
   Digital", "6 remaining under Sanofi Shared Services", "connections 9-14", "these six trading
   partners"])` → returns the verbatim prose stating the **14 / 8 / 6** split with line numbers.
   The "6" and "14" go in `narrative_values` (each backed by a quote) — NOT in `computed_values`
   (so they pass the gate). The mangled table is never row-counted (D4).
2. `find_mentions("edi-integration-register-opella-europe", ["Carrefour France","Boots UK
   (legacy)","dm (Drogerie Markt)","E.Leclerc","Lidl Europe","Coop Group (legacy)"])` → confirms the
   six named TSA-managed connections (canonical entity list pinned to register surface forms,
   resolving the "Coop"/"Coop Group", "dm"/"dm (Drogerie Markt)" drift — FM-3-text).
3. `find_mentions("edi-dispute-resolution-cs-working-notes", [same 6 entities, "Sanofi", "TSA"])` →
   second source corroborating the named connections (satisfies ≥2-source rule).
4. Quantitative anchor (computed): `filter_count("customer-service-escalation-log-2025",
   {col:"root_cause", op:"contains", value:"EDI order not processed"})` → **34** EDI-processing
   escalations/yr → goes in `computed_values`. **Folded INTO F3** as evidence of operational
   tension, NOT split into a 4th finding (D9). Labeled precisely: "34 escalations with
   root_cause='EDI order not processed…'", never "34 EDI incidents" (avoids the channel=61 decoy,
   FM-5).
   **Headline: "6 of 14 active EDI connections (Carrefour FR, Boots UK legacy, dm, E.Leclerc, Lidl,
   Coop legacy) remain Sanofi-managed under the TSA; ~34 EDI-not-processed escalations/yr show the
   operational friction. Non-blocking but a strategic dependency."** Sources: EDI register PDF +
   dispute-notes TXT + escalation CSV.

**Why F3 is now consistent:** the 6/14 come from deterministic substring matches over frozen text
(not LLM prose-counting), the entity list is pinned, the 34 is a pinned `filter_count`, and the
fabrication gate accepts narrative numbers only with a verbatim quote.

---

## 4. Determinism contract + 3-run acceptance test

Two independent guarantees, never conflated: **Reproducibility** (same inputs → same output) and
**Non-fabrication** (output is a function of the data, not the cache/prompt).

### 4.1 Sources of nondeterminism — all eliminated
| Source | Fix |
|---|---|
| LLM sampling | temp 0, pinned `claude-opus-4-8`, fixed max_tokens, record resolved model id in manifest; reject drift. |
| Tool-choice variance | The 3 load-bearing trajectories are **pinned** (`--scripted` is demo default); agent path is the show only. Dedup + canonical arg sorting. |
| Multi-turn cache key | Key over **full message history + tool schemas** (§2.3), not one prompt (fixes current `llm.py:46`). |
| Float formatting | One `Decimal/ROUND_HALF_EVEN` policy in tool code; LLM never re-formats a number. |
| CSV row order | `csv.DictReader`, fixed; all list outputs sorted by explicit key. |
| Dict/JSON order | `json.dumps(sort_keys=True, ensure_ascii=False, separators=(",",":"))` for every hashed/serialized payload (change `stages.py` from `indent=2`). |
| Set iteration | Never return a set; `sorted()` everything. `PYTHONHASHSEED=0` in run wrapper as defense-in-depth; tests vary it. |
| Unicode (em-dash, €) | NFC-normalize + casefold in `_norm`; normalize numbers in `_to_number`. |
| PDF extraction | Pin `pypdf==6.12.2`; extract once, assert double-extraction identical, **freeze to committed `pdftext/<doc>.txt` sidecars** with sha256 in manifest; tools read sidecars. |
| JSON parse fallback | `_extract_json`: require fenced JSON, hard-fail on multiple top-level objects (don't silently pick a span). |
| Clock/RNG | No `datetime.now()/random/uuid/time.time` in pipeline; CI grep tripwire. |
| File discovery order | keep `sorted(path.iterdir())`; lock with a test. |

### 4.2 Cache MAY / MUST-NOT (anti-fabrication)
- **MAY cache** (pure functions): real LLM turns keyed by canonical history; tool results keyed by
  `(tool, canonical_args, file_sha256)` — **file hash in key** so editing a CSV invalidates it;
  frozen PDF text keyed by pdf sha256.
- **MUST NOT**: no finding-keyed entries (`"F1"→{…600000…}`); no hand-edited cache files; no tool
  result that doesn't round-trip from recomputation. Golden dir is write-only via `--save-golden`
  from a real online run.

### 4.3 Acceptance test (`pytest`, CI-enforced). PASS iff A–E green per commit; F on schedule.
- **Gate A — tool purity & math truth (no LLM).** Each tool called twice → byte-identical. Values
  recomputed live from the CSVs (not hardcoded) and asserted:
  `group_by(order-flow,[channel],count)` → EDI count==5667, pct_of_rows==67.3, channel set ==
  {EDI,Manual,Fax,Email}; `filter_count(escalation, root_cause contains "EDI order not processed")`
  == 34; `join_diff(erp,crm,customer_id,[credit_limit_eur,payment_terms])` → FR001 delta==600000,
  FR001 ERP NET45/CRM NET30, only_in_a==22, only_in_b==0, rows_with_any_difference==307,
  credit n_mismatch==267, credit sum_delta==5_325_000, terms n_mismatch==228. **This gate proves
  non-fabrication** (numbers re-derived from bytes every run).
- **Gate B — PDF freeze integrity.** Re-extract each PDF; assert sha256 == manifest == committed
  sidecar; assert sidecar contains load-bearing strings: register "All 14 active"+"connections
  9-14"+"6 remaining"; RACI "EDI channel process steps are not included"; SOP manual+email coverage.
- **Gate C — 3-run determinism (headline).** Run full pipeline 3× in separate processes (leg 1
  `PYTHONHASHSEED=0`, legs 2–3 random seeds), offline/golden. Assert the three `discovery-o2c.json`
  outputs byte-identical after `sort_keys=True`; exactly 3 findings {F1,F2,F3}; rendered report
  contains `67.3`, `5,667`, `€600,000`, `307`, `22`, `34`, `6 of 14`.
- **Gate D — cache integrity (anti-fabrication).** For each golden file: recompute its key from the
  stored (model, system, messages, tool_schemas); assert == filename. For each tool-result entry:
  re-run the tool on the hashed file; assert == cached bytes. Structural lint: no entry keyed by a
  finding id/domain.
- **Gate E — provenance / 2-source rule.** Each finding ≥2 distinct doc_ids. F1: both customer
  exports. F2: order-flow CSV + RACI PDF. F3: EDI register PDF + dispute-notes TXT (+ escalation
  CSV). Every `computed_values` matches a tool number; every `narrative_values` has a verbatim
  find_mentions quote.
- **Gate F — cold-model canary (scheduled / pre-demo).** Run cache-cold against the live model,
  regenerate cache, assert C–E still pass. Detects "cached agent looks fine but live agent no longer
  finds F3." Only after A–F pass may `--save-golden` be re-blessed.

---

## 5. Graceful-degradation fallback

`discovery/scripted.py` — the deterministic mirror. On ANY agent-path failure
(`AgentBudgetExceeded | LLMError | ToolProtocolError | GroundingError | offline cache miss`), run
the pinned trajectories from §3 (same `T.join_diff/group_by/filter_count/find_mentions` calls,
fixed order, fixed args), then ONE tool-free `llm.complete_json` call that reasons over the
PRE-COMPUTED facts + frozen narrative text into the 3 findings.
```python
try:
    findings = run_discovery(llm, file_registry, narrative_text)         # agentic (the show)
except (AgentBudgetExceeded, LLMError, ToolProtocolError, GroundingError) as e:
    log.warning("tool loop failed (%s); falling back to scripted plan", e)
    findings = scripted_plan(llm, file_registry, narrative_text)         # deterministic (the tell)
```
Because both paths call identical math/text functions on identical bytes, the €600K, 307, 67.3%,
5667, 34, and 6/14 are byte-identical whichever runs. `--scripted` forces this path; **it is the
demo default** (the open agent loop is shown only from a recorded golden cassette — temp 0 is not a
hard guarantee across provider/backend drift; the scripted path removes model choice entirely).

---

## 6. Build task list (in order)

1. **`discovery/tools.py`** — implement the 7 tools + `SCHEMAS` + `dispatch` + `FILE_REGISTRY` +
   shared helpers (`_q/_round_*`, `_norm`, `_to_number`, `_iter_rows`, `ToolError`). All §1.0
   invariants. This is the only module with arithmetic. (Unblocks everything; the current pipeline
   can't even see the data — loader truncates CSVs to 25 rows.)
2. **PDF freeze step + sidecars** — pin `pypdf==6.12.2` in `requirements.txt`; add a one-time
   extractor that writes `inputs/o2c/pdftext/<doc>.txt`, asserts double-extraction identical,
   records sha256 in the manifest. `find_mentions` + the agent's narrative text read these sidecars.
3. **`discovery/llm.py`** — add `messages_with_tools` (full-history+schemas cache key, temp 0,
   plaintext sidecar store); harden `_extract_json` (fenced-only, fail on multiple top-level
   objects).
4. **`discovery/agent_loop.py`** — `run_discovery` loop (§2.1), `build_system_prompt` (§2.2, with
   the H1 rule rewrite), `canonical_args`, `validate_and_ground` (§2.4), `AgentBudgetExceeded`.
5. **`discovery/scripted.py`** — `scripted_plan` with the §3 pinned trajectories + one tool-free
   synth call.
6. **`run.py`** — wire agent→scripted fail-over; add `--scripted` (demo default) and keep
   `--golden`; set `PYTHONHASHSEED=0`; record resolved model id; replace the `cross_reference`
   doc-dump path. Reuse `Finding`/`SourceRef`/report renderer unchanged (map `emit_findings`
   payload → dataclasses; `narrative_values`/`computed_values` → `SourceRef.locator/quote`).
7. **Determinism plumbing** — `sort_keys=True` on every hashed/serialized payload (`stages.py`,
   cache writes); `sorted()` every set/list before return; refresh `inputs/o2c/_manifest.json`
   (drop the STUB note, add per-file + per-sidecar sha256).
8. **`tests/` (Gates A–F)** — Gate A first (recompute-from-bytes asserts, the keystone
   non-fabrication control), then B/C/D/E; Gate F as a scheduled job. CI grep tripwire for
   `now(|random|uuid|time.time`.

### Corrected golden values for implementers (verified against `prototype/inputs/o2c/`)
EDI = **5,667 orders / 67.3% by count / 66.8% by value**; channels **{EDI, Manual, Fax, Email}**
(NOT "Phone" — Phone is escalation-log only). Customer conflict: **318 shared, 307 differ, 22 ERP-
only, 0 CRM-only**, FR001 **+€600,000** (NET45→NET30), credit n_mismatch **267** sum_delta
**€5,325,000**, terms n_mismatch **228**. EDI-not-processed escalations = **34** (root_cause has a
U+2014 em-dash). EDI connections **6 of 14** Sanofi-managed (Carrefour FR, Boots UK legacy, dm,
E.Leclerc, Lidl, Coop legacy) — from register prose, not table rows. The original draft's
`sum_delta=78,550,000` was fabricated; the task brief's "~5665 orders" and "Phone" channel are
both wrong — tools return data truth.
