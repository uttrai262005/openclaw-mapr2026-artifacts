# Artifact Guide for Reviewers

This document maps the repository contents to the MAPR 2026 paper.

## Primary paper file
- `paper/mapr2026.docx`

## Primary recomputation script
- `scripts/mapr_analysis_tables.py`

Running the script regenerates:
- `output/mapr_analysis_tables.xlsx`
- `output/mapr_analysis_summary.json`

## Input package used by the script
- `output/reviewer_data/human_subset_scores.xlsx`
- `output/reviewer_data/gpt52_single_full/BT1.xlsx` ... `BT4.xlsx`
- `output/reviewer_data/gpt52_multi_full/BT1.xlsx` ... `BT4.xlsx`
- `output/reviewer_data/gpt4o_full/BT1.xlsx` ... `BT4.xlsx`
- `output/reviewer_data/gpt54mini_full/BT1.xlsx` ... `BT4.xlsx`
- `output/reviewer_data/gpt54_subset/BT1.xlsx` ... `BT4.xlsx`

## Workbook sheet mapping
`output/mapr_analysis_tables.xlsx` contains:
- `summary`: main per-assignment metrics for the four evaluated models
- `ci_metrics`: point estimates + bootstrap confidence intervals
- `bias_table`: per-assignment score bias relative to human ground truth
- `multiagent_subset`: single-agent vs multi-agent ablation on the human-scored subset
- `full_dataset_delta`: full-dataset mean/median shift of Phase 2 relative to Phase 1
- `subset_BT1` ... `subset_BT4`: merged anonymized working tables used for recomputation

## Privacy notes
The repository intentionally excludes:
- raw submissions
- personally identifying student files
- original course exports with direct student identifiers

The reviewer dataset preserves numerical reproducibility while anonymizing public-facing analysis inputs.
