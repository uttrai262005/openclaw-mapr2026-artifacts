# Reproduce SOICT artifacts (analysis + CI + figures + Word)
# Usage: powershell -ExecutionPolicy Bypass -File .\run_all.ps1

$ErrorActionPreference = 'Stop'

Write-Host "[1/4] Analysis tables" -ForegroundColor Cyan
python scripts/soict_analysis_tables.py

Write-Host "[2/4] Bootstrap confidence intervals" -ForegroundColor Cyan
python scripts/bootstrap_ci_metrics.py

Write-Host "[3/4] Figures" -ForegroundColor Cyan
python scripts/make_figures_soict.py

Write-Host "[4/4] Build camera-ready Word" -ForegroundColor Cyan
python scripts/build_camera_ready_docx_fast.py

Write-Host "Done. Outputs:" -ForegroundColor Green
Write-Host "- paper/SOICT_CCIS_camera_ready.docx"
Write-Host "- paper/figures/*"
Write-Host "- output/soict_analysis_tables.xlsx"
Write-Host "- output/soict_bootstrap_ci.xlsx"