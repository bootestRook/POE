@echo off
setlocal

cd /d "%~dp0"
set PORT=8765

echo ========================================
echo SkillEditor one-click runner
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

if /I "%~1"=="--check" (
  echo SkillEditor runner check passed.
  exit /b 0
)

echo Starting SkillEditor...
echo Browser URL: http://127.0.0.1:%PORT%/skill-editor
start "" powershell -NoProfile -ExecutionPolicy Bypass -Command "Start-Sleep -Seconds 2; Start-Process 'http://127.0.0.1:%PORT%/skill-editor'"
python tools\webapp_server.py --port %PORT%

endlocal
