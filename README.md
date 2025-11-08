# XML to SQL Converter

Convert SAP HANA calculation view XML definitions into Snowflake SQL artifacts.

> **👋 New to this project?** If you're a client deploying views to Snowflake, **[START HERE](START_HERE.md)** - This guide will walk you through the repository step-by-step.

## Overview

This tool parses SAP HANA calculation view XML files and generates Snowflake-compatible SQL queries. It supports complex calculation views with projections, joins, aggregations, unions, filters, and calculated expressions.

## Features

- ✅ **Full XML Parsing**: Supports projections, joins, aggregations, unions, filters, variables, and logical models
- ✅ **Snowflake SQL Generation**: Generates valid Snowflake SQL with CTEs, proper joins, and aggregations
- ✅ **Function Translation**: Automatically translates HANA functions to Snowflake equivalents (IF→IFF, string functions, date/time functions)
- ✅ **Currency Conversion**: Supports currency conversion via Snowflake UDFs
- ✅ **Corporate Naming**: Template-based naming conventions for tables and views
- ✅ **Configuration Management**: YAML-based configuration with runtime overrides
- ✅ **CLI Interface**: Easy-to-use command-line interface

## Installation

### Prerequisites

- Python 3.11 or higher
- pip (Python package manager)

### Setup

1. **Clone the repository:**
   ```bash
   git clone https://github.com/iliyaruvinsky/xml2sql.git
   cd xml2sql
   ```

2. **Create a virtual environment (recommended):**
   ```bash
   python -m venv venv
   
   # On Windows:
   venv\Scripts\activate
   
   # On Linux/Mac:
   source venv/bin/activate
   ```

3. **Install the package:**
   ```bash
   pip install -e ".[dev]"
   ```

## Quick Start

**For clients deploying views to Snowflake:** Start with [START_HERE.md](START_HERE.md) - Client deployment guide.

**For developers:** Start with [DEVELOPER_GUIDE.md](DEVELOPER_GUIDE.md) - Developer navigation guide, or [QUICK_START.md](QUICK_START.md) for a 5-minute setup.

## Configuration

### Configuration File Structure

```yaml
defaults:
  client: "PROD"          # Default client value for $$client$$ placeholders
  language: "EN"         # Default language value for $$language$$ placeholders

paths:
  source: "Source (XML Files)"      # Directory containing XML files
  target: "Target (SQL Scripts)"    # Directory for generated SQL files

schema_overrides:
  # Override schema names if needed
  # SAPK5D: "PRODUCTION_SCHEMA"

currency:
  udf_name: "CONVERT_CURRENCY"      # Currency conversion UDF name
  rates_table: "EXCHANGE_RATES"     # Exchange rates table name
  schema: "UTILITY"                 # Schema for currency artifacts

scenarios:
  - id: "Sold_Materials"            # Scenario identifier
    source: "Sold_Materials.XML"    # XML file name (optional, defaults to {id}.XML)
    output: "V_C_SOLD_MATERIALS"     # Output SQL file name (without .sql)
    enabled: true                    # Enable/disable this scenario
    overrides:
      client: "100"                  # Scenario-specific client override
```

### Scenario Configuration

Each scenario can have:
- **id**: Unique identifier (required)
- **source**: XML file name (optional, defaults to `{id}.XML`)
- **output**: Output SQL file name without extension (optional, defaults to formatted `{id}`)
- **enabled**: Enable/disable conversion (default: true)
- **overrides**: Scenario-specific overrides for client, language, etc.

## CLI Usage

### List Scenarios

Display all scenarios defined in the configuration:
```bash
xml-to-sql list --config config.yaml
```

### Convert Scenarios

Convert specific scenarios:
```bash
xml-to-sql convert --config config.yaml --scenario Sold_Materials --scenario SALES_BOM
```

Convert all enabled scenarios:
```bash
xml-to-sql convert --config config.yaml
```

Dry run (list what would be converted without generating SQL):
```bash
xml-to-sql convert --config config.yaml --list-only
```

### Command Options

- `--config, -c`: Path to configuration YAML file (required)
- `--scenario`: Scenario ID to convert (can be specified multiple times)
- `--list-only`: Show planned conversions without generating SQL

## Generated SQL Structure

The tool generates Snowflake SQL with the following structure:

```sql
WITH
  projection_1 AS (
    SELECT
        schema.table.column1 AS column1,
        schema.table.column2 AS column2
    FROM schema.table
    WHERE condition
  ),
  aggregation_1 AS (
    SELECT
        projection_1.column1,
        MAX(projection_1.column2) AS max_column2
    FROM projection_1
    GROUP BY projection_1.column1
  )

SELECT * FROM aggregation_1
```

### Supported Features

- **Common Table Expressions (CTEs)**: Properly ordered based on dependencies
- **Joins**: INNER, LEFT OUTER, RIGHT OUTER, FULL OUTER joins
- **Aggregations**: GROUP BY with aggregate functions (MAX, MIN, SUM, COUNT, AVG)
- **Unions**: UNION and UNION ALL operations
- **Filters**: WHERE clauses with proper predicate translation
- **Calculated Expressions**: Formula translation with HANA function mapping

## Function Translation

The tool automatically translates HANA-specific functions to Snowflake equivalents:

| HANA Function | Snowflake Equivalent |
|--------------|---------------------|
| `IF(condition, then, else)` | `IFF(condition, then, else)` |
| `TO_DATE(string, format)` | `TO_DATE(string, format)` |
| `TO_TIMESTAMP(string, format)` | `TO_TIMESTAMP(string, format)` |
| String concatenation (`+`) | `\|\|` operator |
| `SUBSTRING`, `CONCAT`, `LENGTH`, `UPPER`, `LOWER`, `TRIM` | Direct mapping |

## Testing

### Run Unit Tests

```bash
pytest -v
```

### Run Specific Test Suite

```bash
# Test parser
pytest tests/test_parser.py -v

# Test SQL renderer
pytest tests/test_sql_renderer.py -v

# Test config loader
pytest tests/test_config_loader.py -v
```

### Manual Testing

See [MANUAL_TESTING_GUIDE.md](MANUAL_TESTING_GUIDE.md) for comprehensive manual testing instructions.

## Project Structure

```
xml2sql/
├── src/
│   └── xml_to_sql/
│       ├── cli/              # Command-line interface
│       ├── config/            # Configuration management
│       ├── domain/            # Intermediate representation models
│       ├── parser/            # XML parsing logic
│       └── sql/               # SQL generation
├── tests/                     # Unit and integration tests
├── docs/                      # Documentation
├── Source (XML Files)/        # Input XML files
├── Target (SQL Scripts)/     # Generated SQL files
├── config.example.yaml        # Example configuration
└── pyproject.toml            # Project metadata and dependencies
```

## Troubleshooting

### Common Issues

**Issue: Import errors**
```bash
# Solution: Ensure virtual environment is activated and dependencies are installed
pip install -e ".[dev]"
```

**Issue: XML file not found**
- Verify file paths in `config.yaml` match actual file locations
- Check that the `source` directory path is correct

**Issue: SQL generation fails**
- Check console output for warnings
- Review parser logs for unsupported constructs
- Verify XML file structure matches expected format

**Issue: Invalid SQL generated**
- Check for warnings in the generated SQL file (comments at the top)
- Review the XML structure for unsupported features
- Verify configuration settings (schema names, etc.)

### Getting Help

**For clients deploying views:**
- Start with [START_HERE.md](START_HERE.md) - Navigation guide
- See [CLIENT_DEPLOYMENT_GUIDE.md](CLIENT_DEPLOYMENT_GUIDE.md) - Step-by-step deployment instructions

**For developers:**
- Start with [DEVELOPER_GUIDE.md](DEVELOPER_GUIDE.md) - Complete developer navigation guide
- Quick setup: [QUICK_START.md](QUICK_START.md) - 5-minute setup guide
- Testing: [docs/TESTING.md](docs/TESTING.md) - Testing procedures
- Technical docs: [docs/](docs/) - Architecture and design documentation

## Contributing

Contributions are welcome! Please follow these guidelines:

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests for new functionality
5. Ensure all tests pass
6. Submit a pull request

## License

See [LICENSE](LICENSE) file for details.

## Roadmap

Future enhancements planned:
- Rank node support (when found in XML samples)
- Currency conversion via table joins (alternative to UDF)
- Auto-generation of currency staging scripts
- Performance optimization for large XML files
- Additional HANA function translations

## Acknowledgments

This project converts SAP HANA calculation views to Snowflake SQL for data migration purposes.

---

**Version:** 0.1.0  
**Python:** 3.11+  
**Status:** Production Ready

