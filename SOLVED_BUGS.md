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

**Total Solved**: 1 (+ 13 historical)  
**Total Pending**: 3  
**Success Rate**: 25% (1 of 4 current bugs solved)

**Time to Resolution**:
- BUG-004: < 1 hour (same session)

---

**Process**: Bug discovered → Ticket created in BUG_TRACKER.md → Solution implemented → Moved to SOLVED_BUGS.md with full documentation

