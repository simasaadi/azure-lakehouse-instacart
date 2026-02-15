$ErrorActionPreference = "Stop"

# Use raw mode (expects data/raw exists locally)
$env:DATA_MODE = "raw"

Write-Host "Activating venv..."
.\.venv\Scripts\Activate.ps1

Write-Host "Running pipeline (raw)..."
python .\scripts\01_load_raw_to_duckdb.py
python .\scripts\02_profile_and_checks.py
python .\scripts\03_build_silver.py
python .\scripts\04_build_gold.py

Write-Host "`n✅ Done. Raw pipeline complete."
