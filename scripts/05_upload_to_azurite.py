from pathlib import Path
from azure.storage.blob import BlobServiceClient

REPO_ROOT = Path(__file__).resolve().parents[1]
SILVER_DIR = REPO_ROOT / "data" / "silver_parquet"
GOLD_DIR = REPO_ROOT / "data" / "gold_parquet"

CONN_STR = (
    "DefaultEndpointsProtocol=http;"
    "AccountName=devstoreaccount1;"
    "AccountKey=Eby8vdM02xNOcqFlqUwJPLlmEtlCDXJ1OUzFT50uSRZ6IFsuFq2UVErCz4I6tq/K1SZFPTOtr/KBHBeksoGMGw==;"
    "BlobEndpoint=http://127.0.0.1:10000/devstoreaccount1;"
)

CONTAINER = "lakehouse"

def upload_parquet_dir(container, local_dir: Path, prefix: str) -> None:
    files = sorted(local_dir.glob("*.parquet"))
    if not files:
        raise SystemExit(f"No parquet files found in {local_dir}. Did you run scripts 03 and 04?")

    for p in files:
        blob_name = f"{prefix}/{p.name}"
        print(f"Uploading {p.name} -> {blob_name}")
        with p.open("rb") as f:
            container.get_blob_client(blob_name).upload_blob(f, overwrite=True)

def main() -> None:
    if not SILVER_DIR.exists() or not GOLD_DIR.exists():
        raise SystemExit("Missing data/silver_parquet or data/gold_parquet. Run scripts 03 and 04 first.")

    bsc = BlobServiceClient.from_connection_string(CONN_STR)
    container = bsc.get_container_client(CONTAINER)
    if not container.exists():
        container.create_container()

    upload_parquet_dir(container, SILVER_DIR, "silver")
    upload_parquet_dir(container, GOLD_DIR, "gold")

    print("\nUploaded blobs:")
    for b in container.list_blobs():
        print(f"  {b.name}")

    print("\nDone ✅ (Azurite)")

if __name__ == "__main__":
    main()
