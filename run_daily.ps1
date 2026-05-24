$ErrorActionPreference = "Stop"

$candidates = @(
  "python",
  "py",
  "$env:USERPROFILE\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe"
)

$python = $null
foreach ($candidate in $candidates) {
  try {
    & $candidate -c "import sys; print(sys.version)" *> $null
    $python = $candidate
    break
  } catch {
  }
}

if (-not $python) {
  throw "未找到可用 Python。请安装 Python 3，或在 Codex 环境中运行。"
}

Write-Host "Using Python: $python"
& $python scripts\run_daily.py

Write-Host ""
Write-Host "日报已生成：data\reports\latest_daily_report.md"
Write-Host "看板已生成：data\reports\latest_dashboard.html"
