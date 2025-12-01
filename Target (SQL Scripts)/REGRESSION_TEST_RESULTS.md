# Regression Test Results

**Last Updated**: 2025-11-21
**Commit**: e809a4d31677b91c0aa5dbea5648a2b5838a9f6a
**Total Validated**: 0 files

## Quick Status Dashboard

| XML File | Status | Validated On | Execution Time | HANA Errors | Notes |
|----------|--------|--------------|----------------|-------------|-------|
| _(No files validated yet)_ | - | - | - | - | Upload and test XMLs in HANA to populate this table |

## Legend

- ✅ **PASS**: SQL executed successfully in HANA without errors
- ⚠️ **WARN**: SQL executed but with warnings
- ❌ **FAIL**: SQL failed to execute in HANA
- 🔄 **PENDING**: Converted but not yet tested in HANA
- ⏸️ **SKIP**: Known to fail, waiting for specific bug fix

## Instructions

1. **Test XML in HANA**: Upload converted SQL to HANA Studio and execute
2. **Report Results**: Provide execution time, any errors, and HANA warnings
3. **I will update**: This table and copy successful SQLs to `VALIDATED/` folder
4. **Re-test**: After each bug fix, re-test all ✅ PASS files to catch regressions

## Current Session Focus

**Session 1 - Node ID Cleaning & CV References**
- **Target**: Fix `0/` prefix in node IDs and CV reference format
- **Files to Test**: CV_ELIG_TRANS_01.xml, CV_MD_EYPOSPER.xml
- **Expected**: No syntax errors with "0/" in FROM/SELECT clauses
