import csv, os, sys, tempfile
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from generators.o2c_csvs import (
    generate_cs_escalation_log,
    generate_s4_customer_master,
    generate_crm_customer_export,
    generate_order_flow_analysis,
)


def test_escalation_log_row_count():
    with tempfile.TemporaryDirectory() as d:
        path = os.path.join(d, "escalation.csv")
        generate_cs_escalation_log(path)
        with open(path) as f:
            rows = list(csv.DictReader(f))
    assert len(rows) == 142


def test_escalation_log_edi_count():
    with tempfile.TemporaryDirectory() as d:
        path = os.path.join(d, "escalation.csv")
        generate_cs_escalation_log(path)
        with open(path) as f:
            rows = list(csv.DictReader(f))
    edi = [r for r in rows if "EDI order not processed" in r["root_cause"]]
    assert len(edi) == 34


def test_escalation_log_stockout_clusters():
    """19 stockout rows must fall in Apr-May or Oct-Nov 2025."""
    with tempfile.TemporaryDirectory() as d:
        path = os.path.join(d, "escalation.csv")
        generate_cs_escalation_log(path)
        with open(path) as f:
            rows = list(csv.DictReader(f))
    stockout = [r for r in rows if "Stockout" in r["root_cause"]]
    assert len(stockout) == 19
    from datetime import date
    for r in stockout:
        d_val = date.fromisoformat(r["date"])
        in_apr_may = d_val.month in (4, 5) and d_val.year == 2025
        in_oct_nov = d_val.month in (10, 11) and d_val.year == 2025
        assert in_apr_may or in_oct_nov, f"Stockout row date {r['date']} outside expected clusters"


def test_escalation_log_contains_key_free_text():
    with tempfile.TemporaryDirectory() as d:
        path = os.path.join(d, "escalation.csv")
        generate_cs_escalation_log(path)
        content = open(path).read()
    assert "threatened to delist Doliprane" in content
    assert "third time this quarter for Carrefour FR" in content


def test_s4_row_count():
    with tempfile.TemporaryDirectory() as d:
        path = os.path.join(d, "s4.csv")
        generate_s4_customer_master(path)
        with open(path) as f:
            rows = list(csv.DictReader(f))
    assert len(rows) == 340


def test_s4_migration_flags():
    with tempfile.TemporaryDirectory() as d:
        path = os.path.join(d, "s4.csv")
        generate_s4_customer_master(path)
        with open(path) as f:
            rows = list(csv.DictReader(f))
    migrated = [r for r in rows if r["migration_source"] == "Sanofi Legacy System"]
    assert len(migrated) == 6
    migration_names = {r["customer_name"] for r in migrated}
    assert migration_names == {"Carrefour France", "Boots UK", "dm (Drogerie Markt)",
                               "E.Leclerc", "Lidl Europe", "Coop Group"}
    assert all(r["migration_date"] == "2024-05-01" for r in migrated)


def test_s4_top_account_credit_limits():
    with tempfile.TemporaryDirectory() as d:
        path = os.path.join(d, "s4.csv")
        generate_s4_customer_master(path)
        with open(path) as f:
            rows = list(csv.DictReader(f))
    by_name = {r["customer_name"]: r for r in rows}
    assert by_name["Carrefour France"]["credit_limit_eur"] == "1800000"
    assert by_name["Boots UK"]["credit_limit_eur"] == "1200000"
    assert by_name["dm (Drogerie Markt)"]["credit_limit_eur"] == "950000"


def test_crm_row_count_is_22_fewer_than_s4():
    with tempfile.TemporaryDirectory() as d:
        s4_path = os.path.join(d, "s4.csv")
        crm_path = os.path.join(d, "crm.csv")
        generate_s4_customer_master(s4_path)
        generate_crm_customer_export(crm_path)
        with open(s4_path) as f:
            s4_rows = list(csv.DictReader(f))
        with open(crm_path) as f:
            crm_rows = list(csv.DictReader(f))
    assert len(s4_rows) == 340
    assert len(crm_rows) == 318
    assert len(s4_rows) - len(crm_rows) == 22


def test_crm_credit_limits_higher_than_s4():
    with tempfile.TemporaryDirectory() as d:
        crm_path = os.path.join(d, "crm.csv")
        generate_crm_customer_export(crm_path)
        with open(crm_path) as f:
            rows = list(csv.DictReader(f))
    by_name = {r["customer_name"]: r for r in rows}
    assert by_name["Carrefour France"]["credit_limit_eur"] == "2400000"
    assert by_name["Boots UK"]["credit_limit_eur"] == "1550000"
    assert by_name["Carrefour France"]["payment_terms"] == "NET30"
    assert by_name["Carrefour France"]["source"] == "manually updated by account manager post-carve-out"


def test_order_flow_row_count():
    with tempfile.TemporaryDirectory() as d:
        path = os.path.join(d, "orders.csv")
        generate_order_flow_analysis(path)
        with open(path) as f:
            rows = list(csv.DictReader(f))
    assert len(rows) == 8420


def test_order_flow_channel_split():
    with tempfile.TemporaryDirectory() as d:
        path = os.path.join(d, "orders.csv")
        generate_order_flow_analysis(path)
        with open(path) as f:
            rows = list(csv.DictReader(f))
    total = len(rows)
    edi_pct    = sum(1 for r in rows if r["channel"] == "EDI")    / total
    manual_pct = sum(1 for r in rows if r["channel"] == "Manual") / total
    email_pct  = sum(1 for r in rows if r["channel"] == "Email")  / total
    fax_pct    = sum(1 for r in rows if r["channel"] == "Fax")    / total
    assert 0.668 <= edi_pct    <= 0.678, f"EDI% = {edi_pct:.3f}"
    assert 0.209 <= manual_pct <= 0.219, f"Manual% = {manual_pct:.3f}"
    assert 0.086 <= email_pct  <= 0.096, f"Email% = {email_pct:.3f}"
    assert 0.017 <= fax_pct    <= 0.027, f"Fax% = {fax_pct:.3f}"


def test_order_flow_edi_fulfilment_drops_in_clusters():
    """EDI fulfilment must drop to ≤61% during Apr-May and Oct-Nov clusters."""
    with tempfile.TemporaryDirectory() as d:
        path = os.path.join(d, "orders.csv")
        generate_order_flow_analysis(path)
        with open(path) as f:
            rows = list(csv.DictReader(f))
    from datetime import date
    def in_cluster(r):
        d_val = date.fromisoformat(r["order_date"])
        return (r["channel"] == "EDI" and
                ((d_val.month in (4, 5) and d_val.year == 2025) or
                 (d_val.month in (10, 11) and d_val.year == 2025)))
    cluster_rows = [r for r in rows if in_cluster(r)]
    fulfilled = [r for r in cluster_rows if r["fulfilment_status"] == "FULFILLED"]
    rate = len(fulfilled) / len(cluster_rows)
    assert rate <= 0.62, f"Cluster EDI fulfilment rate = {rate:.3f}, expected ≤0.62"
    normal_edi = [r for r in rows if r["channel"] == "EDI" and not in_cluster(r)]
    normal_rate = sum(1 for r in normal_edi if r["fulfilment_status"] == "FULFILLED") / len(normal_edi)
    assert normal_rate >= 0.85, f"Normal EDI fulfilment rate = {normal_rate:.3f}, expected ≥0.85"
