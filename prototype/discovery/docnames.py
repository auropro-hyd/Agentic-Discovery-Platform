"""Business-friendly document names — the citation chokepoint.

GENERIC: friendly names are DERIVED from the filename (acronym-aware), so the platform works on
ANY engagement's documents with zero setup. An optional per-engagement override map can refine
wording where a client wants specific phrasing, but it is never required and unknown ids never
hard-fail — they fall back to a clean derived name.

The stakeholder report must NEVER show a raw filename, column, locator, or tool name. Everything
client-facing routes a doc id through friendly()/business_phrase_list() here.
"""
from __future__ import annotations

import re

_KNOWN_EXT = (".csv", ".pdf", ".txt", ".json", ".md")

# Tokens that should render upper-case (acronyms) or with specific casing when derived from a
# filename. Generic across domains, not O2C-specific — these are common enterprise terms.
_ACRONYMS = {
    "sap", "erp", "crm", "edi", "raci", "o2c", "p2p", "r2r", "sop", "kpi", "sku", "api",
    "ar", "ap", "gl", "hr", "it", "wms", "tms", "mdm", "ui", "ux", "pdf", "csv", "eu", "uk",
    "us", "tsa", "s4", "s4hana", "qa", "sla", "poc", "mvp", "cs",
}
# Specific display casing (whole-token, lower-cased key).
_CASED = {"s4hana": "S/4HANA", "s4": "S/4HANA", "q1": "Q1", "q2": "Q2", "q3": "Q3", "q4": "Q4"}
# Generic suffixes that, when present, give a clean "kind" label.
_KIND_HINTS = [
    (re.compile(r"export|extract|dump|data", re.I), "System export"),
    (re.compile(r"\blog\b|logs", re.I), "System export"),
    (re.compile(r"sop|policy|procedure|guide|register|raci|standard", re.I),
     "Process documentation"),
    (re.compile(r"notes|minutes|transcript|email|memo", re.I), "Notes"),
    (re.compile(r"review|assessment|analysis", re.I), "Review notes"),
    (re.compile(r"\b20\d\d\b.*sop|inherited|legacy", re.I), "Inherited reference"),
]

# OPTIONAL per-engagement overrides (id -> {friendly, kind, phrase}). Empty by default; the demo
# can load one if a client wants specific wording. Generalization does NOT depend on this.
OVERRIDES: dict[str, dict] = {}

# Back-compat: some code imports DOC_META. It now reflects whatever overrides are loaded.
DOC_META = OVERRIDES


def load_overrides(mapping: dict) -> None:
    OVERRIDES.clear()
    OVERRIDES.update(mapping or {})


def stem(doc_id: str) -> str:
    for ext in _KNOWN_EXT:
        if doc_id.lower().endswith(ext):
            return doc_id[: -len(ext)]
    return doc_id


def _titleise_token(tok: str) -> str:
    low = tok.lower()
    if low in _CASED:
        return _CASED[low]
    if low in _ACRONYMS:
        return tok.upper()
    return tok[:1].upper() + tok[1:] if tok else tok


# Tokens dropped from derived document names so a citation reads as the document TYPE rather than
# trailing client/region qualifiers (e.g. "Credit Management Policy", not "...<Client> Europe").
# NO client name is hardcoded — the engine is client-agnostic. The detected client name (if any)
# and generic geographic region words are populated per-run via set_noise_words(); only neutral
# filler is kept by default.
_DEFAULT_NOISE: set[str] = set()           # nothing client-specific baked in
_NOISE_WORDS: set[str] = set(_DEFAULT_NOISE)


def set_noise_words(words) -> None:
    """Replace the per-run noise list (e.g. the detected client name + region words for this
    engagement). Call once per run; resets to default first so runs don't leak into each other."""
    _NOISE_WORDS.clear()
    _NOISE_WORDS.update(_DEFAULT_NOISE)
    _NOISE_WORDS.update(w.lower() for w in (words or []))


def add_noise_words(words) -> None:
    _NOISE_WORDS.update(w.lower() for w in (words or []))


def _derive_friendly(doc_id: str) -> str:
    s = stem(doc_id)
    # split ONLY on separators (-, _, space). Keep alphanumeric tokens whole so acronyms like
    # o2c / s4 / p2p / q4 / s4hana survive intact rather than splitting into "O 2 C".
    parts = [p for p in re.split(r"[-_\s]+", s) if p and p.lower() not in _NOISE_WORDS]
    return " ".join(_titleise_token(p) for p in parts) or s


def _derive_kind(doc_id: str) -> str:
    s = stem(doc_id)
    for rx, label in _KIND_HINTS:
        if rx.search(s):
            return label
    return "Document"


def friendly(doc_id: str) -> str:
    o = OVERRIDES.get(stem(doc_id))
    if o and o.get("friendly"):
        return o["friendly"]
    return _derive_friendly(doc_id)


def kind(doc_id: str) -> str:
    o = OVERRIDES.get(stem(doc_id))
    if o and o.get("kind"):
        return o["kind"]
    return _derive_kind(doc_id)


def phrase(doc_id: str) -> str:
    o = OVERRIDES.get(stem(doc_id))
    if o and o.get("phrase"):
        return o["phrase"]
    return f"your {friendly(doc_id)}"


def detect_client(texts: list[str], min_mentions: int = 3) -> str | None:
    """Best-effort: infer the client/organisation name from document content.

    Looks for a capitalised proper-noun phrase (1-3 words, optionally with a corporate suffix like
    Inc/Ltd/GmbH/SA) that recurs across the documents. Returns the name only if it clears a
    confidence threshold (appears >= min_mentions times AND in >= 2 documents); otherwise None, so
    callers fall back to neutral phrasing rather than a wrong or placeholder name.
    """
    import re as _re
    from collections import Counter

    # candidate org phrase: Capitalised word(s), optional corp suffix
    suffix = r"(?:\s+(?:Inc|LLC|Ltd|Limited|GmbH|AG|S\.?A\.?|N\.?V\.?|PLC|Group|Holdings|" \
             r"Corporation|Corp|Company|Co|Manufacturing|Pharmaceuticals|Healthcare|Industries))?"
    pat = _re.compile(rf"\b([A-Z][a-zA-Z&]+(?:\s+[A-Z][a-zA-Z&]+){{0,2}}){suffix}\b")
    # very common non-org capitalised words to ignore
    stop = {"the", "order", "customer", "credit", "purchase", "supplier", "finance", "policy",
            "europe", "european", "process", "system", "data", "report", "review", "notes",
            "service", "management", "integration", "register", "guide", "analysis", "export",
            "log", "sop", "raci", "edi", "crm", "erp", "sap", "monday", "tuesday", "wednesday",
            "thursday", "friday", "q1", "q2", "q3", "q4", "north", "south", "east", "west"}

    per_doc_seen = []
    counts = Counter()
    for t in texts:
        seen_here = set()
        for m in pat.finditer(t or ""):
            name = m.group(1).strip()
            low = name.lower()
            if low in stop or all(w in stop for w in low.split()):
                continue
            if len(low) < 3 or low.split()[0] in stop:
                continue
            counts[name] += 1
            seen_here.add(name)
        per_doc_seen.append(seen_here)

    if not counts:
        return None
    name, n = counts.most_common(1)[0]
    docs_with = sum(1 for s in per_doc_seen if name in s)
    if n >= min_mentions and docs_with >= 2:
        return name
    return None


def business_phrase_list(doc_ids: list[str]) -> str:
    """Join several sources into a readable clause. If two same-vendor system exports appear
    together (e.g. an ERP and a CRM customer export), collapse them into one natural phrase."""
    ids = []
    for d in doc_ids:
        s = stem(d)
        if s not in ids:
            ids.append(s)
    phrases = [phrase(i) for i in ids]
    phrases = _collapse_pairs(ids, phrases)
    if not phrases:
        return ""
    if len(phrases) == 1:
        return phrases[0]
    return ", ".join(phrases[:-1]) + " and " + phrases[-1]


def _collapse_pairs(ids: list[str], phrases: list[str]) -> list[str]:
    """Conservative generic collapse: if EXACTLY two ids share the same trailing two words
    (e.g. both end in 'Customer Export'), merge them into one natural phrase. Otherwise leave
    every phrase as-is. Domain-agnostic and safe — never mangles three-way cases."""
    # only collapse on a shared DATA-TYPE tail (e.g. "Customer Export"), never on a generic org
    # suffix like "Opella Europe"
    _COLLAPSIBLE_NOUNS = {"export", "exports", "extract", "dump", "log", "logs", "feed", "table"}

    def words(i):
        return _derive_friendly(i).split()

    def tail(i):
        w = words(i)
        if len(w) >= 2 and w[-1].lower() in _COLLAPSIBLE_NOUNS:
            return tuple(x.lower() for x in w[-2:])
        return ()

    groups: dict[tuple, list[int]] = {}
    for idx, i in enumerate(ids):
        groups.setdefault(tail(i), []).append(idx)

    out, used = [], set()
    for idx, i in enumerate(ids):
        if idx in used:
            continue
        t = tail(i)
        peers = groups.get(t, [])
        if t and len(peers) == 2 and idx == peers[0]:
            a, b = peers
            used.update(peers)
            lead_a = " ".join(words(ids[a])[:-2]) or words(ids[a])[0]
            lead_b = " ".join(words(ids[b])[:-2]) or words(ids[b])[0]
            noun = " ".join(words(i)[-2:]) + "s"
            out.append(f"your {lead_a} and {lead_b} {noun}")
        elif idx not in used:
            out.append(phrase(i))
    return out
