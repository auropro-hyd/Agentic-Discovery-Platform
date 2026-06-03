#!/usr/bin/env python3
"""Generate a realistic, larger Procure-to-Pay PO export with engineered findings + noise.

Deterministic (fixed seed) so the embedded findings are exactly reproducible and independently
verifiable. Run:  python3 inputs/p2p/_generate.py   (writes purchase-order-export.csv)

Engineered findings (the same three the demo surfaces), now hidden in realistic scale:
  F1  high-value orders (> EUR 50,000) that carry only a single approval (policy requires two)
  F2  orders committed before a purchase order existed ("maverick spend", policy bans it)
  F3  off-process spend concentrated with a small number of buyers

The bulk of rows are COMPLIANT (correct approvals, PO-first) so the findings must be discovered
against genuine noise, not handed over.
"""
import csv
import random
from pathlib import Path

random.seed(42)  # deterministic

OUT = Path(__file__).resolve().parent / "purchase-order-export.csv"

SUPPLIERS = {
    "Raw Materials": ["Steelco", "AlloyWorks", "MetalSource EU", "ForgePrime"],
    "Components": ["BoltWorks", "PrecisionParts", "GearHaus", "ValveTech"],
    "Consumables": ["LubriCorp", "CleanSupply", "SafetyFirst"],
    "Packaging": ["PackRight", "BoxLine", "WrapCo"],
    "Logistics": ["FreightOne", "CargoLink"],
    "Services": ["MaintainPro", "ConsultEU", "ITPartner"],
}
BUYERS = [f"buyer_{c}" for c in "abcdefgh"]   # 8 buyers
CATEGORIES = list(SUPPLIERS)

rows = []
pid = 1000


def add(category, amount, approval, po_first, buyer):
    global pid
    pid += 1
    rows.append({
        "po_id": f"PO-{pid}",
        "supplier": random.choice(SUPPLIERS[category]),
        "category": category,
        "amount_eur": amount,
        "raised_by": buyer,
        "approval_status": approval,        # approved | single_approval_only
        "po_before_order": po_first,        # yes | no
    })


# ---- compliant bulk (the realistic majority) ----------------------------------
# ~220 routine, correctly-handled orders across all buyers/categories
for _ in range(220):
    cat = random.choice(CATEGORIES)
    amt = random.choice([1500, 2800, 4200, 6500, 9800, 12000, 18500, 24000, 31000, 45000])
    # under threshold -> single approval is fine; over threshold -> properly dual-approved
    approval = "approved"
    add(cat, amt, approval, "yes", random.choice(BUYERS))

# a handful of legitimately large but properly dual-approved orders (decoys: big but compliant)
for amt in [58000, 64000, 72000, 88000, 110000, 150000]:
    add(random.choice(CATEGORIES), amt, "approved", "yes", random.choice(BUYERS))

# ---- F1: high-value orders with ONLY single approval (policy needs two) --------
# 7 orders > 50,000 on single approval (the headline non-compliance)
F1 = [
    ("Raw Materials", 72000, "buyer_a"),
    ("Raw Materials", 95000, "buyer_a"),
    ("Components", 120000, "buyer_d"),   # largest single order
    ("Raw Materials", 61000, "buyer_a"),
    ("Raw Materials", 88000, "buyer_a"),
    ("Components", 67000, "buyer_d"),
    ("Raw Materials", 54000, "buyer_a"),
]
# ---- F2 / F3: maverick spend (po_before_order = no), concentrated in buyer_a ---
# Of the F1 set, exactly 3 were committed before a PO existed (indices 3,4,5):
#   idx 3 = 61k/buyer_a, idx 4 = 88k/buyer_a, idx 5 = 67k/buyer_d
# -> 3 maverick orders (EUR 216,000), 2 of them buyer_a (EUR 149,000 concentration).
MAVERICK_IDX = {3, 4, 5}
for i, (cat, amt, buyer) in enumerate(F1):
    po_first = "no" if i in MAVERICK_IDX else "yes"
    add(cat, amt, "single_approval_only", po_first, buyer)

random.shuffle(rows)

with OUT.open("w", newline="", encoding="utf-8") as fh:
    w = csv.DictWriter(fh, fieldnames=["po_id", "supplier", "category", "amount_eur",
                                       "raised_by", "approval_status", "po_before_order"])
    w.writeheader()
    w.writerows(rows)

print(f"wrote {len(rows)} rows to {OUT.name}")
