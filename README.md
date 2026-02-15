\# Azure Lakehouse (Local + Cloud Emulator) — Instacart



\# Azure Lakehouse (Local + Azure Blob Emulator) — Instacart



This repository implements a lakehouse-style data pipeline for the Instacart dataset with local execution and an Azure Blob–compatible storage emulator for reproducible runs.



\- \*\*Local mode:\*\* raw CSV → DuckDB warehouse → silver/gold Parquet marts

\- \*\*Emulated cloud storage:\*\* upload \*\*gold\*\* marts to \*\*Azurite\*\* (Azure Blob emulator) and query them downstream (authenticated)

\- \*\*Azure-ready:\*\* Terraform scaffold included to deploy ADLS Gen2 + container when an Azure subscription is available



\## Architecture



\*\*Medallion layers\*\*

\- \*\*Raw:\*\* Kaggle Instacart CSVs (`data/raw/`)

\- \*\*Silver:\*\* cleaned/typed Parquet (`data/silver\_parquet/`) \*(kept local; large)\*

\- \*\*Gold:\*\* curated marts (`data/gold\_parquet/`)



\*\*Cloud emulator\*\*

\- \*\*Storage:\*\* Azurite Blob container `lakehouse/` with:

&nbsp; - `gold/mart\_customer.parquet`

&nbsp; - `gold/mart\_product.parquet`

&nbsp; - `gold/mart\_demand\_profile.parquet`

\- \*\*Query:\*\* download via Azure SDK (auth) → query in DuckDB



\## Quickstart (Cloud Emulator Demo)



\### 1) Start Azurite (separate PowerShell window)

```powershell

azurite --skipApiVersionCheck --blobHost 127.0.0.1 --queueHost 127.0.0.1 --tableHost 127.0.0.1 --location C:\\azurite --silent --debug C:\\azurite\\debug.log



