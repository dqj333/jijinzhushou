@echo off
setlocal
set "PYTHONUTF8=1"

set "PYTHON_EXE="
if exist "%USERPROFILE%\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe" (
  set "PYTHON_EXE=%USERPROFILE%\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe"
)

if not defined PYTHON_EXE (
  where python >nul 2>nul
  if %errorlevel%==0 set "PYTHON_EXE=python"
)

if not defined PYTHON_EXE (
  where py >nul 2>nul
  if %errorlevel%==0 set "PYTHON_EXE=py"
)

if not defined PYTHON_EXE (
  echo No usable Python found.
  exit /b 1
)

echo Opening http://127.0.0.1:8765
start "" "http://127.0.0.1:8765"
"%PYTHON_EXE%" scripts\serve_web.py 8765
