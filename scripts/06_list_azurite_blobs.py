from azure.storage.blob import BlobServiceClient

CONN_STR = (
    "DefaultEndpointsProtocol=http;"
    "AccountName=devstoreaccount1;"
    "AccountKey=Eby8vdM02xNOcqFlqUwJPLlmEtlCDXJ1OUzFT50uSRZ6IFsuFq2UVErCz4I6tq/K1SZFPTOtr/KBHBeksoGMGw==;"
    "BlobEndpoint=http://127.0.0.1:10000/devstoreaccount1;"
)

bsc = BlobServiceClient.from_connection_string(CONN_STR)
container = bsc.get_container_client("lakehouse")

print("Blobs in lakehouse:")
for b in container.list_blobs():
    print(" ", b.name)
