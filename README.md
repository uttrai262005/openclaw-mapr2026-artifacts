# OpenClaw Rubric-Based Grading (SOICT submission artifacts)

This repository contains the **code artifacts** used in our SOICT paper on rubric-grounded automated grading with OpenClaw, including:
- Phase 1 single-agent grading scripts
- Phase 2 multi-agent grading system (`skills/giang-vien-v2`)
- Analysis scripts used to compute reliability metrics (QWK/MAE/Pearson) and Phase-2 vs Phase-1 shifts
- Paper drafts (`paper/`)

## What is NOT included (privacy)
This repo **does not include** raw student submissions (DOCX/PDF/TXT/images) due to privacy constraints.

We recommend releasing only **derived anonymized artifacts** (scores/metadata/audit logs) and keeping raw submissions private.

## Quickstart
### 1) Environment
- Python 3.10+ recommended (tested with Python 3.12)

Create environment and install dependencies:

```bash
pip install -r requirements.txt
```

(Optional) pin exact versions used by the authors:

```bash
pip install -r requirements.lock.txt
```

### 2) Reproduce the paper artifacts (no private data required)
Run the full reproduction pipeline:

**Windows (PowerShell):**
```powershell
powershell -ExecutionPolicy Bypass -File .\run_all.ps1
```

**macOS/Linux:**
```bash
bash ./run_all.sh
```

This produces:
- `output/soict_analysis_tables.xlsx`
- `output/soict_bootstrap_ci.xlsx`
- `paper/figures/*`
- `paper/SOICT_CCIS_camera_ready.docx`

### 3) Configure OpenClaw Gateway (only needed if you run grading)
The graders call an OpenAI-compatible endpoint provided by the OpenClaw Gateway.

Set:
- `OPENCLAW_GATEWAY_URL`
- `OPENCLAW_GATEWAY_TOKEN`

Optionally:
- `OPENCLAW_MODEL` (default used by Phase 1 scripts is `openai-codex/gpt-5.2`)

## Repository structure
- `skills/giang-vien-v2/`: Phase 2 multi-agent grading system
- `bt*_grade_incremental.py`: Phase 1 grading scripts
- `scripts/`: metric computation and paper utilities
- `paper/`: Word/Markdown drafts
- `data/`: placeholder for private datasets (NOT committed)

## Reproducibility notes
- Phase 1 and Phase 2 are designed to be comparable by using the **same underlying model** (gpt-5.2 via OpenClaw/Codex OAuth) while changing only the orchestration.
- LLM outputs are constrained to **JSON-only** responses for robust parsing.

## License
See `LICENSE`.
