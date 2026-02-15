$ErrorActionPreference = "Stop"

# Use sample mode (seed -> sample)
$env:DATA_MODE = "sample"

Write-Host "Activating venv..."
.\.venv\Scripts\Activate.ps1

Write-Host "Building sample dataset from seed..."
python .\scripts\00_make_sample.py

Write-Host "Running pipeline (sample)..."
python .\scripts\01_load_raw_to_duckdb.py
python .\scripts\02_profile_and_checks.py
python .\scripts\03_build_silver.py
python .\scripts\04_build_gold.py

Write-Host "`n✅ Done. Sample pipeline complete."
