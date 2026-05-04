# Reproducibility

This repository contains the scripts and derived artifacts needed to recompute the main benchmark outputs reported in the MAPR 2026 submission.

## Scope
The released package supports **metric recomputation from derived outputs**.
It does not include raw student submissions.

## Prerequisites
- Python 3.10+ (tested on 3.12)

Install dependencies:
```bash
pip install -r requirements.txt
```

Or pinned versions:
```bash
pip install -r requirements.lock.txt
```

## Recompute MAPR tables
```bash
python scripts/mapr_analysis_tables.py
```

Outputs:
- `output/mapr_analysis_tables.xlsx`
- `output/mapr_analysis_summary.json`

## One-command reproduction
### Windows
```powershell
powershell -ExecutionPolicy Bypass -File .\run_all.ps1
```

### macOS/Linux
```bash
bash ./run_all.sh
```

## Notes
- `output/raw/` contains the derived inputs consumed by the benchmark analysis script.
- The current paper draft is stored at `paper/mapr2026.docx`.
- Phase-2 outputs are included for the single-agent vs multi-agent ablation reported in the paper.
