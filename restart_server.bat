@echo off
echo ========================================
echo XML2SQL Web Server - Hard Restart
echo ========================================
echo.

echo [1/6] Killing all Python processes...
taskkill /F /IM python.exe >nul 2>&1
if %ERRORLEVEL% EQU 0 (
    echo    ✓ Python processes terminated
) else (
    echo    ℹ No Python processes found
)
timeout /t 2 /nobreak >nul

echo.
echo [2/6] Verifying port 8000 is free...
netstat -ano | findstr :8000 >nul
if %ERRORLEVEL% EQU 0 (
    echo    ✗ Port 8000 still in use!
    echo    Please manually close the process or wait a moment
    pause
    exit /b 1
) else (
    echo    ✓ Port 8000 is free
)

echo.
echo [3/6] Clearing Python cache files...
for /r "src" %%i in (*.pyc) do @del "%%i" >nul 2>&1
for /d /r "src" %%i in (__pycache__) do @rd /s /q "%%i" >nul 2>&1
echo    ✓ Python cache cleared

echo.
echo [4/6] Reinstalling package in editable mode...
pip install -e . --quiet
if %ERRORLEVEL% EQU 0 (
    echo    ✓ Package reinstalled successfully
) else (
    echo    ✗ Package reinstall failed!
    pause
    exit /b 1
)

echo.
echo [5/6] Verifying package installation...
python -c "import xml_to_sql; print('    ✓ Package loaded successfully')" 2>&1

echo.
echo [6/6] Starting web server...
echo    Server will start at http://localhost:8000
echo    Press Ctrl+C to stop the server
echo.
echo ========================================
echo Ready to start!
echo ========================================
timeout /t 2 /nobreak >nul
echo.

python -m uvicorn src.xml_to_sql.web.main:app --reload --host 0.0.0.0 --port 8000
