# Multi-model single-agent benchmark runner (MAPR 2026)
#
# Runs Phase-1 incremental graders for BT1–BT4 under multiple models.
# Output is written to separate files per model to avoid overwriting.

$ErrorActionPreference = 'Stop'

$models = @(
  @{ name = 'gpt4o'; id = 'openai/gpt-4o' },
  @{ name = 'gpt51'; id = 'openai-codex/gpt-5.1' },
  @{ name = 'gpt52'; id = 'openai-codex/gpt-5.2' }
)

$maxTokens = '150'   # scores-only JSON

foreach ($m in $models) {
  Write-Host "=== Model: $($m.name) ($($m.id)) ===" -ForegroundColor Cyan

  $env:OPENCLAW_MODEL = $m.id
  $env:OPENCLAW_MAX_TOKENS = $maxTokens

  # BT1
  $env:OUT_PATH = "output/ket_qua_BT1_$($m.name).xlsx"
  python bt1_grade_incremental.py

  # BT2
  $env:OUT_PATH = "output/ket_qua_BT2_$($m.name).xlsx"
  python bt2_grade_incremental.py

  # BT3
  $env:OUT_PATH = "output/ket_qua_BT3_$($m.name).xlsx"
  python bt3_grade_incremental.py

  # BT4
  $env:OUT_PATH = "output/ket_qua_BT4_$($m.name).xlsx"
  python bt4_grade_incremental.py --out $env:OUT_PATH
}

Write-Host "Done. Outputs in output/*.xlsx" -ForegroundColor Green
