$ErrorActionPreference = "Stop"

# Activate venv
. .\.venv\Scripts\Activate.ps1

# Build local lakehouse
python .\scripts\01_load_raw_to_duckdb.py
python .\scripts\02_profile_and_checks.py
python .\scripts\03_build_silver.py
python .\scripts\04_build_gold.py

# Upload gold to Azurite (Azure Blob emulator)
python .\scripts\05b_upload_gold_only_to_azurite.py

# Query gold (authenticated blob -> DuckDB)
python .\scripts\07_query_gold_from_blob.py

Write-Host "`nCloud emulator demo complete ✅"
