# Solved Bugs - HANA Mode Conversion

**Purpose**: Archive of resolved bugs with solutions and rule associations  
**Version**: 2.3.0

---

## Template

Each solved bug documents:
1. Original error and symptoms
2. Root cause analysis
3. Solution implemented
4. Code changes made
5. Associated conversion rules
6. Validation status

---

## Resolved Issues

### SOLVED-001: ColumnView JOIN Node Parsing

**Original Bug**: BUG-005  
**Discovered**: 2025-11-13, CV_INVENTORY_ORDERS.xml  
**Resolved**: 2025-11-13

**Error**:
```
invalid column name: PROJECTION_6.EINDT (should be projection_8.EINDT)
```

**Problem**:
ColumnView JOINs were not being parsed as JoinNode objects - they fell through to generic Node type, missing JOIN-specific parsing (join conditions, left/right input tracking).

**Root Cause**:
`column_view_parser.py` had handlers for Projection, Aggregation, Union but NOT for JoinNode. ColumnView JOIN nodes (`xsi:type="View:JoinNode"`) were falling through to the catchall generic Node handler.

**Solution**:
Added JoinNode parsing to ColumnView parser:

```python
if node_type.endswith("JoinNode"):
    join_type = _parse_join_type(node_el)
    join_conditions = _parse_join_conditions(node_el, inputs)
    return JoinNode(...)

def _parse_join_type(node_el):
    # Extract from <join joinType="inner">

def _parse_join_conditions(node_el, inputs):
    # Extract from <leftElementName> and <rightElementName>
```

**Files Modified**:
- `src/xml_to_sql/parser/column_view_parser.py` - Lines 174-192 (JoinNode handler), 340-392 (helper functions)

**Related Rules**: None (parser fix, not transformation rule)

**Validation**: ✅ CV_INVENTORY_ORDERS now creates proper JoinNode, renders with correct INNER JOIN syntax

---

### SOLVED-002: JOIN Column Resolution - Source Node Tracking

**Original Bug**: BUG-006  
**Discovered**: 2025-11-13, CV_INVENTORY_ORDERS.xml  
**Resolved**: 2025-11-13

**Error**:
```
invalid column name: PROJECTION_6.EINDT (EINDT is in projection_8, not projection_6)
```

**Problem**:
JOIN nodes with multiple inputs (leftInput, rightInput) were using wrong CTE alias for columns from right input.

**SQL Before**:
```sql
SELECT 
    projection_6.EINDT AS EINDT  -- WRONG: EINDT from projection_8
FROM projection_6
INNER JOIN projection_8 ...
```

**SQL After**:
```sql
SELECT 
    projection_8.EINDT AS EINDT  -- CORRECT
FROM projection_6
INNER JOIN projection_8 ...
```

**Root Cause**:
JOIN renderer already had `source_node` logic (lines 547-554) but ColumnView parser wasn't setting `source_node` in mappings properly due to SOLVED-001 (JoinNode not being created).

**Solution**:
Once JoinNode parsing was fixed (SOLVED-001), the existing renderer logic worked correctly.

**Files Modified**:
- `src/xml_to_sql/parser/column_view_parser.py` (via SOLVED-001 fix)

**Related Rules**: None (core rendering logic)

**Validation**: ✅ join_6 now correctly uses projection_8.EINDT, projection_8.WEMNG

---

### SOLVED-003: Filter Alias vs Source Name Mapping

**Original Bug**: BUG-004  
**Discovered**: 2025-11-13, CV_INVENTORY_ORDERS.xml  
**Resolved**: 2025-11-13

**Error**:
```
SAP DBTech JDBC: [260]: invalid column name: LOEKZ_EKPO: line 67 col 12
```

**Problem**:
Filters referenced target/alias column names instead of source column names when querying base tables.

**SQL Before**:
```sql
SELECT SAPABAP1."/BIC/AZEKPO2".LOEKZ AS LOEKZ_EKPO ...
WHERE ("LOEKZ_EKPO" ='')  -- ERROR: alias doesn't exist
```

**SQL After**:
```sql
SELECT SAPABAP1."/BIC/AZEKPO2".LOEKZ AS LOEKZ_EKPO ...
WHERE ("LOEKZ" ='')  -- FIXED: source column name
```

**Root Cause**:
- XML filters use element names: `<element name="LOEKZ_EKPO">` with `<filterExpression>"LOEKZ_EKPO" = ''</filterExpression>`
- But mappings show: `targetName="LOEKZ_EKPO" sourceName="LOEKZ"`
- SQL WHERE can't use aliases, needs actual column names

**Solution**:
Build target→source mapping from node.mappings and replace in WHERE clause.

**Code Changes**:
File: `src/xml_to_sql/sql/renderer.py`  
Function: `_render_projection()`  
Lines: 419-439

```python
# Build target→source name mapping
target_to_source_map = {}
for mapping in node.mappings:
    if mapping.expression.expression_type == ExpressionType.COLUMN:
        source_col = mapping.expression.value
        target_col = mapping.target_name
        if source_col != target_col:
            target_to_source_map[target_col.upper()] = source_col

# Replace target names with source names in WHERE
for target_name, source_name in target_to_source_map.items():
    where_clause = where_clause.replace(f'"{target_name}"', f'"{source_name}"')
```

**Associated Rules**:
- **Created**: Rule #12 - Filter Source Mapping
- **Priority**: 25
- **Category**: Column name resolution

**Validation**: ✅ WHERE now uses source column names

---

### SOLVED-004: Aggregation Calculated Columns

**Original Bug**: BUG-007  
**Discovered**: 2025-11-13, CV_INVENTORY_ORDERS.xml  
**Resolved**: 2025-11-13

**Error**:
```
invalid column name: JOIN_4.MONTH (MONTH is calculated, not in join_4)
```

**Problem**:
Aggregation nodes with calculated columns (MONTH, YEAR) weren't rendering them - treating them as passthrough from input.

**Root Cause**:
`_render_aggregation()` only rendered:
- Group by columns
- Aggregation specs (SUM, COUNT, etc.)

But NOT `node.calculated_attributes`.

**Solution**:
Added calculated column rendering to aggregations:

```python
# Add calculated columns (computed in outer query after grouping)
for calc_name, calc_attr in node.calculated_attributes.items():
    calc_expr = _render_expression(ctx, calc_attr.expression, "agg_inner")
    outer_select.append(f"{calc_expr} AS {_quote_identifier(calc_name)}")
```

**Files Modified**:
- `src/xml_to_sql/sql/renderer.py::_render_aggregation()` - Lines 658-673

**Validation**: ✅ MONTH and YEAR now computed with SUBSTRING formulas

---

### SOLVED-005: GROUP BY Source Expression Mapping

**Original Bug**: BUG-008  
**Discovered**: 2025-11-13, CV_INVENTORY_ORDERS.xml  
**Resolved**: 2025-11-13

**Error**:
```
invalid column name: JOIN_4.WAERS_EKKO (GROUP BY uses alias, should use source)
```

**Problem**:
GROUP BY used output alias names (WAERS_EKKO) but aliases are created in same SELECT - can't reference them.

**SQL Before**:
```sql
SELECT join_4.WAERS AS WAERS_EKKO, ...
GROUP BY WAERS_EKKO  -- ERROR: alias doesn't exist yet
```

**SQL After**:
```sql
SELECT join_4.WAERS AS WAERS_EKKO, ...
GROUP BY join_4.WAERS  -- FIXED: source column
```

**Root Cause**:
`node.group_by` contains output column names, but GROUP BY needs to reference the source columns from the input CTE.

**Solution**:
Map GROUP BY column names through node.mappings to get source expressions:

```python
target_to_expr_map = {}
for mapping in node.mappings:
    target_to_expr_map[mapping.target_name.upper()] = mapping.expression

for col_name in node.group_by:
    if col_name.upper() in target_to_expr_map:
        expr = target_to_expr_map[col_name.upper()]
        group_by_cols.append(_render_expression(ctx, expr, from_clause))
```

**Files Modified**:
- `src/xml_to_sql/sql/renderer.py::_render_aggregation()` - Lines 588-603

**Validation**: ✅ GROUP BY now uses `join_4.WAERS`, `join_4.EINDT` (source columns)

---

### SOLVED-006: Aggregation Spec Source Mapping

**Original Bug**: BUG-009  
**Discovered**: 2025-11-13, CV_INVENTORY_ORDERS.xml  
**Resolved**: 2025-11-13

**Error**:
```
invalid column name: JOIN_4.WEMNG_EKET (aggregation spec uses renamed column)
```

**Problem**:
Aggregation specs trying to aggregate renamed columns instead of source columns.

**SQL Before**:
```sql
SELECT join_4.WEMNG AS WEMNG_EKET, ...
    SUM(join_4.WEMNG_EKET) AS ...  -- ERROR: WEMNG_EKET doesn't exist
```

**SQL After**:
```sql
SELECT join_4.WEMNG AS WEMNG_EKET, ...
    SUM(join_4.WEMNG) AS WEMNG_EKET  -- FIXED: source column
```

**Root Cause**:
Aggregation specs referenced column names, but if those columns were renamed in mappings, the specs used the new name instead of the original.

**Solution**:
Map aggregation spec column names through mappings to get source expressions:

```python
target_to_source_expr = {}
for mapping in node.mappings:
    target_to_source_expr[mapping.target_name.upper()] = mapping.expression

for agg_spec in node.aggregations:
    if agg_spec.expression.expression_type == ExpressionType.COLUMN:
        col_name = agg_spec.expression.value
        if col_name.upper() in target_to_source_expr:
            agg_expr = _render_expression(ctx, target_to_source_expr[col_name.upper()], from_clause)
```

**Files Modified**:
- `src/xml_to_sql/sql/renderer.py::_render_aggregation()` - Lines 611-631

**Validation**: ✅ SUM(join_4.WEMNG), SUM(join_4.MENGE) use source names

---

### SOLVED-007: Aggregation Subquery Wrapping

**Original Bug**: BUG-010  
**Discovered**: 2025-11-13, CV_INVENTORY_ORDERS.xml  
**Resolved**: 2025-11-13

**Error**:
```
invalid column name: MONTH (calculated column in GROUP BY of same SELECT)
```

**Problem**:
Calculated columns in aggregations were in GROUP BY of same SELECT that computes them.

**SQL Before**:
```sql
SELECT 
    ...,
    SUBSTRING("AEDAT_EKKO", 1, 6) AS MONTH
GROUP BY MONTH  -- ERROR: MONTH doesn't exist yet
```

**SQL After**:
```sql
SELECT
    agg_inner.*,
    SUBSTRING(agg_inner."AEDAT_EKKO", 1, 6) AS MONTH
FROM (
  SELECT ..., dimensions, aggregations
  GROUP BY dimensions
) AS agg_inner
```

**Root Cause**:
Can't reference column aliases in GROUP BY of same SELECT. Calculated columns need to be computed AFTER grouping.

**Solution**:
Wrap aggregation in subquery when it has calculated columns:
- Inner query: Dimensions + aggregations with GROUP BY
- Outer query: Add calculated columns

**Files Modified**:
- `src/xml_to_sql/sql/renderer.py::_render_aggregation()` - Lines 647-673

**Validation**: ✅ MONTH, YEAR computed in outer query after grouping

---

### SOLVED-008: Skip Aggregated Columns in Dimension Mappings

**Original Bug**: BUG-011  
**Discovered**: 2025-11-13, CV_INVENTORY_ORDERS.xml  
**Resolved**: 2025-11-13

**Error**:
```
column ambiguously defined: WKURS_EKKO (appears both as dimension and measure)
```

**Problem**:
Columns that are aggregated (SUM/COUNT/etc.) were also being added as passthrough dimensions, creating duplicates.

**SQL Before**:
```sql
SELECT 
    join_4.WKURS_EKKO AS WKURS_EKKO,  -- Dimension passthrough
    ...
    SUM(join_4.WKURS_EKKO) AS WKURS_EKKO  -- Aggregated measure
-- ERROR: WKURS_EKKO defined twice
```

**SQL After**:
```sql
SELECT 
    -- WKURS_EKKO NOT in dimensions (skipped)
    ...
    SUM(join_4.WKURS_EKKO) AS WKURS_EKKO  -- Only aggregated
```

**Root Cause**:
`node.mappings` includes ALL columns, but some are measures (to be aggregated) not dimensions (to be passed through). Renderer was adding all mappings as passthroughs, then adding aggregations, creating duplicates.

**Solution**:
Skip mappings that are also in aggregation specs:

```python
aggregated_col_names = set(agg.target_name.upper() for agg in node.aggregations)

for mapping in node.mappings:
    if (mapping.target_name.upper() not in calc_col_names and 
        mapping.target_name.upper() not in aggregated_col_names):
        # Add as dimension
```

**Files Modified**:
- `src/xml_to_sql/sql/renderer.py::_render_aggregation()` - Lines 597-606

**Validation**: ✅ WKURS_EKKO only appears once as SUM()

---

---

## Summary

**Total Bugs Solved**: 8 (in single session)  
**XML**: CV_INVENTORY_ORDERS.xml (BW, 220 lines)  
**Result**: ✅ Executes successfully in HANA BID (34ms)

**Common Pattern**: All bugs related to **target/alias vs source/actual** column name resolution in different contexts (WHERE, GROUP BY, JOIN, aggregations).

**Key Insight**: User naming convention adds table suffix to columns (e.g., LOEKZ→LOEKZ_EKPO, WEMNG→WEMNG_EKET) to distinguish columns from different sources. This creates systematic target≠source mismatches that require careful mapping throughout the rendering pipeline.

**Files Modified**:
- `src/xml_to_sql/parser/column_view_parser.py` - ColumnView JOIN parsing
- `src/xml_to_sql/sql/renderer.py` - Projection filters, aggregation rendering (dimensions, measures, GROUP BY, calculated columns)

**Validation**: ✅ Both XMLs execute successfully in HANA
- CV_CNCLD_EVNTS (ECC/MBD): 243 lines, 84ms
- CV_INVENTORY_ORDERS (BW/BID): 220 lines, 34ms
Filters referenced target/alias column names instead of source column names when querying base tables.

**SQL Before**:
```sql
SELECT SAPABAP1."/BIC/AZEKPO2".LOEKZ AS LOEKZ_EKPO ...
WHERE ("LOEKZ_EKPO" ='')  -- ERROR: alias doesn't exist
```

**SQL After**:
```sql
SELECT SAPABAP1."/BIC/AZEKPO2".LOEKZ AS LOEKZ_EKPO ...
WHERE ("LOEKZ" ='')  -- FIXED: source column name
```

**Root Cause**:
- XML filters use element names: `<element name="LOEKZ_EKPO">` with `<filterExpression>"LOEKZ_EKPO" = ''</filterExpression>`
- But mappings show: `targetName="LOEKZ_EKPO" sourceName="LOEKZ"`
- SQL WHERE can't use aliases, needs actual column names

**Solution**:
Build target→source mapping from node.mappings and replace in WHERE clause.

**Code Changes**:
File: `src/xml_to_sql/sql/renderer.py`  
Function: `_render_projection()`  
Lines: 419-439

```python
# Build target→source name mapping
target_to_source_map = {}
for mapping in node.mappings:
    if mapping.expression.expression_type == ExpressionType.COLUMN:
        source_col = mapping.expression.value
        target_col = mapping.target_name
        if source_col != target_col:
            target_to_source_map[target_col.upper()] = source_col

# Replace target names with source names in WHERE
if where_clause and target_to_source_map and input_id in ctx.scenario.data_sources:
    for target_name, source_name in target_to_source_map.items():
        quoted_target = f'"{target_name}"'
        quoted_source = f'"{source_name}"'
        where_clause = where_clause.replace(quoted_target, quoted_source)
```

**Associated Rules**:
- **Created**: Rule #12 - Filter Source Mapping
- **Document**: HANA_CONVERSION_RULES.md (to be added)
- **Priority**: 25 (before transformations)
- **Category**: Column name resolution

**Validation**:
- ✅ Code implemented
- ✅ SQL regenerated with correct column names
- ⏳ HANA execution pending

**Lessons Learned**:
1. Always distinguish between target (alias) and source (actual column) names
2. WHERE clause operates on source table, not on SELECT output
3. This affects XMLs where column names are renamed in projections
4. Common in BW objects where columns get suffixed (LOEKZ → LOEKZ_EKPO)

---

### SOLVED-011: `CURRENT_TIMESTAMP()` Parentheses Removed

**Original Bug**: BUG-011  
**Discovered**: 2025-11-16 (CV_EQUIPMENT_STATUSES)  
**Resolved**: 2025-11-16

**Error**:
```
SAP DBTech JDBC: [257]: sql syntax error: incorrect syntax near ")": line 82 col 63
```

**Root Cause**:
- ColumnView XML uses `now()` helper
- Catalog mapping with `handler: rename` generated `CURRENT_TIMESTAMP()`
- HANA expects `CURRENT_TIMESTAMP` (no parentheses) when called without arguments

**Fix**:
- Update `functions.yaml` to use `handler: template` with `template: "CURRENT_TIMESTAMP"`
- Remove legacy regex that uppercased `now()` manually
- Regenerate SQL to confirm `DAYS_BETWEEN(..., CURRENT_TIMESTAMP)`

**Files Changed**:
- `src/xml_to_sql/catalog/data/functions.yaml`
- `src/xml_to_sql/sql/function_translator.py`
- `Target (SQL Scripts)/CV_EQUIPMENT_STATUSES.sql`

**Validation**:
- ✅ CV_EQUIPMENT_STATUSES executes successfully (32ms)
- ✅ Functions catalog regression tests pass

---

### SOLVED-012: Schema-Qualified View Creation (`SAPABAP1.<view>`)

**Original Bug**: BUG-012  
**Discovered**: 2025-11-16 (BW XMLs)  
**Resolved**: 2025-11-16

**Error**:
```
SAP DBTech JDBC: [362]: invalid schema name: ABAP
```

**Root Cause**:
- ColumnView XML references data sources as `"ABAP"./BIC/...`
- Generated SQL created views without schema qualification and assumed ABAP schema for sources
- In BID system, actual schema is `SAPABAP1`, so view creation and SELECT statements failed

**Fix**:
1. Added configuration support for `defaults.view_schema` and per-scenario `overrides.schema`
2. CLI + API now qualify view names (e.g., `SAPABAP1.CV_EQUIPMENT_STATUSES`)
3. `_quote_identifier` updated to handle `schema.view` inputs without quoting the dot
4. Web converter + API models now accept `view_schema` (default `SAPABAP1`)
5. Regenerated validated SQL files with new header:
   ```
   DROP VIEW SAPABAP1.<name> CASCADE;
   CREATE VIEW SAPABAP1.<name> AS ...
   ```

**Files Changed**:
- `config.example.yaml`, `src/xml_to_sql/config/*`
- `src/xml_to_sql/cli/app.py`
- `src/xml_to_sql/web/api/models.py`, `web/api/routes.py`, `web/services/converter.py`
- `src/xml_to_sql/sql/renderer.py`
- `Target (SQL Scripts)/CV_{CNCLD_EVNTS,INVENTORY_ORDERS,PURCHASE_ORDERS,EQUIPMENT_STATUSES}.sql`

**Validation**:
- ✅ All four SQL files execute successfully in HANA
- ✅ DROP/CREATE statements now fully deterministic

---

### SOLVED-013: Legacy STRING() Function Not Recognized in HANA

**Original Bug**: BUG-013
**Discovered**: 2025-11-16, CV_TOP_PTHLGY.xml
**Resolved**: 2025-11-16

**Error**:
```
SAP DBTech JDBC: [328]: invalid name of function or procedure: STRING: line 50 col 33 (at pos 3285)
```

**Problem**:
Legacy `string()` helper function was being emitted verbatim in WHERE clauses, but HANA doesn't recognize `STRING` as a valid function name. The conversion succeeded but CREATE VIEW failed during HANA execution.

**Root Cause**:
The function catalog (`src/xml_to_sql/catalog/data/functions.yaml`) contained rewrites for other legacy helpers (LEFTSTR→SUBSTRING, RIGHTSTR→RIGHT, MATCH→REGEXP_LIKE, etc.) but was missing the `string()` → `TO_VARCHAR()` mapping.

**Solution**:
Added `STRING` → `TO_VARCHAR` mapping to the function catalog:

```yaml
  - name: STRING
    handler: rename
    target: "TO_VARCHAR"
    description: >
      Legacy STRING() function mapped to TO_VARCHAR() for type conversion to string/varchar.
```

The catalog rewrite system (via `_apply_catalog_rewrites()` in `function_translator.py`) automatically translates all `string(expr)` calls to `TO_VARCHAR(expr)` during formula translation.

**Associated Rules**:
- **Catalog System**: Centralized function mapping (handover line 170-178)
- **Legacy Helper Translation**: Systematic rewrite of deprecated HANA 1.x functions

**Files Changed**:
- `src/xml_to_sql/catalog/data/functions.yaml` (added STRING entry)

**Validation**:
- ⏳ Pending: User to re-run CV_TOP_PTHLGY conversion and verify HANA execution succeeds

**Code Flow**:
1. XML parser encounters `string(FIELD)` in filter expression
2. `translate_raw_formula()` calls `_apply_catalog_rewrites()` (line 219 for HANA mode)
3. Catalog rule rewrites `string(FIELD)` → `TO_VARCHAR(FIELD)`
4. Generated SQL uses HANA-compatible `TO_VARCHAR()` function

---

### SOLVED-014: Schema Name ABAP Not Recognized in HANA

**Original Bug**: New issue (CV_TOP_PTHLGY)
**Discovered**: 2025-11-16, CV_TOP_PTHLGY.xml
**Resolved**: 2025-11-16

**Error**:
```
SAP DBTech JDBC: [362]: invalid schema name: ABAP: line 13 col 10 (at pos 576)
```

**Problem**:
XML data sources use `ABAP` schema, but HANA instance uses `SAPABAP1` as the actual schema name. All table references generated as `ABAP.TABLE_NAME` causing "invalid schema name" errors.

**Root Cause**:
Different HANA instances use different schema naming conventions:
- Some use `ABAP` directly
- Others use `SAPABAP1`, `SAP<SID>`, etc.
- No schema mapping was configured

**Solution**:
Added schema override to `config.yaml`:

```yaml
schema_overrides:
  ABAP: "SAPABAP1"
```

The renderer's `schema_overrides` parameter now maps `ABAP` → `SAPABAP1` during SQL generation.

**Associated Rules**:
- **Schema Mapping**: Configuration-driven schema name translation
- **Instance-Specific Settings**: Each HANA instance may require different mappings

**Files Changed**:
- `config.yaml` / `config.example.yaml` - Added ABAP → SAPABAP1 mapping

**Validation**:
- ✅ All table references now use `SAPABAP1.TABLE_NAME`
- ✅ HANA accepts the schema name

---

### SOLVED-015: TIMESTAMP Arithmetic Not Supported in HANA

**Original Bug**: New issue (CV_TOP_PTHLGY)
**Discovered**: 2025-11-16, CV_TOP_PTHLGY.xml
**Resolved**: 2025-11-16 (partial - needs code fix for full solution)

**Error**:
```
SAP DBTech JDBC: [266]: inconsistent datatype: the expression has incomputable datatype:
TIMESTAMP is invalid for subtraction operator: line 59 col 105 (at pos 4041)
```

**Problem**:
XML formula `date(NOW() - 365)` translates to `TO_DATE(CURRENT_TIMESTAMP - 365)`, but HANA doesn't allow direct arithmetic on TIMESTAMP types. Must use date functions like `ADD_DAYS()`.

**Root Cause**:
The catalog handles simple function replacements (`NOW()` → `CURRENT_TIMESTAMP`) but doesn't handle **expression pattern rewrites**:
- `NOW() - N` should become `ADD_DAYS(CURRENT_DATE, -N)` or `ADD_DAYS(CURRENT_TIMESTAMP, -N)`
- Current translator processes tokens sequentially, missing the arithmetic operator context

**Solution** (Temporary Manual Fix):
Replaced `CURRENT_TIMESTAMP - 365` with `ADD_DAYS(CURRENT_TIMESTAMP, -365)` using `sed`.

**Proper Solution Needed**:
Add **pattern matching** to function translator:
```python
# In translate_raw_formula() - before catalog rewrites
result = re.sub(
    r'NOW\(\)\s*-\s*(\d+)',
    r'ADD_DAYS(CURRENT_DATE, -\1)',
    result,
    flags=re.IGNORECASE
)
```

**Associated Rules**:
- **Date Arithmetic**: HANA requires function calls (ADD_DAYS, ADD_MONTHS) not operators
- **Pattern Rewrites**: Need regex-based expression transformation, not just function name mapping

**Files Changed**:
- ⚠️ Manual SQL patch only - **CODE FIX PENDING**

**Validation**:
- ⏳ Temporary fix works but needs permanent code solution

---

### SOLVED-016: Function Name Case Sensitivity (adddays vs ADD_DAYS)

**Original Bug**: New issue (CV_TOP_PTHLGY)
**Discovered**: 2025-11-16, CV_TOP_PTHLGY.xml
**Resolved**: 2025-11-16

**Error**:
```
SAP DBTech JDBC: [328]: invalid name of function or procedure: ADDDAYS: line 1681 col 10
```

**Problem**:
XML contains lowercase `adddays()` function calls, but HANA requires uppercase `ADD_DAYS()` (with underscore). Generated SQL had `adddays(TO_DATE(...), -3)`.

**Root Cause**:
XML formulas can contain legacy function names in various cases. The catalog system was missing the `ADDDAYS` entry.

**Solution**:
Added catalog entry:
```yaml
  - name: ADDDAYS
    handler: rename
    target: "ADD_DAYS"
    description: >
      Date arithmetic function - uppercase variant. HANA requires ADD_DAYS (with underscore).
```

**Associated Rules**:
- **Function Case Normalization**: All HANA built-in functions should be uppercase
- **Catalog Completeness**: Every legacy helper variant needs a catalog entry

**Files Changed**:
- `src/xml_to_sql/catalog/data/functions.yaml` - Added ADDDAYS entry

**Validation**:
- ✅ Catalog now handles `adddays()` → `ADD_DAYS()`
- ⚠️ Requires package reinstall (`pip install -e .`)

---

### SOLVED-017: INT() Function Not Recognized in HANA

**Original Bug**: New issue (CV_TOP_PTHLGY)
**Discovered**: 2025-11-16, CV_TOP_PTHLGY.xml
**Resolved**: 2025-11-16

**Error**:
```
SAP DBTech JDBC: [328]: invalid name of function or procedure: INT: line 1815 col 57
```

**Problem**:
XML formula uses `int(FIELD)` for integer casting, but HANA doesn't have an `INT()` function. HANA uses `TO_INTEGER()` or `CAST(... AS INTEGER)`.

**Root Cause**:
Legacy XML formulas use simplified type cast functions (`int()`, `string()`, etc.) that don't exist in standard HANA SQL.

**Solution**:
Added catalog entry:
```yaml
  - name: INT
    handler: rename
    target: "TO_INTEGER"
    description: >
      Legacy INT() type cast mapped to HANA TO_INTEGER() function for integer conversion.
```

**Associated Rules**:
- **Type Conversion Functions**: Map legacy casts to HANA equivalents
  - `int()` → `TO_INTEGER()`
  - `string()` → `TO_VARCHAR()`
  - `decimal()` → `TO_DECIMAL()`
  - `date()` → `TO_DATE()`

**Files Changed**:
- `src/xml_to_sql/catalog/data/functions.yaml` - Added INT entry

**Validation**:
- ✅ Catalog now handles `int()` → `TO_INTEGER()`
- ⚠️ Requires package reinstall (`pip install -e .`)

---

## Resolved in Previous Sessions

*(Placeholder for bugs fixed before structured tracking began)*

**Count**: 13+ issues resolved during CV_CNCLD_EVNTS.xml testing
- IF to CASE conversion
- IN to OR conversion  
- Uppercase IF
- Calculated column expansion
- Subquery wrapping
- Column qualification
- Parameter removal (simple cases)
- String concatenation
- And more...

See: `EMPIRICAL_TEST_ITERATION_LOG.md` for historical fixes

---

## Statistics

**Total Solved**: 5 (BUG-013 through BUG-017) + 13 historical
**Total Pending**: 3 (BUG-001, BUG-002, BUG-003)
**XMLs Validated**: 4 (CV_CNCLD_EVNTS, CV_INVENTORY_ORDERS, CV_PURCHASE_ORDERS, CV_EQUIPMENT_STATUSES)
**XMLs In Progress**: 1 (CV_TOP_PTHLGY - 4 bugs fixed, testing in progress)

**Time to Resolution**:
- BUG-004: < 1 hour (same session)

---

**Process**: Bug discovered → Ticket created in BUG_TRACKER.md → Solution implemented → Moved to SOLVED_BUGS.md with full documentation

