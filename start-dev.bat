@echo off
echo ============================================================
echo   Rare Books - Development Server Launcher
echo ============================================================
echo.
echo Starting both Backend and Frontend servers...
echo.

REM Check Node.js is available
where node >nul 2>&1
if %ERRORLEVEL% neq 0 (
    echo ERROR: Node.js is not installed or not in PATH.
    echo Please install Node.js first: https://nodejs.org/
    echo.
    pause
    exit /b 1
)

REM Check Python is available
where python >nul 2>&1
if %ERRORLEVEL% neq 0 (
    echo ERROR: Python is not installed or not in PATH.
    echo Please install Python first: https://python.org/
    echo.
    pause
    exit /b 1
)

echo [1/2] Starting Flask Backend (API) on http://localhost:5000 ...
start "Flask Backend" cmd /k "cd /d %~dp0bookstore && python run.py"

echo [2/2] Starting Next.js Frontend on http://localhost:3000 ...
start "Next.js Frontend" cmd /k "cd /d %~dp0frontend && pnpm dev"

echo.
echo ============================================================
echo   Both servers are starting!
echo.
echo   Backend  (API):  http://localhost:5000
echo   Frontend (App):  http://localhost:3000  <-- OPEN THIS ONE
echo.
echo   To see the app with navigation, go to:
echo     http://localhost:3000
echo.
echo   Test accounts: admin@bookstore.com / admin
echo ============================================================
echo.
echo Press any key to close this launcher (servers keep running)...
pause >nul
