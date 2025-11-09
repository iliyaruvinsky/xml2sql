# Installation Guide for XML to SQL Converter

This guide will help you install and run the XML to SQL Converter application on your local machine.

## Prerequisites

Before installing, ensure you have:

- **Python 3.11 or higher** - [Download Python](https://www.python.org/downloads/)
- **Node.js 18 or higher** (for frontend) - [Download Node.js](https://nodejs.org/)
- **Git** (optional, if pulling from repository) - [Download Git](https://git-scm.com/downloads)

## Installation Steps

### Option 1: Install from Git Repository (Recommended)

1. **Clone the repository:**
   ```bash
   git clone https://github.com/iliyaruvinsky/xml2sql.git
   cd xml2sql
   ```

2. **Set up Python environment:**
   ```bash
   # Create virtual environment
   python -m venv venv
   
   # Activate virtual environment
   # On Windows:
   venv\Scripts\activate
   
   # On Linux/Mac:
   source venv/bin/activate
   ```

3. **Install Python dependencies:**
   ```bash
   pip install -e .
   ```

4. **Set up frontend:**
   ```bash
   cd web_frontend
   npm install
   npm run build
   cd ..
   ```

5. **Create configuration file:**
   ```bash
   # Copy example config
   cp config.example.yaml config.yaml
   
   # Edit config.yaml with your settings (optional)
   ```

6. **Run the application:**
   ```bash
   python run_server.py
   ```

7. **Access the web interface:**
   - Open your browser and go to: `http://localhost:8000`
   - The web interface should be available

### Option 2: Install from Distribution Package

If you received a distribution package (zip file):

1. **Extract the package:**
   ```bash
   # Extract the zip file to your desired location
   unzip xml2sql-distribution.zip  # On Linux/Mac
   # or use your preferred extraction tool on Windows
   ```

2. **Navigate to the extracted folder:**
   ```bash
   cd xml2sql-distribution
   ```

3. **Follow steps 2-7 from Option 1** (starting from "Set up Python environment")

## Configuration

### Basic Configuration

The application uses `config.yaml` for configuration. Key settings:

- **Client**: Default client value (default: `PROD`)
- **Language**: Default language value (default: `EN`)
- **Schema Overrides**: Map XML schema names to your Snowflake schemas
- **Currency Settings**: UDF and table names for currency conversion

See `config.example.yaml` for a template.

### Web Interface Configuration

The web interface allows you to configure settings per conversion:
- Client and Language values
- Schema overrides
- Currency conversion settings
- Auto-correction options

## Running the Application

### Start the Web Server

```bash
python run_server.py
```

The server will start on `http://localhost:8000` by default.

### Using the Web Interface

1. Open `http://localhost:8000` in your browser
2. Upload a SAP HANA calculation view XML file
3. Configure settings (optional)
4. Click "Convert to SQL"
5. Review the generated SQL
6. Download or copy the SQL

### Using the CLI

```bash
# Convert a single file
xml2sql convert path/to/file.xml

# Convert multiple files
xml2sql convert path/to/*.xml

# List conversion history
xml2sql list
```

## Troubleshooting

### Python Issues

**Problem:** `python` command not found
- **Solution:** Use `python3` instead, or ensure Python is in your PATH

**Problem:** `pip install` fails
- **Solution:** Upgrade pip: `python -m pip install --upgrade pip`

### Node.js Issues

**Problem:** `npm` command not found
- **Solution:** Install Node.js from [nodejs.org](https://nodejs.org/)

**Problem:** Frontend build fails
- **Solution:** 
  ```bash
  cd web_frontend
  rm -rf node_modules package-lock.json
  npm install
  npm run build
  ```

### Port Already in Use

**Problem:** Port 8000 is already in use
- **Solution:** Edit `run_server.py` and change the port number, or stop the process using port 8000

### Database Issues

**Problem:** SQLite database errors
- **Solution:** Ensure the directory is writable, or delete `conversions.db` to reset

## File Structure

```
xml2sql/
├── src/                    # Source code
├── web_frontend/           # React frontend
│   ├── src/               # Frontend source
│   └── dist/              # Built frontend (after npm run build)
├── tests/                  # Test files
├── config.yaml            # Configuration file (create from config.example.yaml)
├── run_server.py          # Server startup script
├── pyproject.toml         # Python dependencies
└── README.md              # Main documentation
```

## Next Steps

- Read [START_HERE.md](START_HERE.md) for a complete overview
- See [WEB_GUI_DEPLOYMENT_GUIDE.md](WEB_GUI_DEPLOYMENT_GUIDE.md) for web interface details
- Check [CLIENT_DEPLOYMENT_GUIDE.md](CLIENT_DEPLOYMENT_GUIDE.md) for deployment options

## Support

For issues or questions:
- Check the documentation in the `docs/` folder
- Review error messages in the application
- Check the GitHub repository for updates

