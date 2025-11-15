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

### SOLVED-001: Filter Alias vs Source Name Mapping

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

