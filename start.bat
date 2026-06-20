@echo off
setlocal EnableDelayedExpansion

echo ========================================
echo   Silence Remover - Setup and Start
echo ========================================

set "ROOT=%~dp0"

if not exist "%ROOT%venv" (
  echo Creating Python virtual environment...
  python -m venv "%ROOT%venv"
  if errorlevel 1 (
    echo ERROR: Failed to create virtual environment. Is Python installed?
    pause
    exit /b 1
  )
)

call "%ROOT%venv\Scripts\activate.bat"

python -m pip install --upgrade pip --quiet
pip install -r "%ROOT%requirements.txt" --quiet

echo Checking ffmpeg...
where ffmpeg >nul 2>nul
if errorlevel 1 (
  echo WARNING: ffmpeg is not on PATH. MoviePy needs it.
  echo Install ffmpeg from https://ffmpeg.org and add it to PATH.
) else (
  echo ffmpeg found.
)

if not exist "%ROOT%backend\uploads" mkdir "%ROOT%backend\uploads"
if not exist "%ROOT%backend\outputs" mkdir "%ROOT%backend\outputs"

if not exist "%ROOT%frontend\node_modules" (
  echo Installing frontend dependencies...
  cd "%ROOT%frontend"
  call npm install
  cd "%ROOT%"
) else (
  echo node_modules exists, skipping install.
)

echo Killing any previous backend/frontend on ports 8000 and 5173...
for /f "tokens=5" %%a in ('netstat -aon ^| findstr :8000 ^| findstr LISTENING') do taskkill /F /PID %%a >nul 2>&1
for /f "tokens=5" %%a in ('netstat -aon ^| findstr :5173 ^| findstr LISTENING') do taskkill /F /PID %%a >nul 2>&1

echo Starting backend server...
start "Silence Remover Backend" cmd /k "cd /d "%ROOT%backend" && call "%ROOT%venv\Scripts\activate.bat" && python main.py"

echo Waiting for backend to be ready...
set /a attempts=0
:wait_backend
set /a attempts+=1
if !attempts! gtr 30 (
  echo Backend failed to start. Check the backend window for errors.
  pause
  exit /b 1
)
curl -sf -m 1 http://localhost:8000/ >nul 2>&1
if errorlevel 1 (
  timeout /t 1 /nobreak >nul
  goto wait_backend
)
echo Backend is up.

echo Starting frontend dev server...
start "Silence Remover Frontend" cmd /k "cd /d "%ROOT%frontend" && npm run dev"

echo ========================================
echo Both servers starting.
echo Backend  : http://localhost:8000
echo Frontend : http://localhost:5173
echo ========================================

echo Press any key to close this window. Servers will keep running.
pause
