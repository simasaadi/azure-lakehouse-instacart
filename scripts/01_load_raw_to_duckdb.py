import os

from pathlib import Path
import duckdb

REPO_ROOT = Path(__file__).resolve().parents[1]
DATA_MODE = os.getenv("DATA_MODE", "raw").lower()
if DATA_MODE not in {"raw", "sample"}:
    raise ValueError("DATA_MODE must be 'raw' or 'sample'")

RAW_DIR = REPO_ROOT / "data" / DATA_MODE

DB_PATH = REPO_ROOT / "warehouse" / f"instacart_{DATA_MODE}.duckdb"


TABLES = {
    "aisles": "aisles.csv",
    "departments": "departments.csv",
    "products": "products.csv",
    "orders": "orders.csv",
    "order_products__prior": "order_products__prior.csv",
    "order_products__train": "order_products__train.csv",
}

def main() -> None:
    missing = [fname for fname in TABLES.values() if not (RAW_DIR / fname).exists()]
    if missing:
        raise FileNotFoundError(
            f"Missing files in {RAW_DIR}:\n" + "\n".join(missing)
        )

    con = duckdb.connect(str(DB_PATH))
    con.execute("CREATE SCHEMA IF NOT EXISTS raw;")

    for table, fname in TABLES.items():
        path = RAW_DIR / fname
        print(f"Loading {fname} -> raw.{table}")

        # Read with DuckDB directly (fast, no pandas needed)
        con.execute(f"""
            CREATE OR REPLACE TABLE raw.{table} AS
            SELECT * FROM read_csv_auto('{path.as_posix()}', header=True);
        """)

    # Row counts summary
    print("\nRow counts:")
    for table in TABLES.keys():
        cnt = con.execute(f"SELECT COUNT(*) FROM raw.{table};").fetchone()[0]
        print(f"  raw.{table}: {cnt:,}")

    con.close()
    print(f"\nDone. DuckDB saved at: {DB_PATH}")

if __name__ == "__main__":
    main()
