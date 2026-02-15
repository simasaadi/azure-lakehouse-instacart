from pathlib import Path
from azure.storage.blob import BlobServiceClient
from azure.core.pipeline.transport import RequestsTransport

REPO_ROOT = Path(__file__).resolve().parents[1]
GOLD_DIR = REPO_ROOT / "data" / "gold_parquet"

CONN_STR = (
    "DefaultEndpointsProtocol=http;"
    "AccountName=devstoreaccount1;"
    "AccountKey=Eby8vdM02xNOcqFlqUwJPLlmEtlCDXJ1OUzFT50uSRZ6IFsuFq2UVErCz4I6tq/K1SZFPTOtr/KBHBeksoGMGw==;"
    "BlobEndpoint=http://127.0.0.1:10000/devstoreaccount1;"
)

CONTAINER = "lakehouse"

def main() -> None:
    if not GOLD_DIR.exists():
        raise SystemExit("Missing data/gold_parquet. Run scripts 04 first.")

    transport = RequestsTransport(connection_timeout=10, read_timeout=300)
    bsc = BlobServiceClient.from_connection_string(CONN_STR, transport=transport)

    container = bsc.get_container_client(CONTAINER)
    if not container.exists():
        container.create_container()

    files = sorted(GOLD_DIR.glob("*.parquet"))
    if not files:
        raise SystemExit(f"No parquet files found in {GOLD_DIR}")

    for p in files:
        blob_name = f"gold/{p.name}"
        size_mb = p.stat().st_size / (1024 * 1024)
        print(f"Uploading {p.name} ({size_mb:.1f} MB) -> {blob_name}")
        with p.open("rb") as f:
            container.get_blob_client(blob_name).upload_blob(
                f,
                overwrite=True,
                max_concurrency=8,
                length=p.stat().st_size,
            )

    print("\nDone ✅ uploaded GOLD")
    print("Now listing blobs:")
    for b in container.list_blobs(name_starts_with="gold/"):
        print(" ", b.name)

if __name__ == "__main__":
    main()
