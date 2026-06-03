"""Generic, deterministic analysis tools — the ONLY module where arithmetic lives.

"Code does the math, the agent does the reasoning." These tools are exposed to the LLM as
callable functions. They are generic (operation-named, work on any CSV), never finding-specific.

Invariants (every tool):
- Pure function of (file bytes, args): no clock, RNG, network, or global mutable state.
- Total-ordered output: lists sorted by an explicit key; dicts serialized sort_keys=True.
- One rounding policy (Decimal/ROUND_HALF_EVEN): money 2dp, pct 1dp, avg 4dp.
- Provenance on every result: {file, sha256_12, row_count} + the keys/rows that produced a value.
- Logical file ids resolved via FILE_REGISTRY (no raw paths from the model).
- Typed errors returned (not raised) so the agent can self-correct deterministically.
"""
from __future__ import annotations

import csv
import hashlib
import unicodedata
from decimal import Decimal, ROUND_HALF_EVEN
from pathlib import Path
from typing import Any

# Populated at startup from inputs/<domain>/ — maps logical id -> Path.
FILE_REGISTRY: dict[str, Path] = {}
# Frozen narrative text (PDF/TXT) for find_mentions — maps logical id -> text.
DOC_TEXT: dict[str, str] = {}


class ToolError(Exception):
    def __init__(self, code: str, message: str, tool: str = ""):
        self.code, self.message, self.tool = code, message, tool
        super().__init__(message)

    def as_result(self) -> dict:
        return {"error": {"code": self.code, "message": self.message, "tool": self.tool}}


# ---- rounding + normalization helpers -------------------------------------
def _q(x, places):
    if x is None:
        return None
    return float(Decimal(str(x)).quantize(Decimal(10) ** -places, rounding=ROUND_HALF_EVEN))


def _round_money(x): return _q(x, 2)
def _round_pct(x): return _q(x, 1)
def _round_avg(x): return _q(x, 4)


def _norm(s) -> str:
    """NFC + casefold so em-dashes and casing never cause silent misses."""
    return unicodedata.normalize("NFC", str(s)).strip().casefold()


_NULLS = {"", "na", "n/a", "null", "none", "-"}


def _to_number(raw) -> float | None:
    """Parse a numeric value, stripping currency/commas/percent. Returns None if not numeric.
    Callers narrow with `if (v := _to_number(x)) is not None:` so the float branch is type-safe."""
    if raw is None:
        return None
    s = str(raw).strip().replace(",", "").replace("€", "").replace("$", "").replace("%", "")
    if s.lower() in _NULLS:
        return None
    try:
        return float(s)
    except ValueError:
        return None


# ---- registry / io --------------------------------------------------------
def _resolve(file: str, tool: str) -> Path:
    p = FILE_REGISTRY.get(file)
    if p is None:
        raise ToolError("unknown_file",
                        f"unknown file id '{file}'. Available: {sorted(FILE_REGISTRY)}", tool)
    return p


def _sha12(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()[:12]


def _read_rows(path: Path) -> tuple[list[str], list[dict]]:
    with path.open(encoding="utf-8-sig", newline="") as fh:
        reader = csv.DictReader(fh)
        rows = list(reader)
        cols = list(reader.fieldnames or [])
    return cols, rows


def _provenance(file: str, path: Path, n: int) -> dict:
    return {"file": file, "sha256_12": _sha12(path), "row_count": n}


def _need_col(col: str, cols: list[str], tool: str):
    if col not in cols:
        raise ToolError("unknown_column",
                        f"column '{col}' not in {cols}. Call describe first.", tool)


# ---------------------------------------------------------------------------
# describe
# ---------------------------------------------------------------------------
def describe(file: str, sample_rows: int = 5) -> dict:
    path = _resolve(file, "describe")
    cols, rows = _read_rows(path)
    n = len(rows)
    sample_rows = max(1, min(int(sample_rows), 10))
    columns = []
    for c in cols:
        values = [r.get(c, "") for r in rows]
        nonempty = [v for v in values if str(v).strip() != ""]
        numeric_ok = sum(1 for v in values[:1000] if _to_number(v) is not None)
        considered = min(1000, len(values)) or 1
        distinct = sorted({str(v) for v in values})
        col: dict[str, Any] = {
            "name": c,
            "dtype": _infer_dtype(values),
            "nulls": n - len(nonempty),
            "distinct_count": len(distinct),
            "numeric_parse_rate": _round_pct(numeric_ok / considered * 100),
        }
        # surface load-bearing rare values that a 5-row sample would miss
        if len(distinct) <= 25:
            counts = {}
            for v in values:
                counts[str(v)] = counts.get(str(v), 0) + 1
            col["distinct_values"] = sorted(
                ({"value": k, "count": v} for k, v in counts.items()),
                key=lambda d: (-d["count"], d["value"]),
            )
        columns.append(col)
    return {
        "provenance": _provenance(file, path, n),
        "columns": columns,
        "sample": rows[:sample_rows],
    }


def _infer_dtype(values: list) -> str:
    seen = [v for v in values[:1000] if str(v).strip() != ""]
    if not seen:
        return "empty"
    nums = [_to_number(v) for v in seen]
    if all(n is not None and n.is_integer() for n in nums):
        return "int"
    if all(n is not None for n in nums):
        return "float"
    return "str"


# ---------------------------------------------------------------------------
# group_by
# ---------------------------------------------------------------------------
def group_by(file: str, by: list[str], agg: str = "count",
             value_col: str | None = None, top_n: int = 20) -> dict:
    path = _resolve(file, "group_by")
    cols, rows = _read_rows(path)
    for c in by:
        _need_col(c, cols, "group_by")
    if agg == "sum":
        if not value_col:
            raise ToolError("bad_arg", "agg='sum' requires value_col.", "group_by")
        _need_col(value_col, cols, "group_by")

    groups: dict[tuple, dict] = {}
    excluded_nonnumeric = 0
    grand_value = 0.0
    for r in rows:
        gk = tuple(str(r.get(c, "")) for c in by)
        g = groups.setdefault(gk, {"count": 0, "sum": 0.0})
        g["count"] += 1
        if value_col is not None:
            v = _to_number(r.get(value_col))
            if v is not None:
                g["sum"] += v
                grand_value += v
            else:
                excluded_nonnumeric += 1
    total = len(rows)

    def metric(g):
        return g["sum"] if agg == "sum" else g["count"]

    ordered = sorted(groups.items(), key=lambda kv: (-metric(kv[1]), kv[0]))
    out = []
    for gk, g in ordered[:top_n]:
        item = {
            "group": dict(zip(by, gk)),
            "count": g["count"],
            "pct_of_rows": _round_pct(g["count"] / total * 100) if total else 0.0,
        }
        if value_col is not None:
            item["sum"] = _round_money(g["sum"])
            item["pct_of_value"] = _round_pct(g["sum"] / grand_value * 100) if grand_value else 0.0
        out.append(item)
    return {
        "provenance": _provenance(file, path, total),
        "by": by, "agg": agg, "value_col": value_col,
        "grand_total_rows": total,
        "grand_total_value": _round_money(grand_value) if value_col is not None else None,
        "total_groups": len(groups),
        "truncated": len(groups) > top_n,
        "groups": out,
    }


# ---------------------------------------------------------------------------
# join_diff
# ---------------------------------------------------------------------------
def join_diff(file_a: str, file_b: str, key: str, compare_cols: list[str],
              top_n: int = 20, rank_by: str | None = None,
              context_cols_a: list[str] | None = None,
              context_cols_b: list[str] | None = None) -> dict:
    pa = _resolve(file_a, "join_diff")
    pb = _resolve(file_b, "join_diff")
    cols_a, rows_a = _read_rows(pa)
    cols_b, rows_b = _read_rows(pb)
    _need_col(key, cols_a, "join_diff")
    _need_col(key, cols_b, "join_diff")
    for c in compare_cols:
        _need_col(c, cols_a, "join_diff")
        _need_col(c, cols_b, "join_diff")
    context_cols_a = context_cols_a or []
    context_cols_b = context_cols_b or []

    idx_a = {str(r[key]): r for r in rows_a}
    idx_b = {str(r[key]): r for r in rows_b}
    shared = sorted(set(idx_a) & set(idx_b))
    only_a = sorted(set(idx_a) - set(idx_b))
    only_b = sorted(set(idx_b) - set(idx_a))

    # pick numeric ranking column
    numeric_cmp = [c for c in compare_cols
                   if _to_number(idx_a[shared[0]].get(c)) is not None] if shared else []
    rank_col = rank_by or (numeric_cmp[0] if numeric_cmp else compare_cols[0])

    per_col: dict[str, dict[str, Any]] = {
        c: {"n_mismatch": 0, "sum_delta": 0.0} for c in compare_cols}
    rows_any_diff = 0
    matched: list[dict[str, Any]] = []
    for k in shared:
        a, b = idx_a[k], idx_b[k]
        diffs = {}
        any_diff = False
        rank_delta = 0.0
        for c in compare_cols:
            va = _to_number(a.get(c))
            vb = _to_number(b.get(c))
            if va is not None and vb is not None:
                delta = vb - va
                changed = va != vb
                diffs[c] = {"type": "numeric", "a": va, "b": vb,
                            "delta": _round_money(delta), "changed": changed}
                if changed:
                    per_col[c]["n_mismatch"] += 1
                    per_col[c]["sum_delta"] += abs(delta)
                if c == rank_col:
                    rank_delta = abs(delta)
            else:
                changed = str(a.get(c, "")) != str(b.get(c, ""))
                diffs[c] = {"type": "text", "a": a.get(c, ""), "b": b.get(c, ""),
                            "changed": changed}
                if changed:
                    per_col[c]["n_mismatch"] += 1
            any_diff = any_diff or changed
        if any_diff:
            rows_any_diff += 1
        ctx = {}
        for c in context_cols_a:
            ctx[c + " (a)"] = a.get(c, "")
        for c in context_cols_b:
            ctx[c + " (b)"] = b.get(c, "")
        matched.append({"key": k, "rank_delta": rank_delta, "diffs": diffs, "context": ctx})

    matched.sort(key=lambda m: (-m["rank_delta"], m["key"]))
    for m in matched:
        m.pop("rank_delta", None)
    for c in per_col:
        per_col[c]["sum_delta"] = _round_money(per_col[c]["sum_delta"])

    return {
        "provenance_a": _provenance(file_a, pa, len(rows_a)),
        "provenance_b": _provenance(file_b, pb, len(rows_b)),
        "key": key, "rank_by": rank_col,
        "matched_keys": len(shared),
        "only_in_a_count": len(only_a), "only_in_b_count": len(only_b),
        "only_in_a": only_a[:top_n], "only_in_b": only_b[:top_n],
        "rows_with_any_difference": rows_any_diff,
        "per_column": per_col,
        "matched_rows": matched[:top_n],
    }


# ---------------------------------------------------------------------------
# filter_count
# ---------------------------------------------------------------------------
_OPS = {"eq", "ne", "lt", "le", "gt", "ge", "contains", "not_contains",
        "starts_with", "ends_with", "in", "not_in", "is_empty", "not_empty"}


def filter_count(file: str, predicate: dict) -> dict:
    path = _resolve(file, "filter_count")
    cols, rows = _read_rows(path)
    _validate_predicate(predicate, cols, 0)
    matched = []
    for i, r in enumerate(rows, 1):
        if _eval_predicate(predicate, r):
            matched.append(i)
    total = len(rows)
    return {
        "provenance": _provenance(file, path, total),
        "matched": len(matched), "total": total,
        "pct_of_total": _round_pct(len(matched) / total * 100) if total else 0.0,
        "example_row_indices": matched[:5],
    }


def _validate_predicate(p, cols: list[str], depth: int):
    if depth > 6:
        raise ToolError("bad_predicate", "predicate nesting too deep (>6).", "filter_count")
    if not isinstance(p, dict):
        raise ToolError("bad_predicate",
                        f"predicate node must be an object like {{col,op,value}} or "
                        f"{{all:[...]}}; got {type(p).__name__}: {p!r}", "filter_count")
    if "all" in p or "any" in p:
        subs = p.get("all", p.get("any"))
        if not isinstance(subs, list):
            raise ToolError("bad_predicate", "'all'/'any' must be a list of predicates.",
                            "filter_count")
        for sub in subs:
            _validate_predicate(sub, cols, depth + 1)
    elif "not" in p:
        _validate_predicate(p["not"], cols, depth + 1)
    elif "col" in p and "op" in p:
        _need_col(p["col"], cols, "filter_count")
        if p["op"] not in _OPS:
            raise ToolError("bad_predicate", f"op '{p['op']}' not in {sorted(_OPS)}", "filter_count")
    else:
        raise ToolError("bad_predicate", f"malformed predicate node: {p}", "filter_count")


def _eval_predicate(p: dict, row: dict) -> bool:
    if "all" in p:
        return all(_eval_predicate(s, row) for s in p["all"])
    if "any" in p:
        return any(_eval_predicate(s, row) for s in p["any"])
    if "not" in p:
        return not _eval_predicate(p["not"], row)
    col, op, val = p["col"], p["op"], p.get("value")
    cell = row.get(col, "")
    if op == "is_empty":
        return str(cell).strip() == ""
    if op == "not_empty":
        return str(cell).strip() != ""
    if op in ("contains", "not_contains", "starts_with", "ends_with"):
        c, v = _norm(cell), _norm(val)
        r = (v in c if op in ("contains", "not_contains")
             else c.startswith(v) if op == "starts_with" else c.endswith(v))
        return (not r) if op == "not_contains" else r
    if op in ("in", "not_in"):
        vals = {_norm(x) for x in (val or [])}
        r = _norm(cell) in vals
        return (not r) if op == "not_in" else r
    # numeric/text comparisons — compare as numbers when both parse, else as normalized text
    nc = _to_number(cell)
    nv = _to_number(val)
    a: float | str
    b: float | str
    if nc is not None and nv is not None:
        a, b = nc, nv
    else:
        a, b = _norm(cell), _norm(val)
    if op == "eq":
        return a == b
    if op == "ne":
        return a != b
    if op == "lt":
        return a < b       # type: ignore[operator]
    if op == "le":
        return a <= b      # type: ignore[operator]
    if op == "gt":
        return a > b       # type: ignore[operator]
    return a >= b          # type: ignore[operator]  (op == "ge")


# ---------------------------------------------------------------------------
# aggregate
# ---------------------------------------------------------------------------
def aggregate(file: str, col: str, fn: str) -> dict:
    path = _resolve(file, "aggregate")
    cols, rows = _read_rows(path)
    _need_col(col, cols, "aggregate")
    if fn not in {"sum", "avg", "min", "max", "distinct_count"}:
        raise ToolError("bad_arg", f"fn '{fn}' invalid.", "aggregate")
    if fn == "distinct_count":
        return {"provenance": _provenance(file, path, len(rows)),
                "col": col, "fn": fn,
                "value": len(sorted({str(r.get(col, "")) for r in rows}))}
    nums: list[float] = []
    excluded = 0
    for r in rows:
        v = _to_number(r.get(col))
        if v is not None:
            nums.append(v)
        else:
            excluded += 1
    if not nums:
        return {"provenance": _provenance(file, path, len(rows)), "col": col, "fn": fn,
                "value": None, "n_considered": 0, "n_excluded": excluded}
    val = {"sum": sum(nums), "avg": sum(nums) / len(nums),
           "min": min(nums), "max": max(nums)}[fn]
    val = _round_avg(val) if fn == "avg" else _round_money(val)
    return {"provenance": _provenance(file, path, len(rows)), "col": col, "fn": fn,
            "value": val, "n_considered": len(nums), "n_excluded": excluded}


# ---------------------------------------------------------------------------
# find_mentions  (over frozen narrative text)
# ---------------------------------------------------------------------------
def find_mentions(doc: str, terms: list[str]) -> dict:
    text = DOC_TEXT.get(doc)
    if text is None:
        raise ToolError("unknown_file",
                        f"unknown doc id '{doc}'. Available: {sorted(DOC_TEXT)}", "find_mentions")
    lines = text.splitlines()
    norm_lines = [_norm(ln) for ln in lines]
    results = {}
    for term in terms[:25]:
        nt = _norm(term)
        hits = [i for i, nl in enumerate(norm_lines, 1) if nt in nl]
        results[term] = {
            "count": len(hits),
            "line_indices": hits[:25],
            "snippets": [lines[i - 1].strip() for i in hits[:3]],
        }
    return {"doc": doc, "results": results}


# ---------------------------------------------------------------------------
# dispatch + schemas
# ---------------------------------------------------------------------------
_DISPATCH = {
    "describe": describe, "group_by": group_by, "join_diff": join_diff,
    "filter_count": filter_count, "aggregate": aggregate, "find_mentions": find_mentions,
}


def dispatch(name: str, args: dict) -> dict:
    fn = _DISPATCH.get(name)
    if fn is None:
        return {"error": {"code": "bad_arg", "message": f"unknown tool {name}", "tool": name}}
    try:
        return fn(**args)
    except ToolError as e:
        return e.as_result()
    except TypeError as e:
        return {"error": {"code": "bad_arg", "message": str(e), "tool": name}}


# ---------------------------------------------------------------------------
# LLM tool schemas — generated from the live registry so file/doc enums are real
# ---------------------------------------------------------------------------
def schemas() -> list[dict]:
    """Anthropic tool definitions. Call AFTER registry.setup_domain so enums are populated."""
    csv_ids = sorted(FILE_REGISTRY)
    doc_ids = sorted(DOC_TEXT)
    csv_enum = {"type": "string", "enum": csv_ids}
    return [
        {"name": "describe",
         "description": ("Inspect a CSV before computing on it: schema, row_count, per-column "
                         "dtype/null/distinct counts, a head sample, and for low-cardinality "
                         "columns (<=25 distinct) the FULL list of distinct values with counts. "
                         "ALWAYS call this on a file before group_by/aggregate/filter_count/"
                         "join_diff so you use real column names and exact category values."),
         "input_schema": {"type": "object", "properties": {
             "file": csv_enum,
             "sample_rows": {"type": "integer", "minimum": 1, "maximum": 10, "default": 5}},
             "required": ["file"]}},
        {"name": "group_by",
         "description": ("Group a CSV by column(s) and aggregate. Returns per group: count, "
                         "pct_of_rows, and (if value_col given) sum + pct_of_value. Percentages "
                         "cover ALL groups even if only top_n returned. Use to find how a "
                         "categorical column (channel, status, root_cause) distributes."),
         "input_schema": {"type": "object", "properties": {
             "file": csv_enum,
             "by": {"type": "array", "items": {"type": "string"}, "minItems": 1, "maxItems": 3},
             "agg": {"type": "string", "enum": ["count", "sum"], "default": "count"},
             "value_col": {"type": ["string", "null"], "default": None},
             "top_n": {"type": "integer", "minimum": 1, "maximum": 100, "default": 20}},
             "required": ["file", "by"]}},
        {"name": "join_diff",
         "description": ("Outer-join two CSVs on a shared key and report per-row differences. "
                         "Returns matched_keys, keys only_in_a, keys only_in_b, and matched rows "
                         "ranked by largest absolute numeric delta (file_b minus file_a). Each "
                         "compare_col yields a numeric delta or a text changed-flag. context_cols "
                         "carry single-file columns (even with different names) as raw values. Use "
                         "to find data conflicts across two system exports of the same entities."),
         "input_schema": {"type": "object", "properties": {
             "file_a": csv_enum, "file_b": csv_enum,
             "key": {"type": "string"},
             "compare_cols": {"type": "array", "items": {"type": "string"}, "minItems": 1},
             "context_cols_a": {"type": ["array", "null"], "items": {"type": "string"}, "default": None},
             "context_cols_b": {"type": ["array", "null"], "items": {"type": "string"}, "default": None},
             "rank_by": {"type": ["string", "null"], "default": None},
             "top_n": {"type": "integer", "minimum": 1, "maximum": 100, "default": 20}},
             "required": ["file_a", "file_b", "key", "compare_cols"]}},
        {"name": "filter_count",
         "description": ("Count rows matching a SAFE structured predicate (no code). Leaf "
                         "{col,op,value} combined with {all:[]}/{any:[]}/{not:}. String "
                         "comparisons are Unicode-normalized and case-insensitive. Returns matched "
                         "count, total, pct, example row indices. Use to quantify how often a "
                         "labeled condition occurs (e.g. a specific root_cause)."),
         "input_schema": {"type": "object", "properties": {
             "file": csv_enum,
             "predicate": {"$ref": "#/$defs/predicate"}},
             "required": ["file", "predicate"],
             "$defs": {"predicate": {"oneOf": [
                 {"type": "object", "properties": {
                     "col": {"type": "string"},
                     "op": {"type": "string", "enum": sorted(_OPS)},
                     "value": {}}, "required": ["col", "op"], "additionalProperties": False},
                 {"type": "object", "properties": {"all": {"type": "array", "items": {"$ref": "#/$defs/predicate"}, "minItems": 1}}, "required": ["all"], "additionalProperties": False},
                 {"type": "object", "properties": {"any": {"type": "array", "items": {"$ref": "#/$defs/predicate"}, "minItems": 1}}, "required": ["any"], "additionalProperties": False},
                 {"type": "object", "properties": {"not": {"$ref": "#/$defs/predicate"}}, "required": ["not"], "additionalProperties": False}]}}}},
        {"name": "aggregate",
         "description": ("Compute one scalar over one column: sum|avg|min|max|distinct_count. "
                         "Non-numeric/empty cells excluded from sum/avg/min/max. Use for totals "
                         "and cardinalities."),
         "input_schema": {"type": "object", "properties": {
             "file": csv_enum,
             "col": {"type": "string"},
             "fn": {"type": "string", "enum": ["sum", "avg", "min", "max", "distinct_count"]}},
             "required": ["file", "col", "fn"]}},
        {"name": "find_mentions",
         "description": ("Search the frozen text of a narrative document (PDF/TXT) for each term; "
                         "return per-term count, line numbers, and matching-line snippets for "
                         "citation. Case-insensitive, Unicode-normalized substring match. Use to "
                         "locate and quote where the documents discuss a concept (which EDI "
                         "connections are named, whether the RACI mentions EDI)."),
         "input_schema": {"type": "object", "properties": {
             "doc": {"type": "string", "enum": doc_ids},
             "terms": {"type": "array", "items": {"type": "string"}, "minItems": 1, "maxItems": 25}},
             "required": ["doc", "terms"]}},
    ]
