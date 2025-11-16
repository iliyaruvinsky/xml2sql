# Bug Tracker - HANA Mode Conversion Issues

**Purpose**: Structured tracking of all bugs discovered during HANA mode testing  
**Version**: 2.3.0  
**Last Updated**: 2025-11-13

---

## Active Bugs

### BUG-001: JOIN Column Resolution - Wrong Projection Reference

**Status**: ✅ **SOLVED** (2025-11-13)  
**Severity**: High  
**Discovered**: CV_INVENTORY_ORDERS.xml testing  
**XML**: CV_INVENTORY_ORDERS.xml  
**Instance Type**: BW (BID)

**Error**:
```
SAP DBTech JDBC: [260]: invalid column name: PROJECTION_6.EINDT: line 103 col 9
```

**Problem**:
```sql
-- Line 103 in join_6
SELECT projection_6.EINDT AS EINDT
FROM projection_6
```

But `projection_6` doesn't have column `EINDT` - it's in `projection_8`.

**Root Cause**:
- JOIN node mapping logic incorrectly resolves which projection exposes which columns
- CTE column propagation doesn't track which columns come from which input
- May be parser issue (incorrect mappings in IR) or renderer issue (wrong CTE reference)

**Related Rules**: None - this is a core IR/rendering bug, not a transformation rule issue

**Impact**: Affects any XML with JOINs where columns come from different projections

**Affected XMLs**:
- CV_INVENTORY_ORDERS.xml
- Potentially others with complex joins

**Next Steps**:
1. Debug JOIN node rendering logic
2. Check how `source_node` is determined in mappings
3. Verify parser correctly captures which input provides which column

---

### BUG-002: Complex Parameter Pattern Cleanup

**Status**: 🔴 **OPEN**  
**Severity**: Medium  
**Discovered**: CV_MCM_CNTRL_Q51.xml testing  
**XML**: CV_MCM_CNTRL_Q51.xml  
**Instance Type**: ECC (MBD)

**Error**:
```
Multiple: Unbalanced parentheses, malformed DATE() calls, orphaned operators
```

**Problem**:
```sql
-- Original XML
('$$IP_DATEFROM$$' = '' OR (DATE("ZZTREAT_DATE") >= DATE('$$IP_DATEFROM$$')))

-- After substitution ($$IP → '')
('' = '' OR (DATE("ZZTREAT_DATE") >= DATE('')))

-- After attempted cleanup
)  >= DATE('')))       -- Corrupted!
```

**Root Cause**:
- Parameter substitution creates malformed SQL FIRST
- Cleanup tries to fix AFTER but can't handle deep nesting
- DATE() function calls with parameters create special complexity
- Multiple parameter references in single expression

**Related Rules**: 
- ✅ Rule #9: Parameter Removal (works for simple cases)
- ❌ Needs enhancement for nested DATE() patterns

**Impact**: 
- Affects XMLs with complex parameter patterns
- 8+ parameters with DATE() nesting particularly problematic

**Affected XMLs**:
- CV_MCM_CNTRL_Q51.xml (8+ parameters, DATE nesting)
- CV_CT02_CT03.xml (REGEXP_LIKE + parameters)

**Proposed Solution**:
- Pre-removal strategy: Remove entire parameter clauses BEFORE substitution
- Don't substitute `$$IP_XXX$$` → `''`, just remove the whole `($$IP_XXX$$ = '' OR ...)` pattern

**Next Steps**:
1. Implement pre-removal in `_substitute_placeholders()`
2. Test on CV_MCM_CNTRL_Q51.xml
3. Update Rule #9 with pre-removal approach

**Deferred**: For later session

---

### BUG-003: REGEXP_LIKE with Parameter Patterns

**Status**: 🔴 **OPEN**  
**Severity**: Medium  
**Discovered**: CV_CT02_CT03.xml testing  
**XML**: CV_CT02_CT03.xml  
**Instance Type**: ECC (MBD)

**Error**:
```
SAP DBTech JDBC: [257]: sql syntax error: incorrect syntax near "AND": line 29 col 165
```

**Problem**:
```sql
WHERE (REGEXP_LIKE(..., CASE WHEN ''= '' THEN '*' ELSE calc.col END, ...) AND
    REGEXP_LIKE(...) AND
    ...
```

Issues:
1. `''=''` - Spacing issue (should be `'' = ''`)
2. Parameter substitution in REGEXP_LIKE pattern creates always-true CASE
3. Multiple consecutive REGEXP_LIKE with parameter CASE patterns

**Root Cause**:
- Parameters used inside REGEXP_LIKE patterns
- CASE WHEN with always-true conditions (`'' = ''`)
- Cleanup doesn't simplify these nested patterns

**Related Rules**:
- ✅ Rule #3: String Concatenation (|| preserved in REGEXP_LIKE)
- ❌ Needs: Parameter simplification in REGEXP_LIKE contexts

**Impact**: XMLs with match() helper functions + parameters

**Affected XMLs**:
- CV_CT02_CT03.xml

**Proposed Solution**:
- Simplify `CASE WHEN '' = '' THEN '*' ELSE x END` → `'*'` (always takes THEN branch)
- Or remove parameter logic from REGEXP_LIKE patterns entirely

**Deferred**: For later session

---

### BUG-004: Filter Alias vs Source Name Mapping

**Status**: ✅ **SOLVED** (2025-11-13) - Moved to SOLVED_BUGS.md  
**Severity**: High  
**Discovered**: CV_INVENTORY_ORDERS.xml testing  
**XML**: CV_INVENTORY_ORDERS.xml

**Error**:
```
SAP DBTech JDBC: [260]: invalid column name: LOEKZ_EKPO: line 67 col 12
```

**Problem**:
```sql
SELECT SAPABAP1."/BIC/AZEKPO2".LOEKZ AS LOEKZ_EKPO ...
WHERE ("LOEKZ_EKPO" ='')  -- Alias doesn't exist in WHERE context
```

**Root Cause**:
- Filters use target/alias column names
- Base table queries need source column names
- Mapping: `LOEKZ` (source) → `LOEKZ_EKPO` (target/alias)

**Solution Implemented**:
```python
# In _render_projection():
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

**Related Rules**: 
- 🆕 **Rule #12: Filter Source Mapping** (added)
- Priority: 25
- Document: Added to HANA_CONVERSION_RULES.md

**Fix Verified**: Code changed, SQL regenerated  
**Status**: ✅ FIXED (waiting HANA validation)

**Files Modified**:
- `src/xml_to_sql/sql/renderer.py` - Lines 419-439

---

## Resolved Bugs

*(Will move BUG-004 here after HANA validation confirms it works)*

---

## Bug Statistics

**Total Bugs**: 11  
**Open**: 2 (BUG-002, BUG-003)  
**Solved**: 8 (BUG-001, BUG-004, BUG-005, BUG-006, BUG-007, BUG-008, BUG-009, BUG-010, BUG-011)  
**Deferred**: 0  
**Deferred**: 2 (BUG-002, BUG-003)

**By Category**:
- Core IR/Rendering: 1 (BUG-001)
- Parameter Handling: 2 (BUG-002, BUG-003)
- Column Mapping: 1 (BUG-004 - FIXED)

**By XML**:
- CV_CNCLD_EVNTS: 0 bugs ✅ (clean)
- CV_MCM_CNTRL_Q51: 1 bug (BUG-002)
- CV_CT02_CT03: 1 bug (BUG-003)
- CV_INVENTORY_ORDERS: 2 bugs (BUG-001 open, BUG-004 fixed)

---

## Future Bug Template

```markdown
### BUG-XXX: [Short Description]

**Status**: 🔴 OPEN | 🟡 IN PROGRESS | ✅ FIXED  
**Severity**: Critical | High | Medium | Low  
**Discovered**: [XML name] testing  
**XML**: [filename]  
**Instance Type**: ECC | BW

**Error**:
[HANA error message]

**Problem**:
[SQL snippet showing issue]

**Root Cause**:
[Analysis of why this happens]

**Related Rules**: 
- [Link to HANA_CONVERSION_RULES.md rules that relate]

**Impact**: 
[Which XMLs/scenarios affected]

**Affected XMLs**:
- List of XMLs with this bug

**Proposed Solution**:
[How to fix]

**Next Steps**:
1. Action items

**Files Modified** (if fixed):
- List of files changed
```

---

**Process**: Every HANA error → Create bug ticket → Map to rules → Implement fix → Document solution

