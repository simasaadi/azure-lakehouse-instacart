from pathlib import Path
import os
import duckdb

REPO_ROOT = Path(__file__).resolve().parents[1]

DATA_MODE = os.getenv("DATA_MODE", "raw").lower()
if DATA_MODE not in {"raw", "sample"}:
    raise ValueError("DATA_MODE must be 'raw' or 'sample'")

DB_PATH = REPO_ROOT / "warehouse" / f"instacart_{DATA_MODE}.duckdb"


def fail(msg: str) -> None:
    raise SystemExit(f"\n❌ DATA QUALITY CHECK FAILED: {msg}\n")


def check(cond: bool, msg: str) -> None:
    if not cond:
        fail(msg)


def scalar(con: duckdb.DuckDBPyConnection, sql: str):
    return con.execute(sql).fetchone()[0]


def main() -> None:
    if not DB_PATH.exists():
        fail(f"DB not found at {DB_PATH}. Run 01_load_raw_to_duckdb.py first.")

    con = duckdb.connect(str(DB_PATH))

    tables = [
        "raw.aisles",
        "raw.departments",
        "raw.products",
        "raw.orders",
        "raw.order_products__prior",
        "raw.order_products__train",
    ]

    print("=== Table row counts ===")
    counts = {}
    for t in tables:
        c = scalar(con, f"SELECT COUNT(*) FROM {t}")
        counts[t] = c
        print(f"{t}: {c:,}")

    # ---- Hard checks (CI should fail if any of these break) ----
    # 1) Non-empty critical tables
    check(counts["raw.orders"] > 0, "raw.orders is empty")
    check(counts["raw.products"] > 0, "raw.products is empty")

    # 2) Primary key nulls
    orders_id_nulls = scalar(con, "SELECT COUNT(*) FROM raw.orders WHERE order_id IS NULL")
    products_id_nulls = scalar(con, "SELECT COUNT(*) FROM raw.products WHERE product_id IS NULL")
    check(orders_id_nulls == 0, f"raw.orders has NULL order_id rows: {orders_id_nulls}")
    check(products_id_nulls == 0, f"raw.products has NULL product_id rows: {products_id_nulls}")

    # 3) Primary key uniqueness (orders, products)
    orders_distinct = scalar(con, "SELECT COUNT(DISTINCT order_id) FROM raw.orders")
    products_distinct = scalar(con, "SELECT COUNT(DISTINCT product_id) FROM raw.products")
    check(orders_distinct == counts["raw.orders"], "raw.orders order_id is not unique")
    check(products_distinct == counts["raw.products"], "raw.products product_id is not unique")

    # 4) Foreign key integrity (prior/train -> orders/products)
    prior_missing_orders = scalar(
        con,
        """
        SELECT COUNT(*)
        FROM raw.order_products__prior p
        LEFT JOIN raw.orders o USING(order_id)
        WHERE o.order_id IS NULL
        """
    )
    prior_missing_products = scalar(
        con,
        """
        SELECT COUNT(*)
        FROM raw.order_products__prior p
        LEFT JOIN raw.products pr USING(product_id)
        WHERE pr.product_id IS NULL
        """
    )
    train_missing_orders = scalar(
        con,
        """
        SELECT COUNT(*)
        FROM raw.order_products__train t
        LEFT JOIN raw.orders o USING(order_id)
        WHERE o.order_id IS NULL
        """
    )
    train_missing_products = scalar(
        con,
        """
        SELECT COUNT(*)
        FROM raw.order_products__train t
        LEFT JOIN raw.products pr USING(product_id)
        WHERE pr.product_id IS NULL
        """
    )

    check(prior_missing_orders == 0, f"prior rows missing orders: {prior_missing_orders}")
    check(prior_missing_products == 0, f"prior rows missing products: {prior_missing_products}")
    check(train_missing_orders == 0, f"train rows missing orders: {train_missing_orders}")
    check(train_missing_products == 0, f"train rows missing products: {train_missing_products}")

    # 5) Reasonable domain checks
    # order_number should be >= 1
    bad_order_number = scalar(con, "SELECT COUNT(*) FROM raw.orders WHERE order_number < 1")
    check(bad_order_number == 0, f"orders.order_number has values < 1: {bad_order_number}")

    # order_dow expected 0-6
    bad_dow = scalar(con, "SELECT COUNT(*) FROM raw.orders WHERE order_dow NOT BETWEEN 0 AND 6")
    check(bad_dow == 0, f"orders.order_dow outside 0-6: {bad_dow}")

    # order_hour_of_day expected 0-23
    bad_hour = scalar(con, "SELECT COUNT(*) FROM raw.orders WHERE order_hour_of_day NOT BETWEEN 0 AND 23")
    check(bad_hour == 0, f"orders.order_hour_of_day outside 0-23: {bad_hour}")

    # days_since_prior_order should not be negative (NULL allowed)
    neg_days = scalar(con, "SELECT COUNT(*) FROM raw.orders WHERE days_since_prior_order < 0")
    check(neg_days == 0, f"orders.days_since_prior_order negative values: {neg_days}")

    print("\nAll checks passed ✅")


if __name__ == "__main__":
    main()
