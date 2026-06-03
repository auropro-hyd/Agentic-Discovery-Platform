import csv
import random
from datetime import date, timedelta

SEED = 42


def _dates_in_range(start: date, end: date) -> list[date]:
    days = (end - start).days
    return [start + timedelta(days=i) for i in range(days + 1)]


def generate_cs_escalation_log(path: str) -> None:
    """Doc 06 — 142 rows. Seeds F2 (34 EDI) and cross-domain (19 stockout clusters)."""
    rng = random.Random(SEED)

    FIELDNAMES = ["case_id", "date", "customer", "country", "channel",
                  "root_cause", "resolution_time_hrs", "notes"]

    # 34 EDI-related rows — spread through the year
    edi_dates = _dates_in_range(date(2025, 1, 15), date(2025, 12, 20))
    edi_customers = [
        ("Carrefour France", "FR"), ("E.Leclerc", "FR"), ("Boots UK", "UK"),
        ("dm (Drogerie Markt)", "DE"), ("Lidl Europe", "EU"), ("Coop Group", "EU"),
    ]
    edi_notes_pool = [
        "EDI acknowledgement not received from partner. Manual re-entry required.",
        "Order duplicate detected on EDI channel. Customer notified.",
        "EDI mapping error — incorrect product code in ORDERS message.",
        "EDI connection timeout. Order queued for manual processing.",
        "Retailer EDI portal shows accepted but order not in our system.",
        "third time this quarter for Carrefour FR — escalating to Opella Digital.",
        "Customer threatened to delist Doliprane if EDI reliability does not improve.",
        "Boots UK EDI outage — contacted Sanofi IT helpdesk as per internal note.",
    ]
    # Guarantee both required verbatim phrases appear (pinned to first 2 rows)
    pinned_notes = [
        "third time this quarter for Carrefour FR — escalating to Opella Digital.",
        "Customer threatened to delist Doliprane if EDI reliability does not improve.",
    ]
    edi_rows = []
    for i in range(34):
        cust, country = rng.choice(edi_customers)
        note = pinned_notes[i] if i < len(pinned_notes) else rng.choice(edi_notes_pool)
        edi_rows.append({
            "case_id": f"CS-2025-{100 + i:04d}",
            "date": rng.choice(edi_dates).isoformat(),
            "customer": "Carrefour France" if i == 0 else cust,
            "country": "FR" if i == 0 else country,
            "channel": "EDI",
            "root_cause": "EDI order not processed — manual intervention required",
            "resolution_time_hrs": rng.choice([4, 6, 8, 12, 24, 48]),
            "notes": note,
        })

    # 19 stockout rows — cluster Apr-May and Oct-Nov (cross-domain signal)
    apr_may_dates = (_dates_in_range(date(2025, 4, 1), date(2025, 4, 15))
                     + _dates_in_range(date(2025, 5, 1), date(2025, 5, 10)))
    oct_nov_dates = (_dates_in_range(date(2025, 10, 6), date(2025, 10, 20))
                     + _dates_in_range(date(2025, 11, 1), date(2025, 11, 8)))
    stockout_dates = (rng.sample(apr_may_dates, 10) + rng.sample(oct_nov_dates, 9))
    stockout_customers = [
        ("Carrefour France", "FR"), ("E.Leclerc", "FR"), ("Tesco UK", "UK"),
        ("Boots UK", "UK"), ("Mercadona", "ES"),
    ]
    stockout_notes_pool = [
        "Customer reporting out-of-stock on Doliprane 500mg in-store. Escalated to supply chain.",
        "Allegra 120mg unavailable at Boots UK — store running promotions this week.",
        "Stockout on Buscopan DACH — customer requesting urgent replenishment.",
        "Customer flagged stockout and requested compensation credit.",
        "Repeated stockout on same SKU — customer requested urgent call with commercial team.",
    ]
    stockout_rows = []
    for i, d_val in enumerate(stockout_dates):
        cust, country = rng.choice(stockout_customers)
        stockout_rows.append({
            "case_id": f"CS-2025-{200 + i:04d}",
            "date": d_val.isoformat(),
            "customer": cust,
            "country": country,
            "channel": rng.choice(["EDI", "Manual", "Email"]),
            "root_cause": "Stockout complaint — product unavailable",
            "resolution_time_hrs": rng.choice([24, 48, 72]),
            "notes": rng.choice(stockout_notes_pool),
        })

    # Remaining 89 generic rows
    generic_dates = _dates_in_range(date(2025, 1, 3), date(2025, 12, 20))
    generic_customers = edi_customers + [("Tesco UK", "UK"), ("Mercadona", "ES")]
    generic_causes = [
        "Pricing discrepancy on invoice",
        "Delivery short — quantity variance",
        "Customer query — payment application",
        "Returns authorisation requested",
        "Credit note dispute",
        "Delivery date change requested",
        "Product substitution query",
    ]
    generic_notes_pool = [
        "Resolved by account manager — credit note issued.",
        "Price list version mismatch. Updated in system.",
        "Short delivery confirmed by logistics — credit raised.",
        "Customer accepted revised delivery date.",
        "Awaiting sign-off from Credit Controller.",
    ]
    generic_rows = []
    for i in range(89):
        cust, country = rng.choice(generic_customers)
        generic_rows.append({
            "case_id": f"CS-2025-{400 + i:04d}",
            "date": rng.choice(generic_dates).isoformat(),
            "customer": cust,
            "country": country,
            "channel": rng.choice(["EDI", "Manual", "Email", "Phone"]),
            "root_cause": rng.choice(generic_causes),
            "resolution_time_hrs": rng.randint(1, 96),
            "notes": rng.choice(generic_notes_pool),
        })

    all_rows = edi_rows + stockout_rows + generic_rows
    rng.shuffle(all_rows)
    # Re-number case IDs after shuffle for chronological plausibility
    all_rows.sort(key=lambda r: r["date"])
    for i, row in enumerate(all_rows):
        row["case_id"] = f"CS-2025-{i + 1:04d}"

    with open(path, "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=FIELDNAMES)
        writer.writeheader()
        writer.writerows(all_rows)


# ── Shared account master ─────────────────────────────────────────────────

# These 8 accounts appear in both S4 and CRM with conflicting values (F1).
# The 6 Sanofi-migrated accounts are the same 6 managed by Sanofi EDI (F3 linkage).
TOP_ACCOUNTS = [
    # (id, name, country, s4_limit, crm_limit, s4_terms, crm_terms, sanofi_migrated)
    ("FR001", "Carrefour France",    "FR", 1_800_000, 2_400_000, "NET45", "NET30", True),
    ("FR002", "E.Leclerc",           "FR", 1_100_000, 1_400_000, "NET45", "NET30", True),
    ("UK001", "Boots UK",            "UK", 1_200_000, 1_550_000, "NET45", "NET30", True),
    ("UK002", "Tesco UK",            "UK", 1_000_000, 1_350_000, "NET45", "NET30", False),
    ("DE001", "dm (Drogerie Markt)", "DE",   950_000, 1_150_000, "NET45", "NET30", True),
    ("EU001", "Lidl Europe",         "EU",   850_000, 1_000_000, "NET45", "NET30", True),
    ("EU002", "Coop Group",          "EU",   800_000,   950_000, "NET45", "NET30", True),
    ("ES001", "Mercadona",           "ES",   750_000,   900_000, "NET45", "NET30", False),
]

# Remaining 332 accounts in S4 — smaller, consistent, no discrepancy
def _generic_accounts(start_id: int, count: int, rng: random.Random) -> list[dict]:
    countries = ["FR", "DE", "UK", "ES", "IT", "BE", "NL", "AT", "CH", "PL"]
    account_types = ["Pharmacy", "Independent Retailer", "Hospital", "Wholesaler", "Co-op"]
    rows = []
    for i in range(count):
        cid = start_id + i
        country = rng.choice(countries)
        limit = rng.choice([50_000, 75_000, 100_000, 150_000, 200_000, 250_000, 300_000])
        rows.append({
            "customer_id": f"CUST{cid:05d}",
            "customer_name": f"{rng.choice(account_types)} Account {cid}",
            "country": country,
            "credit_limit_eur": limit,
            "payment_terms": rng.choice(["NET30", "NET45", "NET60"]),
            "status": "ACTIVE",
            "migration_source": "Opella",
            "migration_date": "",
        })
    return rows


def generate_s4_customer_master(path: str) -> None:
    """Doc 08 — 340 rows. 6 Sanofi-migrated accounts. Credit limits lower than CRM."""
    rng = random.Random(SEED + 1)

    FIELDNAMES = ["customer_id", "customer_name", "country", "credit_limit_eur",
                  "payment_terms", "status", "migration_source", "migration_date"]

    rows = []
    for acct in TOP_ACCOUNTS:
        cid, name, country, s4_limit, _, s4_terms, _, migrated = acct
        rows.append({
            "customer_id": cid,
            "customer_name": name,
            "country": country,
            "credit_limit_eur": s4_limit,
            "payment_terms": s4_terms,
            "status": "ACTIVE",
            "migration_source": "Sanofi Legacy System" if migrated else "Opella",
            "migration_date": "2024-05-01" if migrated else "",
        })

    rows += _generic_accounts(start_id=1000, count=332, rng=rng)

    with open(path, "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=FIELDNAMES)
        writer.writeheader()
        writer.writerows(rows)


def generate_crm_customer_export(path: str) -> None:
    """Doc 09 — 318 rows (22 fewer than S4). Higher credit limits for top accounts.
    Source: 'manually updated by account manager post-carve-out'. NET30 payment terms."""
    rng = random.Random(SEED + 2)

    FIELDNAMES = ["customer_id", "customer_name", "country", "credit_limit_eur",
                  "payment_terms", "last_updated_by", "source"]

    rows = []
    for acct in TOP_ACCOUNTS:
        cid, name, country, _, crm_limit, _, crm_terms, _ = acct
        rows.append({
            "customer_id": cid,
            "customer_name": name,
            "country": country,
            "credit_limit_eur": crm_limit,
            "payment_terms": crm_terms,
            "last_updated_by": rng.choice(["Thomas Beaumont", "Raj Patel",
                                           "Sophie Marchetti", "Account Manager EU"]),
            "source": "manually updated by account manager post-carve-out",
        })

    # 310 generic accounts — 22 fewer than S4's 332 generic accounts
    generic = _generic_accounts(start_id=1000, count=310, rng=rng)
    for g in generic:
        rows.append({
            "customer_id": g["customer_id"],
            "customer_name": g["customer_name"],
            "country": g["country"],
            "credit_limit_eur": g["credit_limit_eur"],
            "payment_terms": g["payment_terms"],
            "last_updated_by": "System migration",
            "source": "Opella CRM migration 2024",
        })

    with open(path, "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=FIELDNAMES)
        writer.writeheader()
        writer.writerows(rows)


def generate_order_flow_analysis(path: str) -> None:
    """Doc 10 — 8,420 rows. EDI 67.3%, manual 21.4%, email 9.1%, fax 2.2%.
    EDI fulfilment drops to ~59% in Apr-May and Oct-Nov 2025 (cross-domain signal)."""
    rng = random.Random(SEED + 3)

    FIELDNAMES = ["order_id", "order_date", "customer", "country", "channel",
                  "sku", "units_ordered", "order_value_eur",
                  "fulfilment_status", "fulfilment_date", "notes"]

    TOTAL = 8420
    # Exact channel counts that hit the required percentages
    channel_counts = {"EDI": 5667, "Manual": 1802, "Email": 767, "Fax": 184}
    # 5667 + 1802 + 767 + 184 = 8420

    SKUS = ["AL120-EU", "AL180-EU", "DP500-FR", "DP1000-FR",
            "MG375-FR", "BS10-DE", "FX60-UK", "CAD400-FR"]
    CUSTOMERS = [
        ("Carrefour France", "FR"), ("E.Leclerc", "FR"), ("Boots UK", "UK"),
        ("Tesco UK", "UK"), ("dm (Drogerie Markt)", "DE"),
        ("Lidl Europe", "EU"), ("Coop Group", "EU"), ("Mercadona", "ES"),
    ]
    all_dates = _dates_in_range(date(2025, 1, 3), date(2025, 12, 20))

    # Identify cluster dates for EDI fulfilment degradation
    cluster_dates = set(
        _dates_in_range(date(2025, 4, 1), date(2025, 5, 31)) +
        _dates_in_range(date(2025, 10, 1), date(2025, 11, 30))
    )

    def fulfilment(channel: str, order_date: date) -> tuple[str, str]:
        """Return (status, fulfilment_date). EDI degrades in cluster periods."""
        in_cluster = order_date in cluster_dates
        if channel == "EDI":
            prob = 0.59 if in_cluster else 0.91
        elif channel == "Manual":
            prob = 0.82
        elif channel == "Email":
            prob = 0.85
        else:  # Fax
            prob = 0.78
        if rng.random() < prob:
            lag = rng.randint(1, 5)
            return "FULFILLED", (order_date + timedelta(days=lag)).isoformat()
        else:
            return "NOT_FULFILLED", ""

    rows = []
    order_num = 1
    for channel, count in channel_counts.items():
        for _ in range(count):
            cust, country = rng.choice(CUSTOMERS)
            sku = rng.choice(SKUS)
            units = rng.randint(50, 2000)
            price_per_unit = rng.uniform(2.5, 18.0)
            order_date = rng.choice(all_dates)
            status, fulfil_date = fulfilment(channel, order_date)
            rows.append({
                "order_id": f"ORD-2025-{order_num:05d}",
                "order_date": order_date.isoformat(),
                "customer": cust,
                "country": country,
                "channel": channel,
                "sku": sku,
                "units_ordered": units,
                "order_value_eur": round(units * price_per_unit, 2),
                "fulfilment_status": status,
                "fulfilment_date": fulfil_date,
                "notes": "",
            })
            order_num += 1

    rng.shuffle(rows)

    with open(path, "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=FIELDNAMES)
        writer.writeheader()
        writer.writerows(rows)
