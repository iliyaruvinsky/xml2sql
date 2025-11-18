# Testing Log - HANA SQL Generation

**Date**: 2025-11-17
**Session**: Session 3 - Multi-instance testing

---

## Test Environment

- **HANA Studio**: kdsu
- **Database Mode**: HANA 2.0
- **Test Method**: Execute generated SQL in HANA Studio

---

## Validated Working Files ✅

### BW_ON_HANA Instance (Macabi_BI.EYAL.EYAL_CDS)

| XML File | SQL Output | Execution Time | Status | Notes |
|----------|-----------|----------------|--------|-------|
| CV_TOP_PTHLGY.xml | CV_TOP_PTHLGY.sql | Working | ✅ | Large multi-CTE view with joins, filters |
| CV_EQUIPMENT_STATUSES.xml | CV_EQUIPMENT_STATUSES.sql | Working | ✅ | |
| CV_INVENTORY_ORDERS.xml | CV_INVENTORY_ORDERS.sql | Working | ✅ | |
| CV_PURCHASE_ORDERS.xml | CV_PURCHASE_ORDERS.sql | Working | ✅ | |

**Path Used**: `Macabi_BI.EYAL.EYAL_CDS`
**Result**: **ALL BW_ON_HANA views work perfectly** ✅

---

### ECC_ON_HANA Instance (EYAL.EYAL_CTL)

| XML File | SQL Output | Execution Time | Status | Notes |
|----------|-----------|----------------|--------|-------|
| CV_CNCLD_EVNTS.xml | CV_CNCLD_EVNTS.sql | 74ms | ✅ | Successfully executed |
| CV_CT02_CT03.xml | CV_CT02_CT03.sql | - | ❌ | **Known Issue** - See below |

**Path Used**: `EYAL.EYAL_CTL`

---

## Known Issues 🔴

### Issue #1: CV_CT02_CT03.xml - Table Qualification in REGEXP_LIKE Filters

**Status**: ❌ Not Working
**Error**:
```
SAP DBTech JDBC: [257]: sql syntax error: incorrect syntax near "AND": line 29 col 206 (at pos 1869)
```

**Root Cause**:
- XML has **calculated columns** (`CAL_PAD_TRTNUM`, `CAL_PAD_EVNTID`) that are referenced in WHERE clause
- WHERE clause uses REGEXP_LIKE with pattern matching
- Filters are generated with full table qualification: `SAPABAP1."/BIC/AEZO_CT0200"."/BIC/EYTRTNUM"`
- Should use subquery alias: `calc."/BIC/EYTRTNUM"`
- Also has escaped empty string issue: `''''` instead of `''`

**Example of Problem**:
```sql
-- WRONG (current output):
WHERE (REGEXP_LIKE(SAPABAP1."/BIC/AEZO_CT0200"."/BIC/EYTRTNUM", ...))

-- CORRECT (needed):
WHERE (REGEXP_LIKE(calc."/BIC/EYTRTNUM", ...))
```

**Why It's Difficult**:
- Needs subquery wrapper with `calc` alias when WHERE references calculated columns
- But changing this logic breaks other working views (CV_TOP_PTHLGY)
- Requires surgical fix specific to this pattern

**Attempts Made**:
1. ❌ Regex replacement in WHERE clause - didn't match pattern
2. ❌ Always use "calc" alias when calculated columns exist - broke CV_TOP_PTHLGY
3. ❌ Check if filters reference calculated columns before rendering - broke topological sort

**Next Steps**:
- Document as known limitation
- Test more XMLs to find pattern
- Come back with fresh approach

---

## Bugs Fixed During Session ✅

### Bug #1: Double-Quoted View Names
**Fixed**: ✅
**Issue**: `""_SYS_BIC"".""Macabi_BI.EYAL.EYAL_CDS/CV_TOP_PTHLGY""` (double quotes)
**Solution**: Removed manual quoting from converter.py and cli/app.py - let renderer handle all quoting
**Files Changed**:
- `src/xml_to_sql/web/services/converter.py:320`
- `src/xml_to_sql/cli/app.py:87`

### Bug #2: Escaped Empty String in WHERE Clause
**Fixed**: ✅
**Issue**: `('''' = '' OR column = '''')` - four quotes instead of two
**Solution**: Updated `_cleanup_hana_parameter_conditions` regex pattern from `''{0,2}` to `'{2,4}`
**File Changed**: `src/xml_to_sql/sql/renderer.py:1018`

### Bug #3: Empty String Literal Escaping
**Status**: ⚠️ Partially Fixed
**Issue**: `_render_literal` was escaping `''` to `''''`
**Attempted Fix**: Added check for `value in ("''", '""')` before escaping
**Result**: Still seeing `''''` in some cases - cleanup regex handles it

---

## Testing Strategy Going Forward

### Phase 1: Validate More XMLs ✅ IN PROGRESS
- [x] Test all BW_ON_HANA XMLs (4/4 working)
- [x] Test ECC_ON_HANA XMLs (1/2 working, 1 known issue)
- [ ] Test remaining XML files from other folders
- [ ] Document each success/failure

### Phase 2: Pattern Analysis
- Identify common patterns in working vs failing files
- Find common characteristics of problematic XMLs
- Build test suite for regression testing

### Phase 3: Systematic Fixes
- Fix bugs that affect multiple files first
- Address edge cases (like CV_CT02_CT03) last
- Always validate against golden copies before declaring success

---

## Lessons Learned

1. **Always backup validated SQL** - Create VALIDATED folder with working copies
2. **Test before claiming fix** - Multiple attempts broke working files
3. **Don't use regex for structural SQL fixes** - Need to fix at the right layer (parser/renderer)
4. **One bug at a time** - Trying to fix multiple issues together creates more problems
5. **Revert when stuck** - `git checkout` saved us from broken state

---

## File Structure

```
Target (SQL Scripts)/
├── VALIDATED/              # Golden copies of working SQL
│   ├── README.md          # Documentation of validated files
│   ├── CV_TOP_PTHLGY.sql
│   ├── CV_EQUIPMENT_STATUSES.sql
│   ├── CV_INVENTORY_ORDERS.sql
│   ├── CV_PURCHASE_ORDERS.sql
│   └── CV_CNCLD_EVNTS.sql
├── CV_*.sql               # Current generated SQL (may change)
└── ...
```

---

**Next Session TODO**:
- Test remaining XML files
- Document success rate by XML type/source
- Create test automation script
- Update llm_handover.md with complete status

---

**Last Updated**: 2025-11-17 18:30
