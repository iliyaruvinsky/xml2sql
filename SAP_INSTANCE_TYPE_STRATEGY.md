# SAP Instance Type Conversion Strategy

**Purpose**: Different SAP instance types require different SQL generation approaches  
**Version**: 2.3.0  
**Date**: 2025-11-13

---

## Instance Types Tested

### 1. SAP ECC (Enterprise Core Components)

**Instance Example**: MBD (Production ECC)  
**Schema Pattern**: `SAPABAP1`, `SAPK5D`, etc.  
**Tables**: Standard SAP tables (VBAP, MARA, BSEG, etc.)

**Conversion Approach**: ✅ **Raw SQL Expansion** (Goal A)

**Strategy**:
- Parse XML calculation view
- Extract table references and transformations
- Generate SQL querying base tables directly
- Apply HANA-specific transformations (IF→CASE, IN→OR, etc.)

**Example**:
```sql
CREATE VIEW CV_CNCLD_EVNTS AS
WITH ctleqr AS (
  SELECT columns...
  FROM SAPABAP1.ZBW_CTL_HD_RE
  WHERE conditions...
)
SELECT * FROM ctleqr;
```

**Status**: ✅ **WORKING** - CV_CNCLD_EVNTS.xml executes successfully (243 lines, 84ms)

---

### 2. SAP BW (Business Warehouse)

**Instance Example**: BID (BW Development)  
**Schema Pattern**: `_SYS_BIC` for calculation views, complex for base tables  
**Objects**: BW InfoCubes, DSOs, calculation views

**Conversion Approach**: ✅ **Calculation View Wrapper** (Goal B)

**Strategy**:
- Parse XML to extract view package/name
- Generate SQL that queries existing calculation view from `_SYS_BIC`
- Simpler, preserves BW semantics and parameters

**Example**:
```sql
CREATE VIEW CV_INVENTORY_ORDERS AS
SELECT * FROM "_SYS_BIC"."Macabi_BI.COOM/CV_INVENTORY_ORDERS";
```

**Rationale**:
- BW calculation views are complex compiled objects
- Underlying tables use BW-specific naming (`/BIC/A*2`, `/BI0/A*00`)
- Table schema resolution is complex in BW
- Querying the calc view preserves all BW logic
- Parameters still work (if calc view has them)

**Status**: 🔮 **To Implement** - Wrapper approach for BW objects

---

## BW-Specific Naming Conventions

### BW DSO Active Tables

**Custom Objects** (locally created):
```
BW DSO Name:    ZEKPO
Active Table:   /BIC/AZEKPO2
Pattern:        /BIC/A<name>2
```

**Standard SAP Objects** (starting with 0):
```
BW DSO Name:    0CCA_O10
Active Table:   /BI0/ACCA_O1000
Pattern:        /BI0/A<name_without_0>00
Transformation: Remove leading "0", add "/BI0/A" prefix, add "00" suffix
```

**Components**:
- `/BIC/` = Custom/local BW objects
- `/BI0/` = SAP standard BW objects
- `A` = Active table indicator
- `2` or `00` = Active table suffix

### Schema Resolution Issues

**Calculation View Context**:
- Views stored in: `_SYS_BIC`
- Query as: `SELECT * FROM "_SYS_BIC"."Package/ViewName"`

**Direct Table Access** (problematic):
- XML specifies: `ABAP` schema
- But SQL rejects: `invalid schema name: ABAP`
- Actual schema: Unknown/varies by BW configuration

**Conclusion**: For BW, use calc view wrappers (Goal B) instead of raw expansion (Goal A)

---

## Detection Strategy

### How to Identify Instance Type from XML

**Indicators for BW**:
1. Table names start with `/BIC/` or `/BI0/`
2. Schema name is `ABAP` (generic BW placeholder)
3. XML package path contains `_SYS_BIC`
4. DataCategory = "CUBE" with BW-style InfoCube structure

**Indicators for ECC**:
1. Schema names like `SAPABAP1`, `SAPK5D`, `SAP<SID>`
2. Standard SAP table names (VBAP, EKKO, BSEG, etc.)
3. No `/BIC/` or `/BI0/` prefixes
4. Direct table references

**Implementation**:
```python
def detect_instance_type(scenario: Scenario) -> str:
    """Detect if this is BW or ECC based on data sources."""
    for ds in scenario.data_sources.values():
        table_name = ds.object_name or ""
        schema_name = ds.schema_name or ""
        
        # BW indicators
        if table_name.startswith("/BIC/") or table_name.startswith("/BI0/"):
            return "BW"
        if schema_name == "ABAP":
            return "BW"
        
        # ECC indicators (default)
        if schema_name.startswith("SAP"):
            return "ECC"
    
    return "ECC"  # Default
```

---

## Conversion Mode Matrix

| Instance Type | Detection | Approach | Schema Handling | Status |
|--------------|-----------|----------|-----------------|--------|
| **SAP ECC** | SAP* schemas, standard tables | Raw SQL Expansion (A) | Direct schema.table | ✅ Working |
| **SAP BW** | /BIC/, /BI0/, ABAP schema | Calc View Wrapper (B) | _SYS_BIC."package/view" | 🔮 To Implement |
| **Snowflake** | Target, not source | Raw SQL (always) | Configurable overrides | ✅ Working |

---

## Implementation Plan

### Phase 1: Current (v2.3.0)
- ✅ ECC support with raw SQL expansion
- ✅ Snowflake support
- ✅ HANA mode with all transformations
- ⏳ BW identified but uses same approach as ECC (fails on schema)

### Phase 2: BW Support (v2.4.0)
- 🔮 Detect BW vs ECC from XML
- 🔮 Add `--bw-mode` option: `expand` vs `wrapper`
- 🔮 Implement calc view wrapper generation
- 🔮 Extract package/view name from XML
- 🔮 Generate `FROM "_SYS_BIC"."package/view"` syntax

### Implementation Files

**To Create**:
- `src/xml_to_sql/bw/` - New module for BW-specific logic
- `src/xml_to_sql/bw/wrapper_generator.py` - Generate calc view wrappers
- `src/xml_to_sql/bw/naming_conventions.py` - BW DSO naming rules

**To Modify**:
- `src/xml_to_sql/parser/xml_format_detector.py` - Add instance type detection
- `src/xml_to_sql/sql/renderer.py` - Route BW objects to wrapper generator
- `src/xml_to_sql/config/schema.py` - Add `instance_type` field

---

## Example Outputs

### ECC Calculation View (Current - Works)

**XML**: CV_CNCLD_EVNTS.xml (ECC tables: SAPABAP1.ZBW_CTL_HD_RE)

**Generated SQL**:
```sql
CREATE VIEW CV_CNCLD_EVNTS AS
WITH ctleqr AS (
  SELECT ... FROM SAPABAP1.ZBW_CTL_HD_RE WHERE ...
)
SELECT * FROM ctleqr;
```

### BW Calculation View (Future)

**XML**: CV_INVENTORY_ORDERS.xml (BW tables: /BIC/AZEKPO2)

**Generated SQL** (Wrapper approach):
```sql
CREATE VIEW CV_INVENTORY_ORDERS AS
SELECT * FROM "_SYS_BIC"."Macabi_BI.COOM/CV_INVENTORY_ORDERS";
```

**Or with transformations**:
```sql
CREATE VIEW CV_INVENTORY_ORDERS_ENHANCED AS
SELECT 
    "MONTH",
    "YEAR",
    "BSART_EKKO",
    -- ... specific columns
FROM "_SYS_BIC"."Macabi_BI.COOM/CV_INVENTORY_ORDERS"
WHERE additional_conditions;
```

---

## Configuration

### config.yaml Enhancement

```yaml
defaults:
  database_mode: "hana"
  hana_version: "2.0"
  instance_type: "auto"  # auto | ecc | bw

scenarios:
  # ECC View
  - id: "CV_CNCLD_EVNTS"
    source: "OLD_HANA_VIEWS/CV_CNCLD_EVNTS.xml"
    instance_type: "ecc"  # Use raw SQL expansion
    database_mode: "hana"
    
  # BW View
  - id: "CV_INVENTORY_ORDERS"
    source: "OLD_HANA_VIEWS/CV_INVENTORY_ORDERS.xml"
    instance_type: "bw"   # Use calc view wrapper
    bw_package: "Macabi_BI.COOM"  # For _SYS_BIC path
```

---

## Rules Catalog Update

Add to `src/xml_to_sql/catalog/data/conversion_rules.yaml`:

```yaml
  - rule_id: BW_CALC_VIEW_WRAPPER
    target_database: hana
    instance_type: bw
    source_pattern: "BW calculation view with /BIC/ or /BI0/ tables"
    target_pattern: 'SELECT * FROM "_SYS_BIC"."package/viewname"'
    applies_to: structure
    priority: 5
    description: >
      BW calculation views should be queried from _SYS_BIC, not expanded to base tables.
      Base tables use complex BW naming (/BIC/A*2, /BI0/A*00) and schema resolution is complex.
      Wrapper approach preserves BW semantics and parameters.

  - rule_id: ECC_TABLE_EXPANSION
    target_database: hana
    instance_type: ecc
    source_pattern: "ECC calculation view with SAP* schema tables"
    target_pattern: "Expanded raw SQL with transformations"
    applies_to: structure
    priority: 5
    description: >
      ECC calculation views expand to raw SQL querying base tables.
      Schemas like SAPABAP1 are directly accessible.
      Full transformation pipeline applies (IF→CASE, IN→OR, etc.)
```

---

## Current Status

**Working**:
- ✅ SAP ECC: CV_CNCLD_EVNTS.xml (raw SQL, 243 lines, executes successfully)

**Deferred** (Complex parameters):
- ⏳ SAP ECC: CV_MCM_CNTRL_Q51.xml (complex DATE() parameter patterns)
- ⏳ SAP ECC: CV_CT02_CT03.xml (REGEXP_LIKE + parameter patterns)

**Identified** (Need BW wrapper approach):
- 🔮 SAP BW: CV_INVENTORY_ORDERS.xml (schema resolution issue, needs wrapper)
- 🔮 SAP BW: CV_PURCHASE_ORDERS.xml (likely same)

---

## Next Steps

1. ✅ **Document BW vs ECC** strategy (this document)
2. 🔮 **Implement BW wrapper** generator (v2.4.0)
3. ✅ **Continue testing ECC XMLs** with current approach
4. 🔮 **Test BW wrapper** approach when implemented

---

**Recommendation for NOW**: 
- Continue testing **ECC calculation views** (like CV_CNCLD_EVNTS)
- **Defer BW views** until wrapper approach implemented
- Focus on validating ECC transformation rules work correctly

**Files to test next** (ECC, non-BW):
- Any XMLs using `SAPABAP1`, `SAPK5D` schemas
- Simpler parameter patterns than CV_MCM_CNTRL_Q51

---

**Status**: BW vs ECC strategy documented. BW wrapper approach designed for future implementation.

