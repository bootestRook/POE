@echo off
setlocal

cd /d "%~dp0"
set PORT=8766

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

echo Stopping stale WebApp server on port %PORT%...
powershell -NoProfile -ExecutionPolicy Bypass -Command "$targets = Get-CimInstance Win32_Process | Where-Object { $_.Name -eq 'python.exe' -and $_.CommandLine -like '*tools\webapp_server.py --port %PORT%*' }; foreach ($p in $targets) { Stop-Process -Id $p.ProcessId -Force }"
if errorlevel 1 (
  echo Failed to stop stale WebApp server.
  pause
  exit /b 1
)

echo Starting WebApp...
echo Browser URL: http://127.0.0.1:%PORT%
python tools\webapp_server.py --port %PORT% --open

endlocal
