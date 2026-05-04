# Release checklist (GitHub)

## Before pushing
- [ ] Confirm no raw student submissions are included.
- [ ] Confirm no direct student identifiers remain in released public analysis inputs.
- [ ] Verify reproduction:
  - Windows: `run_all.ps1`
  - macOS/Linux: `run_all.sh`
- [ ] Open `output/mapr_analysis_tables.xlsx` and confirm values match the current MAPR draft.
- [ ] Open `paper/mapr2026.docx` and ensure any public release link used after acceptance points to this curated artifact package.

## After pushing
- [ ] Create a Git tag `v2.1-mapr-clean`.
- [ ] Create a GitHub Release with:
  - `paper/mapr2026.docx`
  - `output/mapr_analysis_tables.xlsx`
  - `output/mapr_analysis_summary.json`
  - `ARTIFACTS.md`
