# ⚠️ ARCHIVED: PRE-FIX ANALYSIS - BUG-020 NOW SOLVED

**Archive Date**: 2025-11-18
**Original Status**: ACTIVE (Pre-fix analysis)
**Current Status**: ✅ **SOLVED** - See [BUG-020-FIX-SUMMARY.md](../BUG-020-FIX-SUMMARY.md) for complete solution
**Archived Reason**: This document contains the original problem analysis. The bug has been fixed with a three-part solution.

**Fix Summary**:
- **Part 1**: Convert function-style `IN(column, val1, val2)` to operator-style `column IN (val1, val2)`
- **Part 2**: HANA version-aware IN→OR conversion (only for HANA 1.x)
- **Part 3**: Enhanced parameter cleanup for escaped quotes `''''`
- **Result**: CV_CNCLD_EVNTS.xml now passes validation in 66ms (100% success rate)

**For Current Documentation**: See [docs/bugs/SOLVED_BUGS.md](../bugs/SOLVED_BUGS.md) - SOLVED-020 entry (lines 816-936)

---

# BUG-020: IN() Function Corruption During Calculated Column Expansion

**Discovered**: 2025-11-18
**File**: CV_CNCLD_EVNTS.xml
**Status**: ❌ ACTIVE - Blocking ECC instance testing
**Severity**: CRITICAL - Breaks SQL generation for complex calculated columns

## Problem Summary

When a calculated column formula contains nested `IF()` and `IN()` functions that reference another calculated column, the `IN()` function's comma-separated arguments are corrupted during calculated column expansion, producing invalid SQL.

## Test Case

**XML**: `Source (XML Files)/HANA 1.XX XML Views/ECC_ON_HANA/CV_CNCLD_EVNTS.xml`
**Package**: `EYAL.EYAL_CTL`
**HANA Error**: `SQL syntax error: incorrect syntax near "IF": line 36 col 11 (at pos 1868)`

## Original XML Formula

```xml
<!-- CALMONTH calculated column -->
<formula>LEFTSTR("ZZTREAT_DATE",6)</formula>

<!-- CALQUARTER calculated column - references CALMONTH -->
<formula>if( in( rightstr("CALMONTH",2),'01','02','03'), leftstr("ZZTREAT_DATE",4)+'1',
 if( in(rightstr("CALMONTH",2),'04','05','06'), leftstr("ZZTREAT_DATE",4)+'2',
  if( in(rightstr("CALMONTH",2),'07','08','09'), leftstr("ZZTREAT_DATE",4)+'3',
   if(in(rightstr("CALMONTH",2),'10','11','12'), leftstr("ZZTREAT_DATE",4)+'4',''))))
</formula>
```

## Expected SQL Output

```sql
SUBSTRING(SAPABAP1.ZBW_CTL_HD_RE.ZZTREAT_DATE, 1, 6) AS CALMONTH,
IF(IN(RIGHT(SUBSTRING(SAPABAP1.ZBW_CTL_HD_RE.ZZTREAT_DATE, 1, 6), 2), '01', '02', '03'),
   SUBSTRING(SAPABAP1.ZBW_CTL_HD_RE.ZZTREAT_DATE, 1, 4)+'1',
IF(IN(RIGHT(SUBSTRING(SAPABAP1.ZBW_CTL_HD_RE.ZZTREAT_DATE, 1, 6), 2), '04', '05', '06'),
   SUBSTRING(SAPABAP1.ZBW_CTL_HD_RE.ZZTREAT_DATE, 1, 4)+'2',
IF(IN(RIGHT(SUBSTRING(SAPABAP1.ZBW_CTL_HD_RE.ZZTREAT_DATE, 1, 6), 2), '07', '08', '09'),
   SUBSTRING(SAPABAP1.ZBW_CTL_HD_RE.ZZTREAT_DATE, 1, 4)+'3',
IF(IN(RIGHT(SUBSTRING(SAPABAP1.ZBW_CTL_HD_RE.ZZTREAT_DATE, 1, 6), 2), '10', '11', '12'),
   SUBSTRING(SAPABAP1.ZBW_CTL_HD_RE.ZZTREAT_DATE, 1, 4)+'4',
'')))) AS CALQUARTER
```

## Actual SQL Output (BROKEN)

```sql
SUBSTRING(SAPABAP1.ZBW_CTL_HD_RE.ZZTREAT_DATE, 1, 6) AS CALMONTH,
IF( = RIGHT((SUBSTRING(SAPABAP1.ZBW_CTL_HD_RE.ZZTREAT_DATE OR  = 1 OR  = 6)) OR  = 2) OR  = '01' OR  = '02' OR  = '03'),
   SUBSTRING(SAPABAP1.ZBW_CTL_HD_RE.ZZTREAT_DATE, 1, 4)+'1',
IF( = RIGHT((SUBSTRING(SAPABAP1.ZBW_CTL_HD_RE.ZZTREAT_DATE OR  = 1 OR  = 6)) OR  = 2) OR  = '04' OR  = '05' OR  = '06'),
   SUBSTRING(SAPABAP1.ZBW_CTL_HD_RE.ZZTREAT_DATE, 1, 4)+'2',
IF( = RIGHT((SUBSTRING(SAPABAP1.ZBW_CTL_HD_RE.ZZTREAT_DATE OR  = 1 OR  = 6)) OR  = 2) OR  = '07' OR  = '08' OR  = '09'),
   SUBSTRING(SAPABAP1.ZBW_CTL_HD_RE.ZZTREAT_DATE, 1, 4)+'3',
IF(in(RIGHT((SUBSTRING(SAPABAP1.ZBW_CTL_HD_RE.ZZTREAT_DATE, 1, 6)), 2),'10','11','12'),
   SUBSTRING(SAPABAP1.ZBW_CTL_HD_RE.ZZTREAT_DATE, 1, 4)+'4',
'')))) AS CALQUARTER
```

## Symptoms

1. **Empty comparisons**: `IF( = RIGHT(...` instead of `IF(IN(RIGHT(...`
2. **Scattered OR conditions**: `OR  = 1 OR  = 6` from misinterpreted function arguments
3. **Lost IN() function structure**: The `IN()` wrapper is removed and arguments become OR conditions
4. **Partial corruption**: Last nested `IF(in(...))` works correctly, only first 3 levels corrupted

## Root Cause

**Location**: Likely in `src/xml_to_sql/sql/function_translator.py` or `renderer.py`

When expanding calculated columns (CALMONTH) inside complex formulas:
1. Parser encounters `in(rightstr("CALMONTH",2),'01','02','03')`
2. Attempts to inline-expand `"CALMONTH"` → `SUBSTRING(ZZTREAT_DATE, 1, 6)`
3. **The comma-separated arguments of `IN()` are misinterpreted during replacement**
4. Result: `in(rightstr(SUBSTRING(...),2),'01','02','03')` becomes broken fragments

The catalog's `IN` function handler or the calculated column expansion logic doesn't properly preserve function argument boundaries when replacing column references.

## Impact

- ❌ **CV_CNCLD_EVNTS.xml fails** (ECC instance)
- **Blocks 1/5 validated XMLs** (20% failure rate)
- **Pattern**: Any XML with calculated columns containing `IN()` + nested calculated column references

## Workaround

**Option 1**: Modify XML to avoid calculated column references inside `IN()`
**Option 2**: Use subquery approach instead of inline expansion for this specific pattern

## Recommended Fix

1. **Enhance calculated column expansion** in `renderer.py::_expand_calculated_column_refs()`
2. **Parse function boundaries** before performing string replacement
3. **Use AST-based replacement** instead of regex for complex formulas
4. **Preserve `IN()` function structure** during expansion

## Related Bugs

- BUG-007: Aggregation calculated columns (SOLVED - similar expansion issue)
- BUG-019: CV_CT02_CT03 REGEXP_LIKE with calculated columns (ACTIVE - similar pattern)

## Test Status

**Regression Impact**: 4/5 XMLs passing (80% success rate)

| File | Status | Notes |
|------|--------|-------|
| CV_CNCLD_EVNTS.xml | ❌ FAIL | BUG-020 blocks |
| CV_INVENTORY_ORDERS.xml | ✅ PASS | 42ms |
| CV_PURCHASE_ORDERS.xml | ✅ PASS | 46ms |
| CV_EQUIPMENT_STATUSES.xml | ✅ PASS | 29ms |
| CV_TOP_PTHLGY.xml | ✅ PASS | 211ms |

---

**Next Steps**:
1. Investigate calculated column expansion logic
2. Implement AST-based or boundary-aware replacement
3. Add regression test for `IN()` + calculated column pattern
4. Re-test CV_CNCLD_EVNTS.xml after fix
