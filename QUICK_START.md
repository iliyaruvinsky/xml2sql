# Quick Start Guide

## 5-Minute Test

### Step 1: Install Dependencies
```cmd
REM Navigate to project
cd "C:\Users\USER\Google Drive\SW_PLATFORM\15. AI\MY_LATEST_FILES\EXODUS\XML to SQL"

REM Activate virtual environment (CMD)
venv\Scripts\activate.bat

REM Or in PowerShell:
REM .\venv\Scripts\Activate.ps1

REM Install dependencies
python -m pip install -e ".[dev]"
```

### Step 2: Run Tests
```cmd
venv\Scripts\python -m pytest -v
```
**Expected:** 23 tests pass

### Step 3: Create Config
```cmd
REM In CMD:
copy config.example.yaml config.yaml

REM Or in PowerShell:
Copy-Item config.example.yaml config.yaml
```

### Step 4: Convert One File
```cmd
REM Using Python module (correct way)
venv\Scripts\python -m xml_to_sql.cli convert --config config.yaml --scenario Sold_Materials

REM Or if entry point is installed
xml-to-sql convert --config config.yaml --scenario Sold_Materials
```

### Step 5: Check Output
```cmd
REM In CMD:
type "Target (SQL Scripts)\V_C_SOLD_MATERIALS.sql" | more

REM Or in PowerShell:
REM Get-Content "Target (SQL Scripts)\V_C_SOLD_MATERIALS.sql" | Select-Object -First 30
```

**Done!** You should see generated Snowflake SQL.

## Common Commands

```cmd
REM List all scenarios
venv\Scripts\python -m xml_to_sql.cli list --config config.yaml

REM Convert all enabled scenarios
venv\Scripts\python -m xml_to_sql.cli convert --config config.yaml

REM Convert specific scenario
venv\Scripts\python -m xml_to_sql.cli convert --config config.yaml --scenario Sold_Materials

REM Dry run (see what would be converted)
venv\Scripts\python -m xml_to_sql.cli convert --config config.yaml --list-only
```

For detailed testing instructions, see [docs/TESTING.md](docs/TESTING.md).

