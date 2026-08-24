@echo off
setlocal
cd /d %~dp0

echo ===================================================
echo    SOLA PROJECT TRICHY - AUTO BOOTSTRAP
echo ===================================================
echo.

:: Check if scripts\setup_env.ps1 exists
if not exist "scripts\setup_env.ps1" (
    echo ERROR: scripts\setup_env.ps1 not found!
    echo Please make sure you are running this from the project root.
    pause
    exit /b 1
)

:: Run the PowerShell setup script
echo Running environment setup...
powershell -ExecutionPolicy Bypass -File "scripts\setup_env.ps1"

if %ERRORLEVEL% NEQ 0 (
    echo.
    echo ERROR: Setup failed. Please check the output above.
    pause
    exit /b %ERRORLEVEL%
)

echo.
echo ===================================================
echo    STARTING PROJECT SERVICES
echo ===================================================
echo.

:: Start Backend
echo Starting Backend API (FastAPI) in a new window...
start "Sola Backend" cmd /k "cd backend && .\venv\Scripts\python.exe -m uvicorn app.main:app --reload --port 8000"

:: Start Frontend
echo Starting Frontend (Vite) in a new window...
start "Sola Frontend" cmd /k "cd frontend && npm run dev"

echo.
echo All services are starting!
echo.
echo [Backend] http://localhost:8000
echo [Frontend] http://localhost:5173
echo.
echo Keep this window open if you want to see bootstrap logs.
echo Press any key to exit this bootstrap window (services will stay running).
echo.
pause
