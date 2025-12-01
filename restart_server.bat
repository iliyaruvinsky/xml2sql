@echo off
echo ========================================
echo XML2SQL Web Server - Hard Restart
echo ========================================
echo.

echo [1/11] Killing Python processes by name...
taskkill /F /IM python.exe >nul 2>&1
taskkill /F /IM pythonw.exe >nul 2>&1
echo    ✓ Killed by process name

echo.
echo [2/11] Finding processes using port 8000...
for /f "tokens=5" %%a in ('netstat -ano ^| findstr :8000') do (
    echo    Found PID: %%a
    taskkill /F /PID %%a >nul 2>&1
)
echo    ✓ Port-based kill complete

echo.
echo [3/11] Waiting for connections to clear (attempt 1)...
timeout /t 3 /nobreak >nul
netstat -ano | findstr :8000 >nul
if %ERRORLEVEL% EQU 0 (
    echo    ⏳ Port still in TIME_WAIT, continuing cleanup...
) else (
    echo    ✓ Port 8000 is free
    goto :port_free
)

echo.
echo [4/11] Additional cleanup - killing uvicorn processes...
for /f "tokens=2" %%a in ('tasklist /FI "IMAGENAME eq python.exe" /FO LIST ^| findstr /C:"PID:"') do (
    taskkill /F /PID %%a >nul 2>&1
)
echo    ✓ Additional cleanup complete

echo.
echo [5/11] Waiting for connections to clear (attempt 2)...
timeout /t 5 /nobreak >nul
netstat -ano | findstr :8000 >nul
if %ERRORLEVEL% EQU 0 (
    echo    ⏳ Port still in TIME_WAIT, continuing...
) else (
    echo    ✓ Port 8000 is free
    goto :port_free
)

echo.
echo [6/11] Final port check and PID cleanup...
for /f "tokens=5" %%a in ('netstat -ano ^| findstr :8000') do (
    echo    Forcing kill PID: %%a
    taskkill /F /T /PID %%a >nul 2>&1
)
timeout /t 5 /nobreak >nul

:port_free
echo.
echo [7/11] Verifying port 8000 is free...
netstat -ano | findstr :8000 >nul
if %ERRORLEVEL% EQU 0 (
    echo    ⚠ Port 8000 still has TIME_WAIT connections
    echo    This is normal, continuing anyway...
) else (
    echo    ✓ Port 8000 is completely free
)

echo.
echo [8/11] Clearing Python cache files...
for /r "src" %%i in (*.pyc) do @del "%%i" >nul 2>&1
for /d /r "src" %%i in (__pycache__) do @rd /s /q "%%i" >nul 2>&1
echo    ✓ Python cache cleared

echo.
echo [9/11] Reinstalling package in editable mode...
pip install -e . --quiet
if %ERRORLEVEL% EQU 0 (
    echo    ✓ Package reinstalled successfully
) else (
    echo    ✗ Package reinstall failed!
    pause
    exit /b 1
)

echo.
echo [10/11] Verifying package installation...
python -c "import xml_to_sql; print('    ✓ Package loaded successfully')" 2>&1

echo.
echo [11/11] Starting web server...
echo    Server will start at http://localhost:8000
echo    Press Ctrl+C to stop the server
echo.
echo ========================================
echo Ready to start!
echo ========================================
timeout /t 2 /nobreak >nul
echo.

python -m uvicorn src.xml_to_sql.web.main:app --reload --host 0.0.0.0 --port 8000
