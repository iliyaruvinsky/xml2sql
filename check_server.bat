@echo off
echo ========================================
echo Server Status Check
echo ========================================
echo.

echo [1] Checking for Python processes...
tasklist | findstr python.exe
if %ERRORLEVEL% EQU 0 (
    echo.
) else (
    echo    No Python processes running
)

echo.
echo [2] Checking port 8000...
netstat -ano | findstr :8000
if %ERRORLEVEL% EQU 0 (
    echo.
) else (
    echo    Port 8000 is free
)

echo.
echo [3] Checking package version...
python -c "import xml_to_sql; import inspect; from xml_to_sql.sql.renderer import _render_projection; source = inspect.getsource(_render_projection); print('    Latest code loaded:', 'YES' if 'Replace full table qualifications' in source else 'NO')"

echo.
echo ========================================
