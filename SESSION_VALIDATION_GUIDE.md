# Session Validation Guide - BUG-023, BUG-025, and Node ID Fixes

## Summary of Fixes Applied

This session fixed THREE critical bugs that were causing SQL generation errors:

### 1. **BUG-023: Package Path in CREATE VIEW** ✅ VALIDATED
**Problem:** CREATE VIEW statements incorrectly included package paths
**Fix:** Modified [converter.py:312-319](src/xml_to_sql/web/services/converter.py#L312-L319) to exclude package path from view name
**Status:** Already validated in existing output - working correctly

### 2. **BUG-025: CV Reference Format** ✅ FIXES APPLIED
**Problem:** CV references rendered as regular tables instead of `_SYS_BIC` format
**Fix Applied in 4 Files:**
- [column_view_parser.py:488-516](src/xml_to_sql/parser/column_view_parser.py#L488-L516) - Parse `::` separator
- [scenario_parser.py:189-192](src/xml_to_sql/parser/scenario_parser.py#L189-L192) - Detect CV type
- [renderer.py:901-921](src/xml_to_sql/sql/renderer.py#L901-L921) - Render with `_SYS_BIC` format
- [converter.py:243-247](src/xml_to_sql/web/services/converter.py#L243-L247) - Handle bytes/string input

### 3. **NEW BUG: Invalid SQL Identifiers (Node ID Cleaning)** ✅ FIXED + TESTED
**Problem:** Node references like `#/0/Star Join/Join_1` were becoming `0/Star Join/Join_1`, creating invalid SQL like `FROM 0/prj_visits`
**Fix:** Rewrote [scenario_parser.py:793-817](src/xml_to_sql/parser/scenario_parser.py#L793-L817) `_clean_ref()` function
**Test Results:** ✅ ALL 8 TEST CASES PASSED (see [test_clean_ref.py](test_clean_ref.py))

---

## What to Test in Web UI

### **Test File:** CV_ELIG_TRANS_01.xml

Upload this file in the web UI and check the generated SQL for the following:

### **Validation Checkpoint 1: CREATE VIEW (Line ~5)**
**Expected:**
```sql
CREATE VIEW "_SYS_BIC".CV_ELIG_TRANS_01 AS
```
**What to Look For:**
- ✅ View name should be just `CV_ELIG_TRANS_01` (NO package path)
- ✅ Should NOT see: `"_SYS_BIC"."Macabi_BI.Eligibility/CV_ELIG_TRANS_01"`

---

### **Validation Checkpoint 2: Node IDs (Lines ~7-40)**
**Expected:**
```sql
WITH
  join_1 AS (
    SELECT
        prj_visits."_BIC_EYEVNTID" AS "_BIC_EYEVNTID",
        ...
    FROM prj_visits AS prj_visits
    LEFT OUTER JOIN prj_treatments AS prj_treatments ON ...
  ),
```
**What to Look For:**
- ✅ CTE names should be clean: `join_1`, `prj_visits`, `prj_treatments`, `star join`
- ✅ FROM/JOIN should reference clean names: `FROM prj_visits`, `JOIN prj_treatments`
- ❌ Should NOT see: `0/join_1`, `0/prj_visits`, `0/prj_treatments`
- ❌ Should NOT see: `FROM 0/prj_visits AS 0/prj_visits`

---

### **Validation Checkpoint 3: CV References (Line ~137)**
**Expected:**
```sql
INNER JOIN "_SYS_BIC"."Macabi_BI.Eligibility/CV_MD_EYPOSPER" AS cv_md_eyposper ON ...
```
**What to Look For:**
- ✅ Should use `"_SYS_BIC"` schema
- ✅ Package path should use `/` separator: `"Macabi_BI.Eligibility/CV_MD_EYPOSPER"`
- ✅ CV name should be after the slash
- ❌ Should NOT see: `MACABI_BI.ELIGIBILITY.CV_MD_EYPOSPER`
- ❌ Should NOT see: `INNER JOIN MACABI_BI.ELIGIBILITY.CV_MD_EYPOSPER`

---

## Known Remaining Issues

While testing, you may still see these issues (from pending bug list):

### **Issue 1: WHERE Clause Syntax Errors (Lines 71, 101)**
**Current Output:**
```sql
WHERE (("CALMONTH" = $$IP_CALMONTHs$$) or ($$IP_CALMONTHs$$) = '000000') AND ("JOB" = '') or ('') = '00000000'))
```
**Problems:**
- Extra closing parenthesis: `'00000000'))`
- Illogical conditions: `("JOB" = '') or ('') = '00000000')`
- Operator precedence issues

**Status:** This is related to **BUG-026 (Filter Value Type Mismatch)** or **BUG-002 (Complex Parameter Pattern Cleanup)** - still pending

---

## Testing Procedure

1. **Open Web UI:** Navigate to http://localhost:8000 (server is running)
2. **Upload XML:** Select `input/CV_ELIG_TRANS_01.xml`
3. **Check SQL Output:** Review the generated SQL against the 3 validation checkpoints above
4. **Report Results:** Note which checkpoints pass/fail

---

## Files Modified This Session

| File | Lines | Change Summary |
|------|-------|----------------|
| [converter.py](src/xml_to_sql/web/services/converter.py) | 243-247 | Handle both string and bytes input |
| [converter.py](src/xml_to_sql/web/services/converter.py) | 312-319 | Fix package path in CREATE VIEW (BUG-023) |
| [column_view_parser.py](src/xml_to_sql/parser/column_view_parser.py) | 488-516 | Parse `::` separator for CV references (BUG-025) |
| [scenario_parser.py](src/xml_to_sql/parser/scenario_parser.py) | 189-192 | Detect CV type based on `CV_` prefix or `::` |
| [scenario_parser.py](src/xml_to_sql/parser/scenario_parser.py) | 793-817 | Rewrite `_clean_ref()` to strip `#/0/`, `#//` prefixes |
| [renderer.py](src/xml_to_sql/sql/renderer.py) | 901-921 | Render CV references with `_SYS_BIC` format (BUG-025) |

---

## Next Steps After Validation

If all 3 checkpoints pass:
1. Mark BUG-025 as SOLVED
2. Document the node ID fix as a new solved bug
3. Move on to pending bugs: BUG-026, BUG-024, BUG-019, BUG-002

If any checkpoint fails:
1. Note which specific checkpoint failed
2. Provide the generated SQL line numbers and content
3. We'll debug and re-apply fixes as needed
