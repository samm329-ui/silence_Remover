@echo off
setlocal EnableDelayedExpansion 
  
echo ========================================  
echo   Silence Remover - Setup and Start  
echo ========================================  
  
if not exist venv (  
  echo Creating Python virtual environment...  
  python -m venv venv  
)  
  
call venv\Scripts\activate.bat  
  
python -m pip install --upgrade pip --quiet  
pip install -r requirements.txt --quiet  
  
echo Checking ffmpeg...  
where ffmpeg >nul 2>nul  
if errorlevel 1 (  
  echo WARNING: ffmpeg is not on PATH. MoviePy needs it.  
  echo Install ffmpeg from https://ffmpeg.org and add it to PATH.  
) else (  
  echo ffmpeg found.  
)  
  
cd backend  
if not exist uploads mkdir uploads  
if not exist outputs mkdir outputs  
cd ..  
cd frontend  
if not exist node_modules (  
  call npm install  
) else (  
  echo node_modules exists, skipping install.  
)  
cd ..  
  
echo Killing any previous backend/frontend on ports 8000 and 5173...  
for /f "tokens=5" %%%a in ("netstat -aon | findstr :8000 | findstr LISTENING") do taskkill /F /PID %%%a >nul 2>&1  
for /f "tokens=5" %%%a in ("netstat -aon | findstr :5173 | findstr LISTENING") do taskkill /F /PID %%%a >nul 2>&1  
  
  
echo Starting backend server...  
start "Silence Remover Backend" cmd /k "call venv\Scripts\activate.bat ^&^& cd backend ^&^& python main.py"  
  
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
cd frontend  
start "Silence Remover Frontend" cmd /k "npm run dev"  
cd ..  
  
echo ========================================  
echo Both servers starting.  
echo Backend  : http://localhost:8000  
echo Frontend : http://localhost:5173  
echo ========================================  
  
echo Press any key to close this window. Servers will keep running.  
pause  
