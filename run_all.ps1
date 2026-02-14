$ErrorActionPreference = "Stop"

# Activate venv
if (Test-Path ".\.venv\Scripts\Activate.ps1") {
  . .\.venv\Scripts\Activate.ps1
} else {
  Write-Host "Missing .venv. Create it first: python -m venv .venv"
  exit 1
}

python .\scripts\01_load_raw_to_duckdb.py
python .\scripts\02_profile_and_checks.py
python .\scripts\03_build_silver.py
python .\scripts\04_build_gold.py

Write-Host "`nPipeline complete ✅"
