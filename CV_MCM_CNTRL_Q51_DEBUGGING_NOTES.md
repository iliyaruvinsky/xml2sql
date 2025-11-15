# CV_MCM_CNTRL_Q51.xml Debugging Notes

**Status**: DEFERRED - Complex parameter patterns require additional work  
**Date**: 2025-11-13  
**Priority**: Medium - Test simpler XMLs first

---

## XML Characteristics

**File**: `Source (XML Files)/OLD_HANA_VIEWS/CV_MCM_CNTRL_Q51.xml`  
**Format**: View:ColumnView (HANA 1.0)  
**Complexity**: High

**Statistics**:
- Nodes: 12
- Filters: 5
- Calculated columns: 4
- Input parameters: 10 (IP_DATEFROM, IP_DATETO, IP_CALMONTH, IP_CALQUARTER, IP_CALYEAR, IP_ZTREAT_COMM_CD, IP_PERID, IP_ZZMEMBERCD, IP_ZZPOSITION, others)

---

## Problematic Patterns

### 1. Complex DATE() Parameter Patterns

**XML Source**:
```xml
('$$IP_DATEFROM$$' = '' OR (DATE("ZZTREAT_DATE") >= DATE('$$IP_DATEFROM$$') ))  AND
('$$IP_DATETO$$' = '' OR (DATE("ZZTREAT_DATE") <=  DATE('$$IP_DATETO$$')))
```

**After Parameter Substitution** ($$IP_XXX$$ → ''):
```sql
('' = '' OR (DATE("ZZTREAT_DATE") >= DATE('') ))  AND
('' = '' OR (DATE("ZZTREAT_DATE") <=  DATE('')))
```

**After Cleanup Attempt**:
```sql
)   <=  DATE('')))       AND
```

**Problems**:
- Malformed DATE('') calls remain
- Extra closing parens orphaned
- Comparison operators (>=, <=) left dangling
- Nested parentheses not properly tracked

### 2. IN() with Parameters

**XML Source**:
```xml
(IN($$IP_ZTREAT_COMM_CD$$,0) OR IN("ZZTREAT_COMM_CD",$$IP_ZTREAT_COMM_CD$$))
```

**After Substitution**:
```sql
(('' = 0) OR (calc."ZZTREAT_COMM_CD" = ''))
```

**Problems**:
- Nested double parens
- Type mismatch: `'' = 0` (string vs number)
- Not fully removed by cleanup

### 3. Multiple Parameters in Single Filter

**Count**: CV_MCM_CNTRL_Q51 has 8+ parameter references in WHERE clauses  
**Complexity**: Nested, interleaved with DATE() calls, comparison operators

---

## Cleanup Mechanisms Built

All mechanisms in `src/xml_to_sql/sql/renderer.py::_cleanup_hana_parameter_conditions()`:

### Implemented Cleanups:
1. **Balanced paren removal**: `('' = '' OR column = '')` → removed
2. **AND cleanup**: Remove AND before/after removed clauses
3. **Orphaned paren**: `'Z112T'and\n    )` → `'Z112T')`
4. **Missing AND**: `)(` → `) AND (`
5. **DATE() fragments**: `) >= DATE('')))` → `)`
6. **Nested empty**: `(('' = ...))` → removed
7. **Double AND**: `AND AND` → `AND`

### What Works:
- ✅ Simple parameter patterns: `('' = '' OR col = '')`
- ✅ Single-level nesting
- ✅ Most orphaned AND patterns

### What Needs Work:
- ❌ Multi-level nested parens with DATE()
- ❌ Comparison operators orphaned: ` <= DATE('')`
- ❌ Type mismatches: `('' = 0)`
- ❌ Complex interleaved patterns

---

## Current SQL State

**Generated**: 295 lines  
**Parentheses**: 77 opening, 72 closing (5 missing) - overcorrection

**Known Errors** (latest run):
- Line 17: Orphaned `)` (projection_3)
- Line 83: Syntax near AND
- Line 86: Syntax near AND
- Line 116: Syntax near `<=` (malformed DATE fragment)

---

## Recommended Fix Strategy

### Phase 1: Identify All Parameter Patterns
1. Scan XML for ALL parameter usages
2. Categorize by complexity:
   - Simple: `('$$IP_XXX$$' = '' OR col = '$$IP_XXX$$')`
   - DATE: `('$$IP_XXX$$' = '' OR DATE(col) >= DATE('$$IP_XXX$$'))`
   - IN: `(IN($$IP_XXX$$,0) OR ...)`
   - Nested combinations

### Phase 2: Pre-process Before Substitution
**Current approach**: Substitute `$$IP_XXX$$` → `''`, then cleanup  
**Better approach**: 
1. **Detect** parameter patterns in raw formula
2. **Remove entire clause** BEFORE substitution
3. **Then** apply standard transformations

**Implementation**:
```python
def _remove_parameter_clauses_hana(formula: str) -> str:
    """Remove entire parameter filter clauses BEFORE substitution."""
    # Pattern: ('$$IP_XXX$$' = 'default' OR expression)
    # Remove the WHOLE pattern, not just substitute
    patterns = [
        r"\('?\$\$IP_[A-Z_]+\$\$'?\s*=\s*'[^']*'\s+OR\s+\([^)]+\)\s*\)",
        r"\('?\$\$IP_[A-Z_]+\$\$'?\s*=\s*'[^']*'\s+OR\s+[^)]+\)",
    ]
    for pattern in patterns:
        formula = re.sub(pattern, '', formula, flags=re.IGNORECASE)
    return formula
```

### Phase 3: Test with Simpler XMLs First
- CV_CT02_CT03.xml
- CV_INVENTORY_ORDERS.xml  
- CV_PURCHASE_ORDERS.xml

Build confidence that cleanup works for typical cases, then return to CV_MCM_CNTRL_Q51.

---

## Files Modified for CV_MCM_CNTRL_Q51

**Cleanup enhancements** (all permanent, benefit all XMLs):
- `src/xml_to_sql/sql/renderer.py::_cleanup_hana_parameter_conditions()` - Enhanced with 8 cleanup rules
- `src/xml_to_sql/sql/function_translator.py::_substitute_placeholders()` - Simplified parameter substitution
- `src/xml_to_sql/cli/app.py` - Disabled validation temporarily for debugging

---

## Next Steps

1. **Mark CV_MCM_CNTRL_Q51 as deferred** ✅
2. **Update config.yaml** to disable CV_MCM_CNTRL_Q51, enable simpler XMLs
3. **Test**: CV_CT02_CT03.xml (likely simpler parameter patterns)
4. **Validate**: Cleanup mechanisms work on typical cases
5. **Return**: Fix CV_MCM_CNTRL_Q51 with refined approach

---

## Lessons Learned

1. **Parameter complexity varies widely** between XMLs
2. **DATE() nesting** creates special challenges
3. **Pre-removal** strategy likely better than post-substitution cleanup
4. **Test simpler first** to validate core mechanisms
5. **Incremental refinement** works - each fix helps future XMLs

---

**Status**: Documented and deferred. Ready to test simpler XMLs.

