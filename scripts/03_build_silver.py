from pathlib import Path
import duckdb

REPO_ROOT = Path(__file__).resolve().parents[1]
DB_PATH = REPO_ROOT / "warehouse" / "instacart.duckdb"
SILVER_DIR = REPO_ROOT / "data" / "silver_parquet"

def main() -> None:
    SILVER_DIR.mkdir(parents=True, exist_ok=True)

    con = duckdb.connect(str(DB_PATH))
    con.execute("CREATE SCHEMA IF NOT EXISTS silver;")

    # Dimensions
    con.execute("""
        CREATE OR REPLACE TABLE silver.dim_departments AS
        SELECT
            CAST(department_id AS INTEGER) AS department_id,
            CAST(department AS VARCHAR)    AS department
        FROM raw.departments;
    """)

    con.execute("""
        CREATE OR REPLACE TABLE silver.dim_aisles AS
        SELECT
            CAST(aisle_id AS INTEGER) AS aisle_id,
            CAST(aisle AS VARCHAR)    AS aisle
        FROM raw.aisles;
    """)

    con.execute("""
        CREATE OR REPLACE TABLE silver.dim_products AS
        SELECT
            CAST(product_id AS INTEGER)    AS product_id,
            CAST(product_name AS VARCHAR)  AS product_name,
            CAST(aisle_id AS INTEGER)      AS aisle_id,
            CAST(department_id AS INTEGER) AS department_id
        FROM raw.products;
    """)

    # Orders fact (typed)
    con.execute("""
        CREATE OR REPLACE TABLE silver.fct_orders AS
        SELECT
            CAST(order_id AS BIGINT)                  AS order_id,
            CAST(user_id AS BIGINT)                   AS user_id,
            CAST(eval_set AS VARCHAR)                 AS eval_set,
            CAST(order_number AS INTEGER)             AS order_number,
            CAST(order_dow AS INTEGER)                AS order_dow,
            CAST(order_hour_of_day AS INTEGER)        AS order_hour_of_day,
            CAST(days_since_prior_order AS DOUBLE)    AS days_since_prior_order
        FROM raw.orders;
    """)

    # Order line items (prior + train) unified
    con.execute("""
        CREATE OR REPLACE TABLE silver.fct_order_products AS
        SELECT
            CAST(order_id AS BIGINT)               AS order_id,
            CAST(product_id AS INTEGER)            AS product_id,
            CAST(add_to_cart_order AS INTEGER)     AS add_to_cart_order,
            CAST(reordered AS INTEGER)             AS reordered,
            'prior'::VARCHAR                       AS source_set
        FROM raw.order_products__prior
        UNION ALL
        SELECT
            CAST(order_id AS BIGINT)               AS order_id,
            CAST(product_id AS INTEGER)            AS product_id,
            CAST(add_to_cart_order AS INTEGER)     AS add_to_cart_order,
            CAST(reordered AS INTEGER)             AS reordered,
            'train'::VARCHAR                       AS source_set
        FROM raw.order_products__train;
    """)

    # Export to Parquet (one file per table for now)
    tables = [
        ("dim_departments", "silver.dim_departments"),
        ("dim_aisles", "silver.dim_aisles"),
        ("dim_products", "silver.dim_products"),
        ("fct_orders", "silver.fct_orders"),
        ("fct_order_products", "silver.fct_order_products"),
    ]

    for out_name, full_name in tables:
        out_path = (SILVER_DIR / f"{out_name}.parquet").as_posix()
        print(f"Writing {full_name} -> {out_path}")
        con.execute(f"COPY {full_name} TO '{out_path}' (FORMAT PARQUET);")

    # Quick counts
    print("\n=== Silver row counts ===")
    for _, full_name in tables:
        cnt = con.execute(f"SELECT COUNT(*) FROM {full_name}").fetchone()[0]
        print(f"{full_name}: {cnt:,}")

    con.close()
    print(f"\nDone. Silver parquet written to: {SILVER_DIR}")

if __name__ == "__main__":
    main()
