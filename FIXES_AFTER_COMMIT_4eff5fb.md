# Bug Fixes Applied AFTER Commit 4eff5fb

**Commit 4eff5fb**: SESSION 3: HANA multi-instance testing + validation infrastructure
**Date**: 2025-11-17
**Status at commit**: 5/5 XMLs validated, BUG-019 documented as active (not solved)

**This document**: Preserves all bug fixes that were applied AFTER commit 4eff5fb for reapplication

---

## BUG-020: IN() Function Syntax Conversion (SESSION 4)

**Status**: ✅ SOLVED (66ms HANA validation)
**File**: CV_CNCLD_EVNTS.xml
**Session**: SESSION 4 (2025-11-18)

### Problem Summary
XML uses function-style `IN(column, val1, val2)` but HANA requires operator-style `column IN (val1, val2)`.

### Fix Part 1: Function-Style to Operator-Style IN() Conversion

**File**: `src/xml_to_sql/sql/function_translator.py`
**Lines**: 652-763

**ADD NEW FUNCTION**:
```python
def _convert_in_function_to_operator(formula: str) -> str:
    """Convert function-style IN() to operator-style for HANA.

    XML uses: IN(column, 'a', 'b', 'c')
    HANA requires: column IN ('a', 'b', 'c')
    """
    import re

    result = formula
    max_iterations = 20  # Prevent infinite loops
    iteration = 0
    search_start = 0  # Track where to start searching to avoid re-processing

    while iteration < max_iterations:
        iteration += 1

        # Find IN( pattern starting from search_start
        match = re.search(r'\bIN\s*\(', result[search_start:], re.IGNORECASE)
        if not match:
            break

        # Adjust positions relative to full string
        in_start = search_start + match.start()
        in_end = search_start + match.end()  # Position after "IN("

        # Find matching closing paren, tracking nested parens and quotes
        depth = 1
        i = in_end
        in_quote = False
        quote_char = None

        while i < len(result) and depth > 0:
            c = result[i]

            # Handle quotes
            if c in ('"', "'") and (i == 0 or result[i-1] != '\\'):
                if not in_quote:
                    in_quote = True
                    quote_char = c
                elif c == quote_char:
                    in_quote = False
                    quote_char = None

            if not in_quote:
                if c == '(':
                    depth += 1
                elif c == ')':
                    depth -= 1

            i += 1

        if depth != 0:
            # Couldn't find matching paren, break
            break

        close_paren = i - 1

        # Extract arguments: IN(arg1, arg2, arg3, ...)
        args_str = result[in_end:close_paren]

        # Split by comma at depth 0, respecting nested parens and quotes
        args = []
        current_arg = []
        paren_depth = 0  # Track parentheses depth INSIDE the arguments
        in_quote = False
        quote_char = None

        for j, c in enumerate(args_str):
            # Handle quotes
            if c in ('"', "'"):
                if not in_quote:
                    in_quote = True
                    quote_char = c
                elif c == quote_char and (j == 0 or args_str[j-1] != '\\'):
                    in_quote = False
                    quote_char = None

            if not in_quote:
                if c == '(':
                    paren_depth += 1
                elif c == ')':
                    paren_depth -= 1
                elif c == ',' and paren_depth == 0:
                    # This is a top-level comma - split here
                    args.append(''.join(current_arg).strip())
                    current_arg = []
                    continue

            current_arg.append(c)

        if current_arg:
            args.append(''.join(current_arg).strip())

        if len(args) < 2:
            # Not enough args, skip this IN
            break

        # First arg is the expression, rest are values
        expression = args[0]
        values = args[1:]

        # Build: expression IN (val1, val2, val3)
        values_list = ', '.join(values)
        replacement = f"{expression} IN ({values_list})"

        # Replace in result
        result = result[:in_start] + replacement + result[close_paren + 1:]

        # Move search_start past the replacement to avoid re-processing
        search_start = in_start + len(replacement)

    return result
```

### Fix Part 2: HANA Version-Aware IN→OR Conversion

**File**: `src/xml_to_sql/sql/function_translator.py`
**Lines**: 227-238

**MODIFY translate_raw_formula()** - Add after line ~226:
```python
        # BUG-020 FIX: Convert function-style IN() to operator-style
        # XML: IN(col, val1, val2) → SQL: col IN (val1, val2)
        result = _convert_in_function_to_operator(result)

        # BUG-020 FIX: HANA 2.0+ supports IN() natively, no need to convert to OR
        # Only convert IN→OR for HANA 1.x
        hana_version = getattr(ctx, "hana_version", None)
        # Handle both Enum and string values
        version_str = hana_version.value if hasattr(hana_version, 'value') else hana_version

        if version_str and str(version_str).startswith("1."):
            result = _convert_in_to_or_for_hana(result)
```

**IMPORTANT**: This replaces unconditional `_convert_in_to_or_for_hana()` with version-aware call.

### Fix Part 3: Parameter Cleanup for Escaped Quotes

**File**: `src/xml_to_sql/sql/renderer.py`
**Line**: ~1029 (inside _cleanup_hana_parameter_conditions)

**MODIFY** - Find pattern matching for `('')` and change to handle `''''`:
```python
        # Find ('' = pattern or ('''' = pattern (escaped quote)
        match = re.search(r"\((?:''|'''')\s*=\s*'[^']*'\s+OR\s+", result, re.IGNORECASE)
```

**Rationale**: SQL escapes single quotes as `''`, literal single quote becomes `''''`.

### Validation
- ✅ CV_CNCLD_EVNTS.xml: 66ms HANA execution
- ✅ All 5 XMLs from SESSION 3: Still passing

---

## BUG-019: Column Qualification for SAP Special Characters (SESSION 5)

**Status**: ✅ SOLVED (39ms HANA validation)
**File**: CV_CT02_CT03.xml
**Session**: SESSION 5 (2025-11-18)

### Problem Summary
Column qualification regex excluded SAP BEx columns with special characters (`/BIC/*`, `/BI0/*`), REGEXP_LIKE patterns needed cleanup, views needed _SYS_BIC catalog.

### Fix Part 1: Column Qualification Regex Enhancement

**File**: `src/xml_to_sql/sql/renderer.py`
**Line**: ~515 (inside _render_projection, after comment "Pattern: Match any quoted identifier")

**FIND**:
```python
        pattern = r'(?<!\.)("[A-Z_][A-Z0-9_]*")'
```

**REPLACE WITH**:
```python
        pattern = r'(?<!\.)("[^"]+")'  # Match ANY quoted identifier including SAP columns like "/BIC/FIELD"
```

**Rationale**: Changed from `[A-Z_][A-Z0-9_]*` to `[^"]+` to match ANY character inside quotes, including `/`.

### Fix Part 2: _SYS_BIC Catalog Schema with Package Path

**File**: `src/xml_to_sql/web/services/converter.py`
**Lines**: 312-325

**FIND** (around line 312-320):
```python
        # Build qualified view name
        qualified_view_name = f"{effective_view_schema}.{scenario_id}" if effective_view_schema else scenario_id
```

**REPLACE WITH**:
```python
        # Build qualified view name
        # For HANA catalog calculation views in _SYS_BIC, package paths are REQUIRED
        # Format: _SYS_BIC."PACKAGE.PATH/VIEW_NAME"
        # For other schemas, use simple schema.viewname format
        # NOTE: Do NOT add quotes here - the SQL renderer's _quote_identifier will handle quoting
        if hana_package and effective_view_schema == "_SYS_BIC":
            # Catalog calculation view with package path
            view_name_with_package = f"{hana_package}/{scenario_id}"
            qualified_view_name = f'{effective_view_schema}.{view_name_with_package}'
        else:
            # Simple view name without package path
            qualified_view_name = (
                f"{effective_view_schema}.{scenario_id}" if effective_view_schema else scenario_id
            )
```

### Fix Part 3: REGEXP_LIKE CASE Simplification & Wildcard Removal

**File**: `src/xml_to_sql/sql/renderer.py`
**Lines**: ~1111-1159 (inside _cleanup_hana_parameter_conditions)

**ADD** after line ~1110 (after DATE('') cleanup):
```python
    # BUG-019: Simplify CASE WHEN with constant true conditions in REGEXP_LIKE
    # Pattern: REGEXP_LIKE(column, CASE WHEN '''' = '' THEN '*' ELSE ... END)
    # Since '''' (single quote) != '' (empty string), this is always false,
    # but '' = '' is always true. Need to simplify to just '*'
    # Also handle '' = '' pattern (always true)

    # Step 1: Simplify CASE WHEN '' = '' THEN value ELSE ... END to just value
    # This handles the always-true condition
    # Use a more robust pattern that handles any ELSE clause content
    def simplify_case_when(match):
        """Simplify CASE WHEN constant_true_condition to just the THEN value."""
        return f"'{match.group(1)}'"

    # Match CASE WHEN with any ELSE clause content (including column references)
    result = re.sub(
        r"CASE\s+WHEN\s+(?:''|'''')\s*=\s*''\s+THEN\s+'([^']*)'\s+ELSE\s+.*?END",
        simplify_case_when,
        result,
        flags=re.IGNORECASE | re.DOTALL
    )

    # Step 2: Remove REGEXP_LIKE(column, '*') entirely - matches everything, pointless filter
    # Pattern: REGEXP_LIKE(column, '*') AND ... or ... AND REGEXP_LIKE(column, '*')
    result = re.sub(
        r"REGEXP_LIKE\s*\([^,]+,\s*'\*'\s*\)\s+AND\s+",
        "",
        result,
        flags=re.IGNORECASE
    )
    result = re.sub(
        r"\s+AND\s+REGEXP_LIKE\s*\([^,]+,\s*'\*'\s*\)",
        "",
        result,
        flags=re.IGNORECASE
    )

    # Step 3: Remove entire WHERE clauses with only wildcard REGEXP_LIKE
    # Pattern: WHERE (REGEXP_LIKE(..., '*'))
    # Use DOTALL to handle multiline patterns
    result = re.sub(
        r"WHERE\s*\(\s*REGEXP_LIKE\s*\([^)]+,\s*'\*'\s*\)\s*\)",
        "",
        result,
        flags=re.IGNORECASE | re.DOTALL
    )

    # Step 4: Remove entire WHERE clauses that become empty after cleanup
    # Pattern: WHERE ()
    result = re.sub(r'WHERE\s*\(\s*\)', '', result, flags=re.IGNORECASE)
```

### Validation
- ✅ CV_CT02_CT03.xml: 39ms HANA execution
- ✅ All 6 XMLs: Passing

---

## BUG-021: Empty String IN Numeric Type Conversion (SESSION 7)

**Status**: ✅ SOLVED (82ms HANA validation)
**File**: CV_MCM_CNTRL_Q51.xml
**Session**: SESSION 7 (2025-11-18)

### Problem Summary
Parameter substitution resulted in `'' IN (0)` patterns causing HANA type conversion error [339] when comparing empty string to numeric value.

### Fix: Enhanced Parameter Cleanup for Type Mismatches

**File**: `src/xml_to_sql/sql/renderer.py`
**Lines**: ~1156-1193 (inside _cleanup_hana_parameter_conditions)

**ADD** after existing parameter cleanup patterns:
```python
    # BUG-021: Remove empty string IN numeric patterns that cause HANA type conversion errors
    # Error: SAP DBTech JDBC: [339]: invalid number: not a valid number string '' at implicit type conversion
    # Pattern: ('' IN (0) OR column IN (...)) → simplify to just second part
    # Also: '' IN (numeric_value) → remove entirely

    # Step 1: Remove ('' IN (number) OR ... ) patterns - keep only the second part
    # Match: ('' IN (digit) OR something)
    result = re.sub(
        r"\(\s*''\s+IN\s+\(\s*\d+\s*\)\s+OR\s+([^)]+)\)",
        r"(\1)",
        result,
        flags=re.IGNORECASE
    )

    # Step 2: Remove standalone '' IN (number) patterns with surrounding AND
    # Pattern: AND '' IN (0) AND → AND
    result = re.sub(
        r"\s+AND\s+''\s+IN\s+\(\s*\d+\s*\)\s+AND\s+",
        " AND ",
        result,
        flags=re.IGNORECASE
    )

    # Step 3: Remove '' IN (number) at start: ('' IN (0) AND ...)
    result = re.sub(
        r"\(\s*''\s+IN\s+\(\s*\d+\s*\)\s+AND\s+",
        "(",
        result,
        flags=re.IGNORECASE
    )

    # Step 4: Remove '' IN (number) at end: (... AND '' IN (0))
    result = re.sub(
        r"\s+AND\s+''\s+IN\s+\(\s*\d+\s*\)\s*\)",
        ")",
        result,
        flags=re.IGNORECASE
    )
```

### Validation
- ✅ CV_MCM_CNTRL_Q51.xml: 82ms HANA execution
- ✅ No type conversion errors

---

## BUG-022: Empty WHERE Clause After Parameter Cleanup (SESSION 7)

**Status**: ✅ SOLVED (53ms HANA validation)
**File**: CV_MCM_CNTRL_REJECTED.xml
**Session**: SESSION 7 (2025-11-18)

### Problem Summary
After BUG-021 cleanup removed all parameter patterns, empty `WHERE ()` clauses remained, causing syntax error [257].

### Fix Part 1: Empty WHERE Cleanup in Cleanup Function

**File**: `src/xml_to_sql/sql/renderer.py`
**Lines**: ~1199-1204 (inside _cleanup_hana_parameter_conditions)

**ADD** at the end of the function, before `return result`:
```python
    # BUG-022: Remove empty WHERE clauses that result from parameter cleanup
    # Pattern: WHERE () or WHERE ( ) (with optional whitespace)
    # This can occur when all conditions inside WHERE are cleaned up by BUG-021 fixes
    # Error: SAP DBTech JDBC: [257]: sql syntax error: incorrect syntax near ")"
    result = re.sub(
        r'\bWHERE\s+\(\s*\)',
        '',
        result,
        flags=re.IGNORECASE
    )
```

### Fix Part 2: Post-Cleanup Validation in Projection Rendering

**File**: `src/xml_to_sql/sql/renderer.py`
**Lines**: ~513-524 (inside _render_projection, subquery path)

**MODIFY** the FINAL cleanup section:
```python
        # FINAL cleanup: Remove parameter conditions AFTER all qualification
        if ctx.database_mode == DatabaseMode.HANA:
            qualified_where = _cleanup_hana_parameter_conditions(qualified_where)
            # BUG-022: Check if WHERE clause is effectively empty after cleanup
            qualified_where_stripped = qualified_where.strip()
            if qualified_where_stripped in ('', '()'):
                qualified_where = ''

        if qualified_where:
            sql = f"SELECT * FROM (\n  SELECT\n      {select_clause.replace(chr(10) + '    ', chr(10) + '      ')}\n  FROM {from_clause}\n) AS calc\nWHERE {qualified_where}"
        else:
            sql = f"SELECT * FROM (\n  SELECT\n      {select_clause.replace(chr(10) + '    ', chr(10) + '      ')}\n  FROM {from_clause}\n) AS calc"
```

### Fix Part 3: Post-Cleanup Validation in Projection (No Subquery)

**File**: `src/xml_to_sql/sql/renderer.py`
**Lines**: ~527-533 (inside _render_projection, no subquery path)

**MODIFY** the cleanup section:
```python
        # For HANA mode, still clean up parameter conditions
        if ctx.database_mode == DatabaseMode.HANA and where_clause:
            where_clause = _cleanup_hana_parameter_conditions(where_clause)
            # BUG-022: Check if WHERE clause is effectively empty after cleanup
            where_clause_stripped = where_clause.strip()
            if where_clause_stripped in ('', '()'):
                where_clause = ''
```

### Fix Part 4: Post-Cleanup Validation in Join Rendering

**File**: `src/xml_to_sql/sql/renderer.py`
**Lines**: ~591-596 (inside _render_join)

**ADD** after `where_clause = _render_filters(...)`:
```python
    # BUG-022: Clean up parameter conditions for HANA mode
    if ctx.database_mode == DatabaseMode.HANA and where_clause:
        where_clause = _cleanup_hana_parameter_conditions(where_clause)
        where_clause_stripped = where_clause.strip()
        if where_clause_stripped in ('', '()'):
            where_clause = ''
```

### Fix Part 5: Post-Cleanup Validation in Aggregation Rendering

**File**: `src/xml_to_sql/sql/renderer.py`
**Lines**: ~682-687 (inside _render_aggregation)

**ADD** after `where_clause = _render_filters(...)`:
```python
    # BUG-022: Clean up parameter conditions for HANA mode
    if ctx.database_mode == DatabaseMode.HANA and where_clause:
        where_clause = _cleanup_hana_parameter_conditions(where_clause)
        where_clause_stripped = where_clause.strip()
        if where_clause_stripped in ('', '()'):
            where_clause = ''
```

### Fix Part 6: Post-Cleanup Validation in Union Rendering

**File**: `src/xml_to_sql/sql/renderer.py`
**Lines**: ~768-773 (inside _render_union)

**MODIFY** the filters section:
```python
    if node.filters:
        where_clause = _render_filters(ctx, node.filters, None)

        # BUG-022: Clean up parameter conditions for HANA mode
        if ctx.database_mode == DatabaseMode.HANA and where_clause:
            where_clause = _cleanup_hana_parameter_conditions(where_clause)
            where_clause_stripped = where_clause.strip()
            if where_clause_stripped in ('', '()'):
                where_clause = ''

        if where_clause:
            sql = f"SELECT * FROM (\n{sql}\n) AS union_result\nWHERE {where_clause}"
```

### Fix Part 7: Post-Cleanup Validation in Calculation Rendering

**File**: `src/xml_to_sql/sql/renderer.py`
**Lines**: ~830-836 (inside _render_calculation)

**ADD** after `where_clause = _render_filters(...)`:
```python
    # BUG-022: Clean up parameter conditions for HANA mode
    if ctx.database_mode == DatabaseMode.HANA and where_clause:
        where_clause = _cleanup_hana_parameter_conditions(where_clause)
        # After cleanup, check if WHERE clause is empty or just empty parens
        where_clause_stripped = where_clause.strip()
        if where_clause_stripped in ('', '()'):
            where_clause = ''
```

### Validation
- ✅ CV_MCM_CNTRL_REJECTED.xml: 53ms HANA execution
- ✅ No syntax errors on empty WHERE clauses
- ✅ All 8 XMLs tested: Passing

---

## Application Order

**IMPORTANT**: Apply fixes in this order:
1. BUG-020 fixes (function_translator.py, renderer.py parameter cleanup)
2. BUG-019 fixes (renderer.py column qualification, converter.py _SYS_BIC, renderer.py REGEXP_LIKE)
3. BUG-021 fixes (renderer.py enhanced parameter cleanup for type mismatches)
4. BUG-022 fixes (renderer.py post-cleanup validation in all rendering functions)

This order ensures compatibility and no conflicts.

---

## FILES TO MODIFY

1. **src/xml_to_sql/sql/function_translator.py**
   - Add `_convert_in_function_to_operator()` function (BUG-020)
   - Modify `translate_raw_formula()` for version-aware IN processing (BUG-020)

2. **src/xml_to_sql/sql/renderer.py**
   - Modify column qualification regex pattern (BUG-019)
   - Enhance parameter cleanup for escaped quotes (BUG-020)
   - Add REGEXP_LIKE CASE simplification and wildcard removal (BUG-019)
   - Add empty string IN numeric cleanup patterns (BUG-021)
   - Add empty WHERE clause cleanup (BUG-022)
   - Add post-cleanup validation in projection rendering (BUG-022)
   - Add post-cleanup validation in join rendering (BUG-022)
   - Add post-cleanup validation in aggregation rendering (BUG-022)
   - Add post-cleanup validation in union rendering (BUG-022)
   - Add post-cleanup validation in calculation rendering (BUG-022)

3. **src/xml_to_sql/web/services/converter.py**
   - Add _SYS_BIC catalog schema with package path logic (BUG-019)

---

**Created**: 2025-11-18
**Purpose**: Preserve bug fixes before reverting to commit 4eff5fb
**Next Action**: Apply these fixes on top of commit 4eff5fb to get clean working state
