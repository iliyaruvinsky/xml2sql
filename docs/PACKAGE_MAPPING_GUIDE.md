# HANA Package Mapping System

## Overview

The Package Mapping System provides automatic lookup of HANA package paths for Calculation Views based on their names. This eliminates the need to manually specify package paths when converting XMLs to SQL.

## Components

### 1. Package Mapping File
**Location**: `xml2sql/package_mapping.json`

Contains mappings from 167 Calculation Views to their HANA packages, exported from the MBD (ECC) instance.

**Structure**:
```json
{
  "_description": "HANA Calculation View Package Mapping",
  "_source": "HANA_CV_MBD.xlsx",
  "_generated_date": "2025-11-19",
  "_instance": "MBD (ECC)",
  "_total_cvs": 167,
  "_unique_packages": 27,

  "mappings": {
    "CV_CNCLD_EVNTS": "EYAL.EYAL_CTL",
    "CV_MCM_CNTRL_Q51": "EYAL.EYAL_CTL",
    ...
  }
}
```

### 2. PackageMapper Module
**Location**: `src/xml_to_sql/package_mapper.py`

Python module providing package lookup functionality.

**Features**:
- Get package for CV name
- Get all CVs in a package (reverse lookup)
- Search CVs by pattern
- Validate package mappings
- List all packages

### 3. CLI Helper
**Location**: `src/xml_to_sql/cli/package_helper.py`

Command-line interface for package operations.

## Usage

### Python API

```python
from xml_to_sql.package_mapper import get_mapper, get_package

# Quick lookup
package = get_package("CV_CNCLD_EVNTS")
# Returns: "EYAL.EYAL_CTL"

# Using mapper instance
mapper = get_mapper()

# Lookup package
package = mapper.get_package("CV_CNCLD_EVNTS")

# Get all CVs in package
cvs = mapper.get_cvs_in_package("EYAL.EYAL_CTL")

# Search CVs
results = mapper.search_cv("MCM_CNTRL")
# Returns: [("CV_MCM_CNTRL", "EYAL.EYAL_CTL"), ...]

# Validate mapping
is_valid = mapper.validate_mapping("CV_CNCLD_EVNTS", "EYAL.EYAL_CTL")

# Get all packages
packages = mapper.get_all_packages()
```

### CLI Commands

#### Get mapping information
```bash
cd xml2sql
python -m xml_to_sql.cli.package_helper info
```

Output:
```
📊 Package Mapping Information

   Source:       HANA_CV_MBD.xlsx
   Generated:    2025-11-19
   Instance:     MBD (ECC)
   Total CVs:    165
   Total Packages: 26
```

#### Lookup package for a CV
```bash
python -m xml_to_sql.cli.package_helper lookup CV_CNCLD_EVNTS
```

Output:
```
✅ CV_CNCLD_EVNTS
   Package: EYAL.EYAL_CTL
```

#### List all CVs in a package
```bash
python -m xml_to_sql.cli.package_helper list EYAL.EYAL_CTL
```

Output:
```
📦 Package: EYAL.EYAL_CTL
   Total CVs: 19

   Calculation Views:
   - CV_CMVZCTLE
   - CV_CNCLD_EVNTS
   - CV_CNTRLAI_REP
   ...
```

#### Search for CVs by pattern
```bash
python -m xml_to_sql.cli.package_helper search MCM_CNTRL
```

Output:
```
🔍 Search: 'MCM_CNTRL'
   Results: 5

   Matches:
   CV_MCM_CNTRL                             → EYAL.EYAL_CTL
   CV_MCM_CNTRL_Q51                         → EYAL.EYAL_CTL
   CV_MCM_CNTRL_REJECTED                    → EYAL.EYAL_CTL
   ...
```

#### List all packages
```bash
python -m xml_to_sql.cli.package_helper packages
```

#### Validate package mapping
```bash
python -m xml_to_sql.cli.package_helper validate CV_CNCLD_EVNTS EYAL.EYAL_CTL
```

Output:
```
🔍 Validating: CV_CNCLD_EVNTS
   Expected: EYAL.EYAL_CTL
   Actual:   EYAL.EYAL_CTL

   ✅ Package mapping is correct
```

## Integration with Conversion Pipeline

### Web API
The PackageMapper can be integrated into the web API to automatically determine package paths:

```python
from xml_to_sql.package_mapper import get_package

# In converter service
hana_package = get_package(cv_name) or config.hana_package
```

### CLI Converter
The CLI app can use automatic package lookup:

```python
from xml_to_sql.package_mapper import get_package

# Before conversion
if not scenario_cfg.hana_package:
    # Try automatic lookup
    scenario_cfg.hana_package = get_package(scenario_cfg.id)
```

### Regression Testing
Update regression tests to use package mappings:

```python
from xml_to_sql.package_mapper import get_package

# In test cases
cv_name = "CV_CNCLD_EVNTS"
package = get_package(cv_name) or "EYAL.EYAL_CTL"  # fallback
```

## Package Statistics

Based on MBD (ECC) instance export:

| Package | CV Count |
|---------|----------|
| Macabi.CTL | 32 |
| ICM | 23 |
| EYAL.EYAL_CTL | 19 |
| system-local.bw.bw2hana | 12 |
| Macabi.MD | 10 |
| ICM.ERRORS | 9 |
| ICM.STAGING.100 | 9 |
| HANA_DEMO | 7 |
| Macabi.HR | 6 |
| sap.erp.sappl.mm.pur.po-history | 5 |

## Updating Package Mappings

### From Excel Export

1. Export CV list from HANA instance to Excel with columns:
   - `PACKAGE_ID` - Package path
   - `OBJECT_NAME` - CV name

2. Save as `HANA_CV_MBD.xlsx` in project root

3. Run generation script:
```bash
python generate_package_mapping.py
```

4. Verify mappings:
```bash
python test_package_mapper.py
```

### Manual Updates

Edit `package_mapping.json` directly:

```json
{
  "mappings": {
    "NEW_CV_NAME": "Package.Path",
    ...
  }
}
```

## Validation

### Test Script
Run comprehensive tests:
```bash
python test_package_mapper.py
```

Tests cover:
- Metadata loading
- CV lookup (exact and case-insensitive)
- Package validation
- Reverse lookup (package → CVs)
- Search functionality
- Package listing

### Integration Test
Verify with actual conversion:
```bash
cd xml2sql
python -m xml_to_sql.cli.package_helper lookup CV_CNCLD_EVNTS
python -m xml_to_sql.cli.app convert --file "Source (XML Files)/..." --mode hana
```

## Benefits

1. **Automatic Package Detection**: No need to manually specify package paths
2. **Validation**: Verify CVs are in correct packages before conversion
3. **Discovery**: Search and explore available CVs and packages
4. **Consistency**: Single source of truth for package mappings
5. **Maintenance**: Easy to update when HANA structure changes

## Future Enhancements

1. **Multiple Instances**: Support mappings from multiple HANA instances (MBD, BWD, etc.)
2. **Auto-detection**: Automatically detect instance from XML metadata
3. **Schema Prefix**: Auto-add `_SYS_BIC` schema prefix when needed
4. **Web UI**: Visual interface for exploring packages and CVs
5. **Fuzzy Search**: More intelligent CV name matching
6. **History**: Track package changes over time

## See Also

- [llm_handover.md](llm_handover.md) - Project overview and session history
- [GOLDEN_COMMIT.yaml](../GOLDEN_COMMIT.yaml) - Validated commits tracking
- [SOLVED_BUGS.md](bugs/SOLVED_BUGS.md) - Bug fix documentation
