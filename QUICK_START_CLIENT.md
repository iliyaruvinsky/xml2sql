# Quick Start Guide - For Clients

## What to Do After Extracting the Zip File

### Step 1: Extract the Zip File
- Extract `xml2sql-distribution-20251109-083213.zip` to any folder on your computer
- Example: `C:\xml2sql` or `C:\Users\YourName\xml2sql`

### Step 2: Install Python (if not already installed)
- Download Python 3.11 or higher from [python.org](https://www.python.org/downloads/)
- During installation, check "Add Python to PATH"
- Verify installation: Open Command Prompt and type `python --version`

### Step 3: Install Node.js (if not already installed)
- Download Node.js 18 or higher from [nodejs.org](https://nodejs.org/)
- Verify installation: Open Command Prompt and type `node --version`

### Step 4: Open Command Prompt in the Extracted Folder
- Navigate to the extracted folder
- Right-click in the folder → "Open in Terminal" or "Open PowerShell here"
- Or open Command Prompt and type: `cd "path\to\extracted\folder"`

### Step 5: Set Up Python Environment
```bash
# Create virtual environment
python -m venv venv

# Activate it (Windows)
venv\Scripts\activate

# Install dependencies
pip install -e .
```

### Step 6: Start the Application
```bash
python run_server.py
```

### Step 7: Open in Browser
- Open your web browser
- Go to: `http://localhost:8000`
- You should see the XML to SQL Converter interface

### Step 8: Convert Your XML Files
1. Click "Upload XML File" or drag & drop a SAP HANA calculation view XML file
2. (Optional) Configure settings (Client, Language, Schema Overrides, etc.)
3. Click "Convert to SQL"
4. Review the generated SQL
5. Download or copy the SQL

## That's It! 🎉

The application is now running on your computer. You can convert SAP HANA calculation view XML files to Snowflake SQL.

## Troubleshooting

**Port 8000 already in use?**
- Edit `run_server.py` and change `port=8000` to another number (e.g., `port=8001`)
- Then access `http://localhost:8001` instead

**Python not found?**
- Make sure Python is installed and added to PATH
- Try `python3` instead of `python`

**npm not found?**
- The frontend is already built in the package, so you don't need npm unless you want to modify the frontend

**Need more help?**
- See `INSTALLATION_GUIDE.md` for detailed instructions
- See `START_HERE.md` for complete documentation

