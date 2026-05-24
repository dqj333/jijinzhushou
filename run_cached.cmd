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

echo Using Python: %PYTHON_EXE%
"%PYTHON_EXE%" scripts\build_context.py
"%PYTHON_EXE%" scripts\generate_report.py

echo.
echo Report: data\reports\latest_daily_report.md
echo Dashboard: data\reports\latest_dashboard.html
