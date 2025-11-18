# VALIDATED SQL Scripts

This folder contains **VALIDATED** SQL scripts that have been successfully executed in HANA Studio.

## Purpose

- **Golden copies** of working SQL for regression testing
- **Backup** before making risky changes
- **Comparison baseline** when debugging issues

## Workflow

1. **Before testing a fix**: Compare new output with validated version
2. **After successful HANA execution**: Copy SQL here with execution time in filename or notes
3. **Before major changes**: Always ensure validated copies exist

## Validated Files

### BW_ON_HANA Instance ✅ 4/4 Working

| File | Source Folder | HANA Package | Execution | Date Validated |
|------|--------------|--------------|-----------|----------------|
| CV_TOP_PTHLGY.sql | BW_ON_HANA | Macabi_BI.EYAL.EYAL_CDS | ✅ Success | 2025-11-17 |
| CV_EQUIPMENT_STATUSES.sql | BW_ON_HANA | Macabi_BI.EYAL.EYAL_CDS | ✅ Success | 2025-11-17 |
| CV_INVENTORY_ORDERS.sql | BW_ON_HANA | Macabi_BI.EYAL.EYAL_CDS | ✅ Success | 2025-11-17 |
| CV_PURCHASE_ORDERS.sql | BW_ON_HANA | Macabi_BI.EYAL.EYAL_CDS | ✅ Success | 2025-11-17 |

**Result**: All BW_ON_HANA views work perfectly!

### ECC_ON_HANA Instance ⚠️ 1/2 Working

| File | Source Folder | HANA Package | Execution | Date Validated |
|------|--------------|--------------|-----------|----------------|
| CV_CNCLD_EVNTS.sql | ECC_ON_HANA | EYAL.EYAL_CTL | ✅ Success (74ms) | 2025-11-17 |

## Known Issues

| File | Source Folder | Issue | Root Cause |
|------|--------------|-------|------------|
| CV_CT02_CT03.sql | ECC_ON_HANA | Syntax error in REGEXP_LIKE filters | Calculated columns in WHERE need subquery alias 'calc' |

**Details**: See `docs/TESTING_LOG.md` for full analysis and attempted fixes.

---

**Last Updated**: 2025-11-17
