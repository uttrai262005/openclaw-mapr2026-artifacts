# Release checklist (GitHub)

## Before pushing
- [ ] Confirm no private data is included (`dataset_clean/`, raw submissions, or any student PDFs/DOCX).
- [ ] If score tables include MSSV, run anonymization:
  ```bash
  python scripts/anonymize_ids.py --in output/soict_analysis_tables.xlsx --out output/soict_analysis_tables_anonymized.xlsx --salt "<secret>"
  ```
- [ ] Verify reproduction:
  - Windows: `run_all.ps1`
  - macOS/Linux: `run_all.sh`

## After pushing
- [ ] Create a Git tag `v1.0-soict`.
- [ ] Create a GitHub Release with:
  - `paper/SOICT_CCIS_camera_ready.docx`
  - figures under `paper/figures/`
  - (optional) anonymized score tables

## Optional (nice-to-have)
- [ ] Add a PDF export of the paper for convenient viewing on GitHub.
  - If you have Microsoft Word installed, export `paper/SOICT_CCIS_camera_ready.docx` as PDF and upload to the release.
