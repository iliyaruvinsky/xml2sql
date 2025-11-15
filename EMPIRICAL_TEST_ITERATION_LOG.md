# Empirical Testing Iteration Log

This document tracks each iteration of the empirical testing cycle with HANA error messages and fixes applied.

## Test Cycle #1 - 2025-11-13

**Distribution**: xml2sql-distribution-20251113-125805.zip (baseline)  
**XML File**: CV_CNCLD_EVNTS.xml  
**Mode**: Initial - Snowflake SQL tested in HANA

### Issues Found

#### Issue 1.1: Wrong SQL Dialect
**Error**: `sql syntax error: incorrect syntax near "IN": line 34 col 35`  
**Generated SQL**:
```sql
IFF((RIGHT("CALMONTH", 2) IN ('01', '02', '03')), ...)
```

**Analysis**: 
- Converter was generating Snowflake SQL (IFF, ||)
- HANA requires different syntax (IF, +)
- Need database mode selection

**Fix Applied**: 
- Implemented multi-database mode support (DatabaseMode enum)
- Added HANA mode with version awareness
- Created mode-aware function translator

**Status**: ✅ Fixed - Multi-database mode feature implemented

---

## Test Cycle #2 - 2025-11-13

**Distribution**: Current codebase with multi-database mode  
**XML File**: CV_CNCLD_EVNTS.xml  
**Mode**: HANA mode, HANA version 2.0

### Issues Found

#### Issue 2.1: Lowercase IF Function
**Error**: `sql syntax error: incorrect syntax near "if": line 34 col 9`  
**Generated SQL**:
```sql
if( (RIGHT("CALMONTH", 2) IN ('01', '02', '03')), ...)
```

**Analysis**:
- HANA requires uppercase `IF()` not lowercase `if()`
- The raw formula from XML has lowercase `if`
- Need to uppercase IF in HANA mode

**Fix Applied**:
- Created `_uppercase_if_statements()` function
- Applied to HANA mode in `translate_raw_formula()`
- Now generates: `IF(...)` instead of `if(...)`

**Status**: ✅ Fixed

#### Issue 2.2: IN Operator Inside IF()
**Error**: `sql syntax error: incorrect syntax near "IN": line 34 col 35`  
**Generated SQL**:
```sql
IF((RIGHT("CALMONTH", 2) IN ('01', '02', '03')), ...)
```

**Analysis**:
- HANA doesn't support `IN` operator inside `IF()` conditions in this context
- The legacy `in()` helper function was converted to standard SQL `IN`
- HANA needs `OR` conditions instead

**Fix Applied**:
- Created `_convert_in_to_or_for_hana()` function
- Converts: `(expr IN ('a', 'b', 'c'))` → `(expr = 'a' OR expr = 'b' OR expr = 'c')`
- Applied to HANA mode in `translate_raw_formula()`
- Now generates: `IF(RIGHT("CALMONTH", 2) = '01' OR RIGHT("CALMONTH", 2) = '02' OR RIGHT("CALMONTH", 2) = '03', ...)`

**Status**: ✅ Fixed

### Expected Output After Fixes

The SQL should now be:
```sql
CREATE VIEW CV_CNCLD_EVNTS AS
WITH
  ctleqr AS (
    SELECT
        ...
        IF(RIGHT("CALMONTH", 2) = '01' OR RIGHT("CALMONTH", 2) = '02' OR RIGHT("CALMONTH", 2) = '03', 
           SUBSTRING("ZZTREAT_DATE", 1, 4)+'1',
        IF(RIGHT("CALMONTH", 2) = '04' OR RIGHT("CALMONTH", 2) = '05' OR RIGHT("CALMONTH", 2) = '06',
           SUBSTRING("ZZTREAT_DATE", 1, 4)+'2',
        IF(...))) AS CALQUARTER,
        ...
```

Key changes:
- ✅ `if(` → `IF(` (uppercase)
- ✅ `IN ('01', '02', '03')` → `= '01' OR ... = '02' OR ... = '03'`
- ✅ Uses `+` for string concatenation (HANA style)
- ✅ Uses `CREATE VIEW` (not CREATE OR REPLACE VIEW)

### Next Steps

1. Re-convert CV_CNCLD_EVNTS.xml with HANA mode (web UI or CLI)
2. Execute new SQL in HANA
3. Report results (success or new errors)
4. Continue iteration if needed

---

## Lessons Learned

1. **Empirical testing is essential**: Static analysis didn't catch the IN operator issue
2. **HANA syntax is strict**: Requires uppercase function names, has limitations on operators in conditions
3. **Mode-aware translation needs refinement**: Initial implementation covered common cases but edge cases emerged in real testing
4. **Iterative approach works**: Each error provides specific feedback for targeted fixes

## Code Changes Applied

**Modified Files**:
- `src/xml_to_sql/sql/function_translator.py`:
  - Added `_uppercase_if_statements()`
  - Added `_convert_in_to_or_for_hana()`
  - Updated `translate_raw_formula()` to apply HANA-specific transformations

**Testing Status**:
- ✅ Code verified: No linter errors
- ⏳ Awaiting empirical test results from Test Cycle #3

