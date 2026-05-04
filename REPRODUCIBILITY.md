# Reproducibility

This repository contains the scripts and anonymized derived artifacts needed to recompute the main benchmark outputs reported in the MAPR 2026 submission.

## Scope
The released package supports **metric recomputation from anonymized derived outputs**.
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

## Released analysis inputs
All public inputs used by the benchmark script are under:
- `output/reviewer_data/`

These files are anonymized and sufficient to recompute the reported tables.

## Paper file
- `paper/mapr2026.docx`

## Additional guide
See `ARTIFACTS.md` for mapping between repository outputs and paper sections/tables.
