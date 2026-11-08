@echo off
cd /d "%~dp0"
if exist ".venv\Scripts\python.exe" goto dependencies
if exist "%LocalAppData%\Programs\Python\Python311\python.exe" (
  "%LocalAppData%\Programs\Python\Python311\python.exe" -m venv .venv
) else (
  py -3 -m venv .venv
)
if errorlevel 1 (
  echo Could not create the environment. Install Python 3.10 or newer.
  pause
  exit /b 1
)
:dependencies
".venv\Scripts\python.exe" -c "import streamlit" >nul 2>&1
if not errorlevel 1 goto launch
".venv\Scripts\python.exe" -m pip install -r requirements.txt
if errorlevel 1 (
  echo Installation failed. Check Python 3.10+ installation.
  pause
  exit /b 1
)
:launch
".venv\Scripts\python.exe" -m streamlit run app.py --server.headless false --server.address localhost
pause
