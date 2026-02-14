from pathlib import Path
import duckdb

REPO_ROOT = Path(__file__).resolve().parents[1]
DB_PATH = REPO_ROOT / "warehouse" / "instacart.duckdb"

def fail(msg: str) -> None:
    raise SystemExit(f"\nDATA QUALITY CHECK FAILED: {msg}\n")

def scalar(con, q: str):
    return con.execute(q).fetchone()[0]

def main() -> None:
    con = duckdb.connect(str(DB_PATH))

    # Basic profiling summary (fast signals)
    tables = [
        "raw.aisles",
        "raw.departments",
        "raw.products",
        "raw.orders",
        "raw.order_products__prior",
        "raw.order_products__train",
    ]

    print("=== Table row counts ===")
    for t in tables:
        cnt = scalar(con, f"SELECT COUNT(*) FROM {t}")
        print(f"{t}: {cnt:,}")

    print("\n=== Key integrity checks ===")

    # 1) orders: order_id should be unique and non-null
    total_orders = scalar(con, "SELECT COUNT(*) FROM raw.orders")
    distinct_orders = scalar(con, "SELECT COUNT(DISTINCT order_id) FROM raw.orders")
    null_order_id = scalar(con, "SELECT COUNT(*) FROM raw.orders WHERE order_id IS NULL")
    print(f"orders.order_id nulls: {null_order_id:,}")
    print(f"orders.order_id distinct vs total: {distinct_orders:,} / {total_orders:,}")
    if null_order_id != 0:
        fail("raw.orders has NULL order_id")
    if distinct_orders != total_orders:
        fail("raw.orders has duplicate order_id")

    # 2) products: product_id unique and non-null
    total_products = scalar(con, "SELECT COUNT(*) FROM raw.products")
    distinct_products = scalar(con, "SELECT COUNT(DISTINCT product_id) FROM raw.products")
    null_product_id = scalar(con, "SELECT COUNT(*) FROM raw.products WHERE product_id IS NULL")
    print(f"products.product_id nulls: {null_product_id:,}")
    print(f"products.product_id distinct vs total: {distinct_products:,} / {total_products:,}")
    if null_product_id != 0:
        fail("raw.products has NULL product_id")
    if distinct_products != total_products:
        fail("raw.products has duplicate product_id")

    # 3) order_products: product_id and order_id should exist in dimension tables
    prior_missing_orders = scalar(con, """
        SELECT COUNT(*)
        FROM raw.order_products__prior op
        LEFT JOIN raw.orders o USING(order_id)
        WHERE o.order_id IS NULL
    """)
    prior_missing_products = scalar(con, """
        SELECT COUNT(*)
        FROM raw.order_products__prior op
        LEFT JOIN raw.products p USING(product_id)
        WHERE p.product_id IS NULL
    """)
    print(f"prior rows with missing order_id in orders: {prior_missing_orders:,}")
    print(f"prior rows with missing product_id in products: {prior_missing_products:,}")
    if prior_missing_orders != 0:
        fail("raw.order_products__prior has order_id not found in raw.orders")
    if prior_missing_products != 0:
        fail("raw.order_products__prior has product_id not found in raw.products")

    # 4) sanity: days_since_prior_order should be non-negative where present
    neg_days = scalar(con, """
        SELECT COUNT(*) FROM raw.orders
        WHERE days_since_prior_order IS NOT NULL
          AND days_since_prior_order < 0
    """)
    print(f"orders.days_since_prior_order negative values: {neg_days:,}")
    if neg_days != 0:
        fail("raw.orders has negative days_since_prior_order")

    con.close()
    print("\nAll checks passed ✅")

if __name__ == "__main__":
    main()
