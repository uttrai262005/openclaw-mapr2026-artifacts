# OpenClaw MAPR 2026 Artifacts

This repository contains the **reviewer-facing artifact package** for the MAPR 2026 submission:

**LLM Selection for Automated Rubric Grading: A Multi-Model Benchmark on Real E-Commerce Assignments**

## What is included
- The current MAPR draft: `paper/mapr2026.docx`
- Metric recomputation script: `scripts/mapr_analysis_tables.py`
- Recomputed analysis tables:
  - `output/mapr_analysis_tables.xlsx`
  - `output/mapr_analysis_summary.json`
- An anonymized reviewer dataset package under `output/reviewer_data/`
- Core grading / pipeline code used to generate the released derived outputs

## What is not included
- Raw student submissions
- Original DOCX/PDF/TXT/image assignment files
- Personally identifying student records
- Legacy paper drafts unrelated to the MAPR submission

## Privacy and release design
This repository is intentionally curated for **artifact review and post-acceptance reproducibility**.

All public benchmark inputs used by the MAPR analysis script are stored in **anonymized, reviewer-safe form** under:
- `output/reviewer_data/`

The anonymized package preserves:
- score totals
- assignment-level alignment across models
- human evaluation subset alignment
- reproducibility of reported metrics

while removing direct student identifiers from the released analysis inputs.

## Main outputs
- `output/mapr_analysis_tables.xlsx`
- `output/mapr_analysis_summary.json`

## Reproduce the reported MAPR tables
### Install dependencies
```bash
pip install -r requirements.txt
```

For pinned versions:
```bash
pip install -r requirements.lock.txt
```

### Run
**Windows (PowerShell):**
```powershell
powershell -ExecutionPolicy Bypass -File .\run_all.ps1
```

**macOS/Linux:**
```bash
bash ./run_all.sh
```

This regenerates:
- `output/mapr_analysis_tables.xlsx`
- `output/mapr_analysis_summary.json`

## Quick file guide
- `paper/mapr2026.docx`: current paper draft
- `scripts/mapr_analysis_tables.py`: main reviewer-facing metric builder
- `output/reviewer_data/human_subset_scores.xlsx`: anonymized human-scored subset
- `output/reviewer_data/gpt52_single_full/*.xlsx`: anonymized single-agent totals
- `output/reviewer_data/gpt52_multi_full/*.xlsx`: anonymized multi-agent totals
- `output/reviewer_data/gpt4o_full/*.xlsx`: anonymized GPT-4o totals
- `output/reviewer_data/gpt54mini_full/*.xlsx`: anonymized GPT-5.4-mini totals
- `output/reviewer_data/gpt54_subset/*.xlsx`: anonymized GPT-5.4 subset totals

## Reviewer guidance
See `ARTIFACTS.md` for a table-by-table mapping from repository outputs to paper content.

## Citation
See `CITATION.cff`.

## License
See `LICENSE`.
