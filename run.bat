@echo off
setlocal

cd /d "%~dp0"

echo ========================================
echo V1 WebApp runner
echo ========================================
echo.

where python >nul 2>nul
if errorlevel 1 (
  echo Python was not found. Please install Python 3.11+ and add it to PATH.
  pause
  exit /b 1
)

where node >nul 2>nul
if errorlevel 1 (
  echo Node.js was not found. Please install Node.js and add it to PATH.
  pause
  exit /b 1
)

if not exist node_modules (
  echo Installing WebApp dependencies...
  call npm.cmd install
  if errorlevel 1 (
    echo npm install failed.
    pause
    exit /b 1
  )
)

echo Building WebApp...
call npm.cmd run build
if errorlevel 1 (
  echo WebApp build failed.
  pause
  exit /b 1
)

echo Starting WebApp...
echo Browser URL: http://127.0.0.1:8000
python tools\webapp_server.py --open

endlocal
