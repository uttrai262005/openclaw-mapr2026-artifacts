#!/usr/bin/env bash
set -euo pipefail

echo "[1/1] Build MAPR analysis tables"
python scripts/mapr_analysis_tables.py

echo "Done. Outputs:"
echo "- output/mapr_analysis_tables.xlsx"
echo "- output/mapr_analysis_summary.json"
