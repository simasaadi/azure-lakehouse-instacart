from pathlib import Path
import duckdb
from azure.storage.blob import BlobServiceClient

REPO_ROOT = Path(__file__).resolve().parents[1]
TMP_DIR = REPO_ROOT / "tmp" / "azurite_downloads"
TMP_DIR.mkdir(parents=True, exist_ok=True)

CONN_STR = (
    "DefaultEndpointsProtocol=http;"
    "AccountName=devstoreaccount1;"
    "AccountKey=Eby8vdM02xNOcqFlqUwJPLlmEtlCDXJ1OUzFT50uSRZ6IFsuFq2UVErCz4I6tq/K1SZFPTOtr/KBHBeksoGMGw==;"
    "BlobEndpoint=http://127.0.0.1:10000/devstoreaccount1;"
)

CONTAINER = "lakehouse"
BLOBS = {
    "mart_customer": "gold/mart_customer.parquet",
    "mart_product": "gold/mart_product.parquet",
    "mart_demand_profile": "gold/mart_demand_profile.parquet",
}

def download_blob(container, blob_name: str, out_path: Path) -> None:
    blob = container.get_blob_client(blob_name)
    data = blob.download_blob().readall()
    out_path.write_bytes(data)

def main() -> None:
    bsc = BlobServiceClient.from_connection_string(CONN_STR)
    container = bsc.get_container_client(CONTAINER)

    local_paths = {}
    print("=== Downloading parquet from Azurite (authenticated) ===")
    for key, blob_name in BLOBS.items():
        out_path = TMP_DIR / f"{key}.parquet"
        print(f"Downloading {blob_name} -> {out_path}")
        download_blob(container, blob_name, out_path)
        local_paths[key] = out_path.as_posix()

    con = duckdb.connect()

    print("\n=== Row counts (downloaded from blob) ===")
    for key, p in local_paths.items():
        cnt = con.execute(f"SELECT COUNT(*) FROM read_parquet('{p}')").fetchone()[0]
        print(f"{key}: {cnt:,}")

    print("\n=== Top 10 products by line_items ===")
    q1 = f"""
    SELECT product_name, line_items, reorder_rate
    FROM read_parquet('{local_paths["mart_product"]}')
    ORDER BY line_items DESC
    LIMIT 10;
    """
    for row in con.execute(q1).fetchall():
        print(row)

    print("\n=== Customer segments ===")
    q2 = f"""
    SELECT customer_segment, COUNT(*) AS customers
    FROM read_parquet('{local_paths["mart_customer"]}')
    GROUP BY customer_segment
    ORDER BY customers DESC;
    """
    for row in con.execute(q2).fetchall():
        print(row)

    con.close()
    print("\nDone ✅ (authenticated blob -> query in DuckDB)")

if __name__ == "__main__":
    main()
