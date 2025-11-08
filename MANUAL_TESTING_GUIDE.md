# Manual Testing Guide - Step by Step

> **Note:** This is a very detailed, step-by-step manual testing walkthrough. For the main testing guide, see [docs/TESTING.md](docs/TESTING.md). This guide provides exhaustive manual verification steps for thorough testing.

Follow these steps in order to verify the entire system works correctly.

## Prerequisites Check

### Step 1: Verify Environment
```cmd
cd "C:\Users\USER\Google Drive\SW_PLATFORM\15. AI\MY_LATEST_FILES\EXODUS\XML to SQL"
venv\Scripts\python --version
```
**Expected:** Python 3.11.x or higher

### Step 2: Verify Dependencies
```cmd
venv\Scripts\python -m pip list | findstr "lxml typer pyyaml pytest"
```
**Expected:** Should show lxml, typer, pyyaml, and pytest installed

---

## Phase 1: Unit Tests

### Step 3: Run All Unit Tests
```cmd
venv\Scripts\python -m pytest -v
```
**Expected Result:** 
- 23 tests should pass
- No failures or errors
- Output shows: `23 passed in X.XXs`

**If any test fails:** Note which test failed and the error message.

### Step 4: Run Specific Test Categories

**Test Config Loader:**
```cmd
venv\Scripts\python -m pytest tests/test_config_loader.py -v
```
**Expected:** 2 tests pass

**Test Parser:**
```cmd
venv\Scripts\python -m pytest tests/test_parser.py -v
```
**Expected:** 4 tests pass

**Test SQL Renderer:**
```cmd
venv\Scripts\python -m pytest tests/test_sql_renderer.py -v
```
**Expected:** 16 tests pass

---

## Phase 2: Configuration Testing

### Step 5: Verify Config File Exists
```cmd
dir config.yaml
```
**Expected:** File exists and is not empty

### Step 6: Test Config Loading
```cmd
venv\Scripts\python -m xml_to_sql.cli list --config config.yaml
```
**Expected Result:**
- Lists all scenarios from config.yaml
- Shows status (enabled/disabled)
- Shows source file paths
- No errors

**Example output:**
```
Sold_Materials [enabled] -> C:\...\Source (XML Files)\Sold_Materials.XML
SALES_BOM [enabled] -> C:\...\Source (XML Files)\SALES_BOM.XML
...
```

### Step 7: Test Dry Run (List Only)
```cmd
venv\Scripts\python -m xml_to_sql.cli convert --config config.yaml --list-only
```
**Expected Result:**
- Shows planned conversions
- Does NOT generate SQL files
- Shows source → target paths
- No errors

---

## Phase 3: Single File Conversion Tests

### Step 8: Convert Sold_Materials (Simple Case)
```cmd
venv\Scripts\python -m xml_to_sql.cli convert --config config.yaml --scenario Sold_Materials
```
**Expected Result:**
- Shows parsing statistics (nodes, filters, etc.)
- Shows success message with file path
- File created: `Target (SQL Scripts)\V_C_SOLD_MATERIALS.sql`

**Verify the SQL file:**
```cmd
type "Target (SQL Scripts)\V_C_SOLD_MATERIALS.sql"
```
**Expected:** 
- Contains `WITH` clause
- Contains `projection_1` CTE
- Contains `aggregation_1` CTE
- Contains `WHERE ERDAT > 20140101`
- Contains `GROUP BY` and `MAX(ERDAT)`
- Ends with `SELECT * FROM aggregation_1`

### Step 9: Convert SALES_BOM (Complex Joins)
```cmd
venv\Scripts\python -m xml_to_sql.cli convert --config config.yaml --scenario SALES_BOM
```
**Expected Result:**
- Success message
- File created: `Target (SQL Scripts)\V_C_SALES_BOM.sql`

**Verify the SQL:**
```cmd
type "Target (SQL Scripts)\V_C_SALES_BOM.sql"
```
**Expected:**
- Contains multiple CTEs
- Contains `JOIN` statements
- Contains multiple projection nodes
- Contains aggregation nodes

### Step 10: Convert KMDM_Materials (UNION Support)
```cmd
venv\Scripts\python -m xml_to_sql.cli convert --config config.yaml --scenario KMDM_Materials
```
**Expected Result:**
- Success message
- File created: `Target (SQL Scripts)\V_C_KMDM_MATERIALS.sql`

**Verify UNION in SQL:**
```cmd
type "Target (SQL Scripts)\V_C_KMDM_MATERIALS.sql" | findstr /i "UNION"
```
**Expected:**
- Should find `UNION ALL` or `UNION` in the SQL
- Multiple SELECT statements combined

### Step 11: Convert Recently_created_products (Multiple Unions)
```cmd
venv\Scripts\python -m xml_to_sql.cli convert --config config.yaml --scenario Recently_created_products
```
**Expected Result:**
- Success message
- File created: `Target (SQL Scripts)\V_C_RECENTLY_CREATED_PRODUCTS.sql`

**Verify:**
```cmd
type "Target (SQL Scripts)\V_C_RECENTLY_CREATED_PRODUCTS.sql" | findstr /i "UNION"
```
**Expected:** Multiple UNION statements

### Step 12: Convert CURRENT_MAT_SORT
```cmd
venv\Scripts\python -m xml_to_sql.cli convert --config config.yaml --scenario CURRENT_MAT_SORT
```
**Expected Result:**
- Success message
- File created: `Target (SQL Scripts)\V_C_CURRENT_MAT_SORT.sql`

### Step 13: Convert Material Details (Variables Test)
```cmd
venv\Scripts\python -m xml_to_sql.cli convert --config config.yaml --scenario "Material Details"
```
**Expected Result:**
- Success message
- File created: `Target (SQL Scripts)\V_C_MATERIAL_DETAILS.sql`
- Note: This file has variables defined

### Step 14: Convert Sold_Materials_PROD
```cmd
venv\Scripts\python -m xml_to_sql.cli convert --config config.yaml --scenario Sold_Materials_PROD
```
**Expected Result:**
- Success message
- File created: `Target (SQL Scripts)\V_C_SOLD_MATERIALS_PROD.sql`

---

## Phase 4: Batch Conversion Test

### Step 15: Convert All Enabled Scenarios
```cmd
venv\Scripts\python -m xml_to_sql.cli convert --config config.yaml
```
**Expected Result:**
- Processes all enabled scenarios from config
- Shows progress for each scenario
- Generates SQL files for all
- No errors

**Verify all files created:**
```cmd
dir "Target (SQL Scripts)\*.sql"
```
**Expected:** Should show 7 SQL files (one for each enabled scenario)

---

## Phase 5: SQL File Verification

### Step 16: Check All Generated SQL Files

**List all SQL files:**
```cmd
dir "Target (SQL Scripts)\*.sql" /b
```

**For each file, verify:**
1. File is not empty
2. Contains `SELECT` statement
3. Contains proper SQL syntax

**Quick check command:**
```cmd
for %f in ("Target (SQL Scripts)\*.sql") do @echo %f && @type "%f" | findstr /c:"SELECT" >nul && echo [OK] || echo [MISSING SELECT]
```

**Expected:** All files show `[OK]`

### Step 17: Verify SQL Structure

**Check for CTEs:**
```cmd
type "Target (SQL Scripts)\V_C_SOLD_MATERIALS.sql" | findstr /i "WITH"
```
**Expected:** Should find `WITH` keyword

**Check for proper column references:**
```cmd
type "Target (SQL Scripts)\V_C_SOLD_MATERIALS.sql" | findstr /i "AS"
```
**Expected:** Should find multiple `AS` keywords for column aliases

**Check for filters:**
```cmd
type "Target (SQL Scripts)\V_C_SOLD_MATERIALS.sql" | findstr /i "WHERE"
```
**Expected:** Should find `WHERE` clause

---

## Phase 6: Feature-Specific Tests

### Step 18: Test Function Translation

**Check for IFF (IF function translation):**
```cmd
type "Target (SQL Scripts)\*.sql" | findstr /i "IFF"
```
**Expected:** If any XML had IF functions, should see `IFF` in SQL

**Check for string concatenation (|| operator):**
```cmd
type "Target (SQL Scripts)\*.sql" | findstr /c:"||"
```
**Expected:** If any XML had string concatenation, should see `||`

### Step 19: Test UNION Support

**Count UNION statements:**
```cmd
type "Target (SQL Scripts)\*.sql" | findstr /i /c:"UNION ALL" /c:"UNION"
```
**Expected:** Should find UNION statements in files that have union nodes

### Step 20: Test Aggregation Support

**Check for GROUP BY:**
```cmd
type "Target (SQL Scripts)\*.sql" | findstr /i "GROUP BY"
```
**Expected:** Should find GROUP BY in files with aggregations

**Check for aggregation functions:**
```cmd
type "Target (SQL Scripts)\*.sql" | findstr /i "MAX\|MIN\|SUM\|COUNT\|AVG"
```
**Expected:** Should find aggregation functions

---

## Phase 7: Error Handling Tests

### Step 21: Test Missing File Handling

**Create a test config with non-existent file:**
```cmd
copy config.yaml config.test.yaml
```

Edit `config.test.yaml` and add:
```yaml
scenarios:
  - id: "NonExistent"
    source: "Missing_File.XML"
    enabled: true
```

**Run conversion:**
```cmd
venv\Scripts\python -m xml_to_sql.cli convert --config config.test.yaml --scenario NonExistent
```
**Expected:** 
- Error message indicating file not found
- No SQL file created
- Command exits with error code

### Step 22: Test Invalid Config

**Create invalid YAML:**
```cmd
echo invalid: yaml: [ > config.invalid.yaml
```

**Try to load:**
```cmd
venv\Scripts\python -m xml_to_sql.cli list --config config.invalid.yaml
```
**Expected:** 
- Error message about YAML parsing
- No scenarios listed

### Step 23: Test Disabled Scenario

**In config.yaml, set a scenario to disabled:**
```yaml
scenarios:
  - id: "Sold_Materials"
    enabled: false
```

**Try to convert:**
```cmd
venv\Scripts\python -m xml_to_sql.cli convert --config config.yaml --scenario Sold_Materials
```
**Expected:**
- Message: "No scenarios matched the requested filters"
- No SQL file created

**Revert the change** (set enabled: true) before continuing.

---

## Phase 8: Regression Test

### Step 24: Run Full Regression Suite
```cmd
venv\Scripts\python -m pytest tests/test_sql_renderer.py::test_render_all_xml_samples -v
```
**Expected:** All 7 XML sample tests pass

### Step 25: Verify No Warnings in Generated SQL

**Check for warning comments:**
```cmd
type "Target (SQL Scripts)\*.sql" | findstr /i "WARNING\|TODO\|FIXME"
```
**Expected:** 
- May have some warnings (this is normal)
- Note any warnings for review

---

## Phase 9: Output Verification

### Step 26: Check File Sizes
```cmd
dir "Target (SQL Scripts)\*.sql"
```
**Expected:**
- All files have reasonable size (> 100 bytes)
- No zero-byte files

### Step 27: Check SQL Syntax (Manual Review)

**Open each SQL file and verify:**
1. Proper CTE structure
2. Correct table/schema references
3. Valid SQL syntax
4. Proper column aliases
5. Correct WHERE clauses
6. Proper JOIN syntax (if applicable)
7. Correct GROUP BY (if applicable)
8. Valid UNION syntax (if applicable)

**Sample verification checklist:**
- [ ] V_C_SOLD_MATERIALS.sql - Simple projection + aggregation
- [ ] V_C_SALES_BOM.sql - Complex joins
- [ ] V_C_KMDM_MATERIALS.sql - Contains UNION
- [ ] V_C_RECENTLY_CREATED_PRODUCTS.sql - Multiple unions
- [ ] V_C_CURRENT_MAT_SORT.sql - Aggregation
- [ ] V_C_MATERIAL_DETAILS.sql - Variables
- [ ] V_C_SOLD_MATERIALS_PROD.sql - Production variant

---

## Phase 10: Performance Check

### Step 28: Time Conversion of All Files
```cmd
powershell -Command "Measure-Command { venv\Scripts\python -m xml_to_sql.cli convert --config config.yaml }"
```
**Expected:**
- Completes in reasonable time (< 30 seconds for all files)
- No timeouts or hangs

---

## Final Verification

### Step 29: Summary Check

**Count generated files:**
```cmd
dir "Target (SQL Scripts)\*.sql" | find /c ".sql"
```
**Expected:** Should match number of enabled scenarios (typically 7)

**Verify all scenarios processed:**
```cmd
venv\Scripts\python -m xml_to_sql.cli convert --config config.yaml --list-only
```
Compare with actual files generated.

### Step 30: Cleanup Test (Optional)

**Delete generated SQL files:**
```cmd
del "Target (SQL Scripts)\*.sql"
```

**Re-run conversion:**
```cmd
venv\Scripts\python -m xml_to_sql.cli convert --config config.yaml
```
**Expected:** All files regenerated successfully

---

## Test Results Log

Use this section to track your results:

- [ ] Step 3: All 23 unit tests pass
- [ ] Step 6: Config loading works
- [ ] Step 8: Sold_Materials conversion successful
- [ ] Step 9: SALES_BOM conversion successful
- [ ] Step 10: KMDM_Materials (UNION) conversion successful
- [ ] Step 11: Recently_created_products conversion successful
- [ ] Step 12: CURRENT_MAT_SORT conversion successful
- [ ] Step 13: Material Details conversion successful
- [ ] Step 14: Sold_Materials_PROD conversion successful
- [ ] Step 15: Batch conversion successful
- [ ] Step 16: All SQL files verified
- [ ] Step 18: Function translation works
- [ ] Step 19: UNION support works
- [ ] Step 20: Aggregation support works
- [ ] Step 21: Error handling works (missing file)
- [ ] Step 22: Error handling works (invalid config)
- [ ] Step 24: Regression tests pass

**Issues Found:**
(List any problems encountered)

**Notes:**
(Any observations or improvements needed)

---

## Success Criteria

✅ **All tests pass** - Unit tests complete successfully
✅ **All conversions work** - Each XML file generates valid SQL
✅ **SQL files are valid** - Generated SQL has proper structure
✅ **Error handling works** - Invalid inputs handled gracefully
✅ **No crashes** - System handles all scenarios without errors

If all steps complete successfully, the system is ready for use!

