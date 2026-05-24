$ErrorActionPreference = "Stop"

$candidates = @(
  "$env:USERPROFILE\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe",
  "python",
  "py"
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

Start-Process "http://127.0.0.1:8765"
& $python scripts\serve_web.py 8765
