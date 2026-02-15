import os

from pathlib import Path
import duckdb

REPO_ROOT = Path(__file__).resolve().parents[1]
DATA_MODE = os.getenv("DATA_MODE", "raw").lower()
if DATA_MODE not in {"raw", "sample"}:
    raise ValueError("DATA_MODE must be 'raw' or 'sample'")

DB_PATH = REPO_ROOT / "warehouse" / f"instacart_{DATA_MODE}.duckdb"
GOLD_DIR = REPO_ROOT / "data" / "gold_parquet"

def main() -> None:
    GOLD_DIR.mkdir(parents=True, exist_ok=True)

    con = duckdb.connect(str(DB_PATH))
    con.execute("CREATE SCHEMA IF NOT EXISTS gold;")

    # Customer-level metrics (great for dashboards/interviews)
    con.execute("""
        CREATE OR REPLACE TABLE gold.mart_customer AS
        WITH base AS (
            SELECT
                user_id,
                COUNT(*)                           AS total_orders,
                MIN(order_number)                  AS first_order_number,
                MAX(order_number)                  AS last_order_number,
                AVG(days_since_prior_order)        AS avg_days_between_orders,
                SUM(CASE WHEN days_since_prior_order IS NULL THEN 1 ELSE 0 END) AS first_order_rows
            FROM silver.fct_orders
            GROUP BY user_id
        )
        SELECT
            user_id,
            total_orders,
            first_order_number,
            last_order_number,
            avg_days_between_orders,
            CASE
                WHEN total_orders = 1 THEN 'one-time'
                WHEN total_orders BETWEEN 2 AND 5 THEN 'repeat'
                WHEN total_orders BETWEEN 6 AND 15 THEN 'loyal'
                ELSE 'power'
            END AS customer_segment
        FROM base;
    """)

    # Product-level metrics (top products + reorder rate)
    con.execute("""
        CREATE OR REPLACE TABLE gold.mart_product AS
        WITH lines AS (
            SELECT
                op.product_id,
                COUNT(*) AS line_items,
                AVG(CAST(op.reordered AS DOUBLE)) AS reorder_rate
            FROM silver.fct_order_products op
            GROUP BY op.product_id
        )
        SELECT
            p.product_id,
            p.product_name,
            p.aisle_id,
            p.department_id,
            l.line_items,
            l.reorder_rate
        FROM lines l
        JOIN silver.dim_products p USING(product_id);
    """)

    # Simple daily/hourly demand profile (operationally intuitive)
    con.execute("""
        CREATE OR REPLACE TABLE gold.mart_demand_profile AS
        SELECT
            order_dow,
            order_hour_of_day,
            COUNT(*) AS orders
        FROM silver.fct_orders
        GROUP BY order_dow, order_hour_of_day;
    """)

    # Export gold
    tables = [
        ("mart_customer", "gold.mart_customer"),
        ("mart_product", "gold.mart_product"),
        ("mart_demand_profile", "gold.mart_demand_profile"),
    ]

    for out_name, full_name in tables:
        out_path = (GOLD_DIR / f"{out_name}.parquet").as_posix()
        print(f"Writing {full_name} -> {out_path}")
        con.execute(f"COPY {full_name} TO '{out_path}' (FORMAT PARQUET);")

    print("\n=== Gold row counts ===")
    for _, full_name in tables:
        cnt = con.execute(f"SELECT COUNT(*) FROM {full_name}").fetchone()[0]
        print(f"{full_name}: {cnt:,}")

    con.close()
    print(f"\nDone. Gold parquet written to: {GOLD_DIR}")

if __name__ == "__main__":
    main()
