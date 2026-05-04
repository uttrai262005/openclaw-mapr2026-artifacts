# OpenClaw MAPR 2026 Artifacts

This repository contains the **code, derived artifacts, and reproducibility materials** for the MAPR 2026 submission:

**LLM Selection for Automated Rubric Grading: A Multi-Model Benchmark on Real E-Commerce Assignments**

## What this repo contains
- Phase-1 single-agent grading scripts for BT1-BT4
- Phase-2 multi-agent grading pipeline for ablation comparison
- Derived score outputs for multiple models:
  - GPT-5.2 (single-agent baseline)
  - GPT-5.4
  - GPT-4o
  - GPT-5.4-mini
- Human-scored evaluation subset used for metric computation
- Metric computation scripts and exported analysis tables
- The current MAPR draft paper (`paper/mapr2026.docx`)

## Privacy
This repository does **not** include raw student submissions (DOCX/PDF/TXT/images).

Only **derived artifacts** are included:
- score tables
- audit summaries
- benchmark outputs
- analysis tables

If you need to publish score tables more broadly, consider anonymizing identifiers before external redistribution.

## Main outputs
Generated MAPR analysis outputs:
- `output/mapr_analysis_tables.xlsx`
- `output/mapr_analysis_summary.json`

Supporting derived inputs used by the benchmark script:
- `output/raw/human_subset/mau_cham_tay.xlsx`
- `output/raw/gpt52_single_full/*.xlsx`
- `output/raw/gpt52_multi_full/*.xlsx`
- `output/raw/gpt4o_full/*.xlsx`
- `output/raw/gpt54mini_full/*.xlsx`
- `output/raw/gpt54_subset/*.xlsx`

## Reproduce MAPR analysis
### Environment
- Python 3.10+ recommended
- Install dependencies:

```bash
pip install -r requirements.txt
```

For pinned versions:

```bash
pip install -r requirements.lock.txt
```

### Run analysis
**Windows (PowerShell):**
```powershell
powershell -ExecutionPolicy Bypass -File .\run_all.ps1
```

**macOS/Linux:**
```bash
bash ./run_all.sh
```

This generates:
- `output/mapr_analysis_tables.xlsx`
- `output/mapr_analysis_summary.json`

## Repository structure
- `bt*_grade_incremental.py`: grading scripts
- `skills/`: multi-agent grading skill and related components
- `scripts/mapr_analysis_tables.py`: MAPR benchmark metric builder
- `output/raw/`: derived benchmark inputs used for recomputation
- `paper/`: paper draft and related paper assets

## Reproducibility note
This package is designed so reviewers or later readers can:
1. inspect the benchmark setup,
2. recompute reported metrics from released derived outputs,
3. verify that the MAPR paper tables match the repository artifacts.

## Citation
See `CITATION.cff`.

## License
See `LICENSE`.
