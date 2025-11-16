# Auto-Correction Testing Guide

## How Auto-Correction Works

Auto-correction automatically fixes common SQL issues in the generated SQL. It works **after** SQL generation and validation, scanning the SQL for patterns that need fixing.

## What Gets Auto-Corrected

### High-Confidence Fixes (Applied Automatically)

1. **Reserved Keywords** → Adds quotes around reserved keywords used as identifiers
   - Example: `SELECT ORDER FROM table` → `SELECT `ORDER` FROM table`
   - Triggered by: Validation issues with codes `RESERVED_KEYWORD`, `UNQUOTED_RESERVED_KEYWORD`, `RESERVED_KEYWORD_AS_IDENTIFIER`

2. **String Concatenation** → Replaces `+` with `||` for string concatenation
   - Example: `'Hello' + 'World'` → `'Hello' || 'World'`
   - Works even without validation issues - pattern matching finds `+` between strings
   - Note: Only fixes when `+` is clearly used for strings (between quoted strings)

3. **Function Translation** → Replaces HANA `IF()` with Snowflake `IFF()`
   - Example: `IF(condition, true_val, false_val)` → `IFF(condition, true_val, false_val)`
   - Works even without validation issues - pattern matching finds `IF(` patterns

## How to Test

### Step 1: Enable Auto-Correction

1. Open the web application
2. Go to the **Configuration** section (left panel)
3. Scroll down to **Auto-Correction** section
4. **Check** the box: "Enable auto-correction of SQL issues"

### Step 2: Convert Your XML File

1. Upload your XML file (drag & drop or click to select)
2. Click **"Convert to SQL"** button
3. Wait for conversion to complete

### Step 3: Check the Results

After conversion, look for these sections in the **SQL Preview** panel (right side):

#### A. Validation Results Section
- Shows any validation issues found
- Look for issues that auto-correction can fix:
  - Reserved keyword warnings
  - String concatenation warnings (`STRING_CONCAT_PLUS`)
  - HANA function warnings (`HANA_IF_NOT_TRANSLATED`)

#### B. Auto-Corrections Applied Section (NEW!)
- **Only appears if corrections were made**
- Shows:
  - Number of corrections applied
  - Each correction with:
    - **Confidence level** (HIGH/MEDIUM/LOW)
    - **Issue code** (what was fixed)
    - **Description** (what changed)
    - **Line number** (where in SQL)
    - **Before/After diff** (original → corrected)

#### C. SQL Content
- The SQL shown is the **corrected version** (if corrections were applied)
- Compare with validation issues to see what was fixed

## Testing Scenarios

### Scenario 1: Test String Concatenation Fix

**What to look for:**
- XML that generates SQL with string concatenation using `+`
- Example SQL might contain: `'text1' + 'text2'` or `column + 'suffix'`

**Expected result:**
- Auto-correction section shows: "Replaced string concatenation operator + with ||"
- SQL shows: `'text1' || 'text2'` or `column || 'suffix'`

### Scenario 2: Test Function Translation

**What to look for:**
- XML that uses HANA `IF()` function
- Generated SQL might contain: `IF(condition, value1, value2)`

**Expected result:**
- Auto-correction section shows: "Replaced HANA IF() function with Snowflake IFF()"
- SQL shows: `IFF(condition, value1, value2)`

### Scenario 3: Test Reserved Keywords

**What to look for:**
- XML that uses reserved keywords as column/table names
- Example: Column named "ORDER", "GROUP", "SELECT", etc.

**Expected result:**
- Validation shows: "Reserved keyword 'ORDER' used as identifier without quotes"
- Auto-correction section shows: "Quoted reserved keyword 'ORDER'"
- SQL shows: `` `ORDER` `` (with backticks)

## Important Notes

1. **Auto-correction only runs if enabled** - Make sure the checkbox is checked
2. **Corrections are applied to the SQL** - The final SQL shown is the corrected version
3. **Not all issues can be auto-corrected** - Some issues require manual fixes
4. **Pattern matching works independently** - String concat and IF() fixes work even if validation didn't flag them
5. **Reserved keyword fixes require validation** - Must be detected by validation first

## Troubleshooting

### "No corrections applied" message

**Possible reasons:**
- Your SQL doesn't have issues that auto-correction can fix
- The issues are not in the patterns auto-correction looks for
- Validation didn't detect the issues (for reserved keywords)

**What to check:**
1. Look at Validation Results - are there any warnings/errors?
2. Check the SQL content - does it contain `+` for strings or `IF(` functions?
3. Try a different XML file that you know has these issues

### Corrections not showing

**Possible reasons:**
- Auto-correction checkbox was not checked
- Server needs restart after code changes
- Browser cache - try hard refresh (Ctrl+F5)

**What to do:**
1. Verify checkbox is checked
2. Restart FastAPI server: `python run_server.py`
3. Hard refresh browser: Ctrl+F5 (Windows) or Cmd+Shift+R (Mac)

## Example Test Workflow

1. **Enable auto-correction** ✓
2. **Upload XML file** (e.g., `Sold_Materials_PROD.XML`)
3. **Click "Convert to SQL"**
4. **Check Validation Results** - Look for fixable issues
5. **Check Auto-Corrections Applied** - See what was fixed
6. **Review SQL** - Verify corrections look correct
7. **Compare** - If you have the original SQL, compare before/after

## Current Limitations

- **Schema qualification fixes** - Not yet fully implemented (placeholder)
- **CTE naming fixes** - Not yet fully implemented (placeholder)
- **Type casting fixes** - Not yet fully implemented (placeholder)
- **Re-validation** - Corrected SQL is not re-validated (to avoid double work)

These will be enhanced in future updates.

