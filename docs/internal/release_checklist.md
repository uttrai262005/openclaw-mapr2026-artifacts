# Release checklist (GitHub)

## Before pushing
- [ ] Confirm no raw student submissions are included.
- [ ] Confirm the repository contains only derived artifacts and paper-support files.
- [ ] Verify reproduction:
  - Windows: `run_all.ps1`
  - macOS/Linux: `run_all.sh`
- [ ] Open `output/mapr_analysis_tables.xlsx` and confirm values match the current MAPR draft.
- [ ] Open `paper/mapr2026.docx` and ensure the GitHub link points to the MAPR artifact repository.

## After pushing
- [ ] Create a Git tag `v2.0-mapr`.
- [ ] Create a GitHub Release with:
  - `paper/mapr2026.docx`
  - `output/mapr_analysis_tables.xlsx`
  - `output/mapr_analysis_summary.json`

## Optional
- [ ] Add an anonymized public export if you later want broader sharing beyond the review artifact package.
