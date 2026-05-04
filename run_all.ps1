# Recompute MAPR 2026 benchmark artifacts
# Usage: powershell -ExecutionPolicy Bypass -File .\run_all.ps1

$ErrorActionPreference = 'Stop'

Write-Host "[1/1] Build MAPR analysis tables" -ForegroundColor Cyan
python scripts/mapr_analysis_tables.py

Write-Host "Done. Outputs:" -ForegroundColor Green
Write-Host "- output/mapr_analysis_tables.xlsx"
Write-Host "- output/mapr_analysis_summary.json"
