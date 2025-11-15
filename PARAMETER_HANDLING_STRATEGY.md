# Parameter Handling Strategy for HANA Mode

**Current Implementation**: Approach A - Parameter Removal  
**Status**: Active for v2.3.0  
**Future Enhancement**: Approaches B & C documented for later implementation

---

## Context

HANA Calculation Views (XML-based) support input parameters through HANA's graphical modeling engine. When converting to **HANA SQL views**, these parameters cannot be preserved using the same mechanism.

---

## Current Implementation: Approach A - Parameter Removal

### Strategy

**Remove all input parameter filter clauses** from WHERE conditions, resulting in views that return unfiltered data.

### How It Works

**XML Source**:
```xml
<parameter name="IP_TREAT_DATE" mandatory="false">
  <inlineType primitiveType="NVARCHAR" length="8"/>
  <defaultValue xsi:nil="true"/>
</parameter>

<filterExpression>
  ('$$IP_TREAT_DATE$$' = '' OR "ZZTREAT_DATE" = '$$IP_TREAT_DATE$$')
</filterExpression>
```

**HANA Mode Output**:
```sql
CREATE VIEW CV_EXAMPLE AS
WITH projection_1 AS (
  SELECT ...
  FROM base_table
  WHERE ("CONTROL_MODEL" = 'Z02')
  -- Parameter clause removed entirely
)
```

### Implementation

**Files**:
- `src/xml_to_sql/sql/function_translator.py::_substitute_placeholders()` - Replaces `$$IP_*$$` with `''`
- `src/xml_to_sql/sql/renderer.py::_cleanup_hana_parameter_conditions()` - Removes `('' = '' OR ...)` patterns

**Process**:
1. Parse XML with parameters
2. Generate SQL with parameter references
3. Substitute `$$IP_XXX$$` → `''`
4. Clean up always-true conditions: `('' = '' OR column = '')` → removed
5. Clean up orphaned AND, parens, etc.

### Pros & Cons

**Advantages** ✅:
- SQL views execute successfully in HANA
- Works for Snowflake deployment too
- Validates SQL structure is correct
- No complex parameter machinery needed

**Limitations** ⚠️:
- Views return ALL data (no runtime filtering)
- Users lose dynamic parameter functionality
- May return large datasets
- WHERE clauses simplified (some business logic removed)

### Current Status

**Working**: 
- ✅ CV_CNCLD_EVNTS.xml - Simple parameter patterns (executes successfully)
- ⏳ CV_CT02_CT03.xml - Testing in progress
- ⏳ CV_MCM_CNTRL_Q51.xml - Deferred (complex DATE() nesting)

**Known Issues**:
- Complex DATE() parameter patterns need enhanced cleanup
- Nested parameter clauses require better detection
- Multiple parameters in single expression create orphaned operators

---

## Future Enhancement: Approach B - Table-Valued Functions

### Strategy

Convert parameterized calculation views to HANA **table-valued functions** instead of views.

### Example Output

**HANA SQL**:
```sql
CREATE FUNCTION CV_CNCLD_EVNTS(
    IN IP_TREAT_DATE NVARCHAR(8) DEFAULT '',
    IN IP_CALMONTH NVARCHAR(6) DEFAULT '',
    IN IP_CALQUARTER NVARCHAR(5) DEFAULT '',
    IN IP_CALYEAR NVARCHAR(4) DEFAULT ''
)
RETURNS TABLE (
    ZZPROCESS_STAT NVARCHAR(2),
    REMUNERATION DECIMAL(15,2),
    ...
)
LANGUAGE SQLSCRIPT AS
BEGIN
    RETURN SELECT 
        ...
    FROM base_table
    WHERE ("CONTROL_MODEL" = 'Z02' AND
        (:IP_TREAT_DATE = '' OR "ZZTREAT_DATE" = :IP_TREAT_DATE));
END;
```

### Usage

**With Parameters**:
```sql
SELECT * FROM CV_CNCLD_EVNTS(
    IP_TREAT_DATE => '20240101',
    IP_CALMONTH => '202401'
);
```

**Without Parameters** (defaults):
```sql
SELECT * FROM CV_CNCLD_EVNTS(
    IP_TREAT_DATE => '',
    IP_CALMONTH => ''
);
```

### Implementation Requirements

**Files to Create**:
- `src/xml_to_sql/sql/hana_function_renderer.py` - Generate table-valued function syntax
- Add mode option: `hana_parameterized` vs `hana_simple`

**Complexity**: Medium-High
- HANA SQLScript syntax
- RETURNS TABLE definition from logical model
- Parameter declaration from XML variables
- Different BEGIN/END structure

### Pros & Cons

**Advantages** ✅:
- Preserves full parameter functionality
- Users can pass runtime values
- Dynamic filtering works as in original calculation view
- True functional equivalent

**Disadvantages** ⚠️:
- More complex SQL
- Different object type (function vs view)
- Query syntax changes: `SELECT * FROM function()` not `SELECT * FROM view`
- May require HANA permissions for function creation

---

## Future Enhancement: Approach C - Session Variables

### Strategy

Use HANA session variables to emulate parameter behavior.

### Example

**View Creation**:
```sql
CREATE VIEW CV_CNCLD_EVNTS AS
SELECT ...
WHERE ("CONTROL_MODEL" = 'Z02' AND
    (SESSION_CONTEXT('IP_TREAT_DATE') = '' OR 
     "ZZTREAT_DATE" = SESSION_CONTEXT('IP_TREAT_DATE')));
```

**Usage**:
```sql
-- Set session variables before query
CALL SYS.SET_SESSION_CONTEXT('IP_TREAT_DATE', '20240101');
CALL SYS.SET_SESSION_CONTEXT('IP_CALMONTH', '202401');

-- Query view
SELECT * FROM CV_CNCLD_EVNTS;
```

### Implementation Requirements

**Files to Modify**:
- `src/xml_to_sql/sql/function_translator.py::_substitute_placeholders()` - Convert `$$IP_XXX$$` to `SESSION_CONTEXT('IP_XXX')`

**Complexity**: Low-Medium

### Pros & Cons

**Advantages** ✅:
- Still a VIEW (not function)
- Parameters work at runtime
- Standard SQL VIEW syntax for queries

**Disadvantages** ⚠️:
- Requires session setup before each query
- Session-level state management
- May not work in connection pooling scenarios

---

## Decision Matrix

| Approach | Complexity | Parameters Work | View/Function | Production Ready | Timeline |
|----------|-----------|-----------------|---------------|------------------|----------|
| **A: Remove** | Low | ❌ No | View | ✅ Yes (for non-param cases) | ✅ **Now** |
| **B: Table Function** | High | ✅ Yes | Function | ✅ Yes | 🔮 Future |
| **C: Session Vars** | Medium | ✅ Yes | View | ⚠️ Depends | 🔮 Future |

---

## Recommendation

**Phase 1** (Current - v2.3.0): 
- ✅ Use Approach A (Parameter Removal)
- ✅ Validate SQL structure works
- ✅ Deploy to Snowflake (no parameters there anyway)
- ✅ Use for HANA testing/validation

**Phase 2** (Future - v2.4.0):
- 🔮 Implement Approach B (Table-Valued Functions)
- 🔮 Add `--hana-mode` option: `simple` (current) vs `parameterized` (new)
- 🔮 Preserve full calculation view functionality

**Phase 3** (Optional - v2.5.0):
- 🔮 Implement Approach C (Session Variables) as alternative
- 🔮 Let users choose based on their deployment scenario

---

## Files Reference

**Current Implementation**:
- `src/xml_to_sql/sql/function_translator.py::_substitute_placeholders()` - Parameter substitution
- `src/xml_to_sql/sql/renderer.py::_cleanup_hana_parameter_conditions()` - Cleanup logic
- `HANA_MODE_CONVERSION_RULES.md` - Rule #8: Input Parameters

**Future Enhancement Placeholder**:
- `src/xml_to_sql/sql/hana_function_renderer.py` - To be created
- `docs/HANA_PARAMETERIZED_VIEWS.md` - Design document (to be created)

---

**Status**: Approach A implemented and active. Approaches B & C documented for future enhancement.

