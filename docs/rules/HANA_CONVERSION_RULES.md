# HANA Conversion Rules

**Target Database**: SAP HANA (SQL Views)
**Version**: 2.4.0
**Last Updated**: 2025-11-16
**Validated**:
- CV_CNCLD_EVNTS.xml (ECC, 243L, 84ms)
- CV_INVENTORY_ORDERS.xml (BW, 220L, 34ms)
- CV_PURCHASE_ORDERS.xml (BW, ~220L, 29ms)
- CV_EQUIPMENT_STATUSES.xml (BW, 170L, 32ms)
- CV_TOP_PTHLGY.xml (BW, 2139L, in progress)

---

## Purpose

This document contains **ONLY** the transformation rules for converting HANA Calculation View XMLs to **HANA SQL** (native HANA views, not Snowflake).

**Use this when**: `database_mode: hana`

---

## Rule Execution Order

Rules applied in priority order (lower number = earlier execution):

1. **Priority 10**: Legacy function rewrites (LEFTSTR, RIGHTSTR)
2. **Priority 15**: Calculated column expansion
3. **Priority 20**: Uppercase functions
4. **Priority 30**: IN operator → OR conditions
5. **Priority 40**: IF → CASE WHEN
6. **Priority 45**: Empty string → NULL
7. **Priority 50**: String concatenation (|| → +)
8. **Priority 60**: Subquery wrapping
9. **Priority 70**: Column qualification
10. **Priority 80**: Parameter removal

---

## HANA-Specific Transformation Rules

### Rule 1: IF() to CASE WHEN (Priority 40)

**Rule ID**: `HANA_1_0_IF_TO_CASE`  
**Applies To**: All HANA versions >=1.0  
**Category**: Conditional expressions

**Why**: HANA SQL views don't support `IF()` function in SELECT clauses.

**Transformation**:
```
Source:  IF(condition, then_value, else_value)
Target:  CASE WHEN condition THEN then_value ELSE else_value END
```

**Example**:
```sql
-- Before
IF(RIGHT("CALMONTH", 2) = '01', '2015' + '1', '')

-- After
CASE WHEN RIGHT("CALMONTH", 2) = '01' THEN '2015' + '1' ELSE NULL END
```

**Implementation**: `function_translator.py::_convert_if_to_case_for_hana()`

**Validated**: CV_CNCLD_EVNTS.xml (12 IF statements converted)

---

### Rule 2: IN Operator to OR Conditions (Priority 30)

**Rule ID**: `HANA_1_0_IN_TO_OR`  
**Applies To**: All HANA versions >=1.0  
**Category**: Operators

**Why**: HANA doesn't support `IN` operator inside conditional expressions (IF/CASE context).

**Transformation**:
```
Source:  (expression IN (val1, val2, val3))
Target:  (expression = val1 OR expression = val2 OR expression = val3)
```

**Example**:
```sql
-- Before
(RIGHT("CALMONTH", 2) IN ('01', '02', '03'))

-- After  
(RIGHT("CALMONTH", 2) = '01' OR RIGHT("CALMONTH", 2) = '02' OR RIGHT("CALMONTH", 2) = '03')
```

**Implementation**: `function_translator.py::_convert_in_to_or_for_hana()`

**Validated**: CV_CNCLD_EVNTS.xml (multiple IN operators converted)

---

### Rule 3: String Concatenation (Priority 50)

**Rule ID**: `HANA_1_0_STRING_CONCAT`  
**Applies To**: All HANA versions >=1.0  
**Category**: Operators  
**Exception**: Don't convert inside REGEXP_LIKE()

**Why**: HANA uses `+` operator for string concatenation (traditional), though `||` is also supported.

**Transformation**:
```
Source:  string1 || string2
Target:  string1 + string2
```

**Example**:
```sql
-- Before
SUBSTRING("ZZTREAT_DATE", 1, 4) || '1'

-- After
SUBSTRING("ZZTREAT_DATE", 1, 4) + '1'
```

**Implementation**: `function_translator.py::_translate_string_concat_to_hana()`  
**Protection**: Preserves `||` inside `REGEXP_LIKE()` calls

**Validated**: CV_CNCLD_EVNTS.xml

---

### Rule 4: Uppercase Functions (Priority 20)

**Rule ID**: `HANA_1_0_UPPERCASE_IF`  
**Applies To**: All HANA versions >=1.0  
**Category**: Syntax normalization

**Why**: HANA requires uppercase function names.

**Transformation**:
```
Source:  if(condition, ...)
Target:  IF(condition, ...)
```

**Implementation**: `function_translator.py::_uppercase_if_statements()`

**Also applies to**: AND keywords in cleanup phase

---

### Rule 5: LEFTSTR/RIGHTSTR (Version-Dependent)

**HANA 1.0**: `HANA_1_0_LEFTSTR_PRESERVE`  
**HANA 2.0+**: `HANA_2_0_LEFTSTR_MODERNIZE`

**For HANA 1.0**:
```
Source:  leftstr("CALMONTH", 2)
Target:  LEFTSTR("CALMONTH", 2)  (preserve legacy function)
```

**For HANA 2.0+**:
```
Source:  leftstr("CALMONTH", 2)
Target:  SUBSTRING("CALMONTH", 1, 2)  (modernize)
```

**Implementation**: `function_translator.py::_translate_for_hana()`

---

### Rule 6: Calculated Column Expansion (Priority 15)

**Rule ID**: `HANA_1_0_CALC_COL_EXPANSION`  
**Applies To**: All HANA versions >=1.0  
**Category**: Structural transformation

**Why**: SQL doesn't allow referencing column aliases in the same SELECT clause.

**Problem**:
```sql
SELECT 
    SUBSTRING("DATE", 1, 6) AS CALMONTH,
    RIGHT("CALMONTH", 2) AS QUARTER  -- ERROR: CALMONTH not defined yet
```

**Solution**:
```sql
SELECT 
    SUBSTRING("DATE", 1, 6) AS CALMONTH,
    RIGHT(SUBSTRING("DATE", 1, 6), 2) AS QUARTER  -- Expanded inline
```

**Implementation**: `renderer.py::_render_projection()` with calc_column_map

**Validated**: CV_CNCLD_EVNTS.xml (CALQUARTER references CALMONTH)

---

### Rule 7: Subquery Wrapping (Priority 60)

**Rule ID**: `HANA_1_0_SUBQUERY_WRAP`  
**Applies To**: All HANA versions >=1.0  
**Category**: Structural transformation

**Why**: Filters can't reference calculated columns in the same SELECT.

**Transformation**:
```sql
-- Before (INVALID)
SELECT 
    SUBSTRING("DATE", 1, 6) AS CALMONTH
FROM table
WHERE CALMONTH = '202401'  -- ERROR: CALMONTH not in scope

-- After (VALID)
SELECT * FROM (
  SELECT SUBSTRING("DATE", 1, 6) AS CALMONTH
  FROM table
) AS calc
WHERE calc.CALMONTH = '202401'  -- OK: calc.CALMONTH exists
```

**Implementation**: `renderer.py::_render_projection()` needs_subquery logic

**Validated**: CV_CNCLD_EVNTS.xml (3 projections wrapped)

---

### Rule 8: Column Qualification (Priority 70)

**Rule ID**: `HANA_1_0_COLUMN_QUALIFICATION`  
**Applies To**: All HANA versions >=1.0  
**Category**: Structural transformation

**Why**: When using subqueries, all column references in WHERE must be qualified.

**Transformation**:
```
Source:  WHERE ("COLUMN" = 'value')
Target:  WHERE (calc."COLUMN" = 'value')
```

**Implementation**: `renderer.py::_render_projection()` - regex qualification

**Validated**: CV_CNCLD_EVNTS.xml

---

### Rule 9: Parameter Removal (Priority 80)

**Rule ID**: `HANA_1_0_PARAMETER_REMOVAL`  
**Applies To**: All HANA versions >=1.0  
**Category**: Parameter handling

**Why**: HANA SQL views don't support runtime parameters like calculation views.

**Strategy**: Remove parameter filter clauses entirely.

**Original**:
```xml
('$$IP_TREAT_DATE$$' = '' OR "ZZTREAT_DATE" = '$$IP_TREAT_DATE$$')
```

**After substitution**:
```sql
('' = '' OR "ZZTREAT_DATE" = '')  -- Always true, pointless
```

**Final** (cleaned):
```sql
-- Entire clause removed
```

**Implementation**: 
- `function_translator.py::_substitute_placeholders()` - Replace with ''
- `renderer.py::_cleanup_hana_parameter_conditions()` - Remove clauses

**Limitations**: 
- Complex DATE() patterns may leave fragments
- Nested parameters may cause orphaned parens
- See CV_MCM_CNTRL_Q51_DEBUGGING_NOTES.md

---

### Rule 10: NULL Fallback (Priority 45)

**Rule ID**: `HANA_1_0_NULL_FALLBACK`  
**Applies To**: All HANA versions >=1.0  
**Category**: Data type handling

**Why**: Empty string in CASE ELSE causes "invalid number" error in numeric contexts.

**Transformation**:
```
Source:  ELSE ''
Target:  ELSE NULL
```

**Implementation**: `function_translator.py::_convert_if_to_case_for_hana()`

---

### Rule 11: VIEW Creation Syntax

**Snowflake**: `CREATE OR REPLACE VIEW <view_name> AS`  
**HANA**:

```
DROP VIEW <schema>.<view_name> CASCADE;
CREATE VIEW <schema>.<view_name> AS
```

- Default schema today: `SAPABAP1` (configurable via `defaults.view_schema` or per-scenario `overrides.schema`)
- Applies to both ECC and BW conversions
- Ensures re-runs always recreate the view cleanly

**Implementation**: 
- `config`: `defaults.view_schema`, `overrides.schema`
- `cli/app.py` + `web/services/converter.py` – pass schema-qualified view name
- `renderer.py::_generate_view_statement()` – renders DROP/CREATE with schema

---

### Rule 12: Filter/GROUP BY Source Mapping (Priority 25)

**Rule ID**: `HANA_SOURCE_NAME_MAPPING`  
**Applies To**: All HANA versions, all node types  
**Category**: Column name resolution

**Why**: XML uses target/alias names but SQL needs source/actual column names for base table queries.

**Problem**: User naming convention adds table suffixes (LOEKZ→LOEKZ_EKPO) to distinguish columns from different sources.

**Transformations**:
1. **Projection Filters**: `WHERE ("LOEKZ_EKPO" = '')` → `WHERE ("LOEKZ" = '')`
2. **Aggregation GROUP BY**: `GROUP BY WAERS_EKKO` → `GROUP BY join_4.WAERS`
3. **Aggregation Specs**: `SUM(WEMNG_EKET)` → `SUM(join_4.WEMNG)`

**Implementation**: 
- `renderer.py::_render_projection()` - Lines 419-439 (filter mapping)
- `renderer.py::_render_aggregation()` - Lines 588-603 (GROUP BY), 611-631 (aggregation specs)

**Validated**: CV_INVENTORY_ORDERS.xml (220 lines, executes successfully)

---

### Rule 13: ColumnView JOIN Parsing (Priority 5)

**Rule ID**: `COLUMNVIEW_JOIN_PARSING`  
**Applies To**: ColumnView XML format (HANA 1.x era)  
**Category**: Parser enhancement

**Why**: ColumnView JOINs have different XML structure than Calculation:scenario JOINs.

**XML Pattern**:
```xml
<viewNode xsi:type="View:JoinNode" name="Join_6">
  <join leftInput="#//Join_6/Projection_6" rightInput="#//Join_6/Projection_8" joinType="inner">
    <leftElementName>EBELN_EKPO</leftElementName>
    <rightElementName>EBELN</rightElementName>
  </join>
</viewNode>
```

**Implementation**: `parser/column_view_parser.py` - Added JoinNode handler with join type/condition parsing

**Validated**: CV_INVENTORY_ORDERS join_6 renders with correct INNER JOIN syntax

---

### Rule 14: Aggregation Calculated Columns (Priority 55)

**Rule ID**: `AGGREGATION_CALC_COLS`  
**Applies To**: Aggregation nodes with calculated columns  
**Category**: Structural transformation

**Why**: Calculated columns in aggregations must be computed AFTER grouping.

**Structure**:
```sql
aggregation AS (
  SELECT
      agg_inner.*,
      SUBSTRING(agg_inner."AEDAT_EKKO", 1, 6) AS MONTH  -- After grouping
  FROM (
    SELECT dimensions, SUM(measures)
    FROM input
    GROUP BY dimensions
  ) AS agg_inner
)
```

**Implementation**: `renderer.py::_render_aggregation()` - Lines 647-673

**Validated**: MONTH, YEAR in CV_INVENTORY_ORDERS

---

### Rule 14: Legacy Type Cast Functions (STRING, INT)

**Rule ID**: `HANA_LEGACY_TYPE_CASTS`
**Applies To**: All HANA versions
**Category**: Function mapping
**Discovered**: 2025-11-16, CV_TOP_PTHLGY.xml
**Bugs Fixed**: BUG-013, BUG-017

**Why**: Legacy XML formulas use simplified type cast functions that don't exist in HANA SQL.

**Transformations**:
```
Source:  string(FIELD)       →  Target: TO_VARCHAR(FIELD)
Source:  int(FIELD)           →  Target: TO_INTEGER(FIELD)
Source:  decimal(FIELD, P, S) →  Target: TO_DECIMAL(FIELD, P, S)  (if discovered)
Source:  date(FIELD)          →  Target: TO_DATE(FIELD)
```

**Implementation**: `functions.yaml` catalog entries:
- `STRING` → `TO_VARCHAR`
- `INT` → `TO_INTEGER`

**Catalog Entry**:
```yaml
  - name: STRING
    handler: rename
    target: "TO_VARCHAR"

  - name: INT
    handler: rename
    target: "TO_INTEGER"
```

**Validated**: CV_TOP_PTHLGY.xml

---

### Rule 15: Function Name Case Sensitivity

**Rule ID**: `HANA_FUNCTION_UPPERCASE`
**Applies To**: All HANA versions
**Category**: Syntax normalization
**Discovered**: 2025-11-16, CV_TOP_PTHLGY.xml
**Bug Fixed**: BUG-016

**Why**: HANA SQL functions are case-sensitive and must be uppercase.

**Transformations**:
```
Source:  adddays(date, -3)   →  Target: ADD_DAYS(date, -3)
Source:  daysbetween(d1, d2) →  Target: DAYS_BETWEEN(d1, d2)
Source:  substring(str, 1, 4)→  Target: SUBSTRING(str, 1, 4)
```

**Implementation**: `functions.yaml` catalog entries with uppercase targets

**Catalog Entry**:
```yaml
  - name: ADDDAYS
    handler: rename
    target: "ADD_DAYS"

  - name: DAYSBETWEEN
    handler: rename
    target: "DAYS_BETWEEN"
```

**Validated**: CV_TOP_PTHLGY.xml

---

### Rule 16: TIMESTAMP Arithmetic (CRITICAL - Needs Pattern Matching)

**Rule ID**: `HANA_TIMESTAMP_ARITHMETIC`
**Applies To**: All HANA versions
**Category**: Expression pattern rewrite
**Discovered**: 2025-11-16, CV_TOP_PTHLGY.xml
**Bug Fixed**: BUG-015 (partial - manual fix only)
**Status**: ⚠️ REQUIRES PATTERN MATCHING SYSTEM

**Why**: HANA doesn't support direct arithmetic operations on TIMESTAMP types.

**Problem**:
```sql
-- INVALID in HANA
TO_DATE(CURRENT_TIMESTAMP - 365)
TO_DATE(NOW() - 270)
date(NOW() - 365)
```

**Solution**:
```sql
-- VALID in HANA
TO_DATE(ADD_DAYS(CURRENT_TIMESTAMP, -365))
TO_DATE(ADD_DAYS(CURRENT_DATE, -270))
ADD_DAYS(CURRENT_DATE, -365)
```

**Current Implementation**: Manual `sed` patch (NOT SUSTAINABLE)

**Proper Solution Needed**: Pattern matching system

**Pattern Catalog** (proposed in `PATTERN_MATCHING_DESIGN.md`):
```yaml
patterns:
  - name: "timestamp_minus_days"
    match: "CURRENT_TIMESTAMP\\s*-\\s*(\\d+)"
    hana: "ADD_DAYS(CURRENT_TIMESTAMP, -$1)"

  - name: "now_minus_days"
    match: "NOW\\(\\)\\s*-\\s*(\\d+)"
    hana: "ADD_DAYS(CURRENT_DATE, -$1)"

  - name: "date_now_minus"
    match: "date\\s*\\(\\s*NOW\\(\\)\\s*-\\s*(\\d+)\\s*\\)"
    hana: "ADD_DAYS(CURRENT_DATE, -$1)"
```

**See**: `PATTERN_MATCHING_DESIGN.md` for full implementation plan

**Validated**: CV_TOP_PTHLGY.xml (with manual patch)

---

### Rule 17: Schema Name Mapping

**Rule ID**: `HANA_SCHEMA_MAPPING`
**Applies To**: All HANA versions
**Category**: Configuration-driven transformation
**Discovered**: 2025-11-16, CV_TOP_PTHLGY.xml
**Bug Fixed**: BUG-014

**Why**: Different HANA instances use different schema naming conventions.

**Problem**: XML specifies `ABAP` schema, but actual HANA instance uses `SAPABAP1`.

**Solution**: Configuration override in `config.yaml`:
```yaml
schema_overrides:
  ABAP: "SAPABAP1"
  SAPK5D: "PRODUCTION_SCHEMA"  # Example for other mappings
```

**Implementation**: `renderer.py::render_scenario()` accepts `schema_overrides` parameter

**Common Mappings**:
- `ABAP` → `SAPABAP1` (most common)
- `SAPK5D` → customer-specific schema
- `_SYS_BIC` → preserved (calculation view catalog)

**Validated**: CV_TOP_PTHLGY.xml

---

## Known Limitations (HANA Mode)

### ❌ **NOT Implemented:**
1. ~~**Filter alias mapping**~~ ✅ SOLVED (Rule #12)
2. **Complex parameter cleanup** - DATE() nesting, multiple levels (CV_MCM_CNTRL_Q51)
3. **REGEXP_LIKE parameter patterns** - Special handling needed (CV_CT02_CT03)
4. **BW wrapper mode** - Implemented but optional

### ✅ **Working:**
1. All core transformations (IF, IN, strings, etc.)
2. Calculated column expansion
3. Subquery wrapping
4. Column qualification
5. Simple parameter removal
6. Version-aware function handling

---

## Files Reference

**Rules Catalog**: `src/xml_to_sql/catalog/data/conversion_rules.yaml`  
**Function Catalog**: `src/xml_to_sql/catalog/data/functions.yaml`  
**Implementation**: `src/xml_to_sql/sql/function_translator.py`, `src/xml_to_sql/sql/renderer.py`

---

**Status**: Core rules working for standard ECC calculation views. Edge cases documented for future refinement.

