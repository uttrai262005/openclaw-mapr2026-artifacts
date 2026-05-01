#!/usr/bin/env bash
set -euo pipefail

echo "[1/4] Analysis tables"
python scripts/soict_analysis_tables.py

echo "[2/4] Bootstrap confidence intervals"
python scripts/bootstrap_ci_metrics.py

echo "[3/4] Figures"
python scripts/make_figures_soict.py

echo "[4/4] Build camera-ready Word"
python scripts/build_camera_ready_docx_fast.py

echo "Done. Outputs:"
echo "- paper/SOICT_CCIS_camera_ready.docx"
echo "- paper/figures/*"
echo "- output/soict_analysis_tables.xlsx"
echo "- output/soict_bootstrap_ci.xlsx"