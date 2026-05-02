# Reproducibility

This repository contains the scripts and artifacts to reproduce the tables and figures reported in the SOICT paper draft.

## Prerequisites
- Python 3.10+ (tested on 3.12)
- OpenClaw Gateway running locally

For exact dependency versions, prefer:
```bash
pip install -r requirements.lock.txt
```

### System dependency (OCR)
If you run OCR-enabled utilities (`pytesseract`), you must install the system Tesseract binary.
See README for platform-specific install notes.

Environment variables (required for grading runs):
- OPENCLAW_GATEWAY_URL
- OPENCLAW_GATEWAY_TOKEN

Optional:
- OPENCLAW_MODEL (Phase 1 defaults to openai-codex/gpt-5.2)

## Reproduce analysis tables
```bash
python scripts/soict_analysis_tables.py
```
Outputs: output/soict_analysis_tables.xlsx

## Reproduce bootstrap confidence intervals
```bash
python scripts/bootstrap_ci_metrics.py
```
Outputs: output/soict_bootstrap_ci.xlsx

## Reproduce figures
```bash
python scripts/make_figures_soict.py
```
Outputs: paper/figures/figure_pipeline.png, paper/figures/figure_scatter_p1_p2_vs_gt.png

## Build the camera-ready Word draft
```bash
python scripts/build_camera_ready_docx_fast.py
```
Outputs: paper/SOICT_CCIS_camera_ready.docx
