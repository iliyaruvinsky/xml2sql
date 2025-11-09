# SQL Validation Enhancement Plan

## Overview

This plan outlines the implementation of comprehensive SQL validation checks to ensure generated SQL is production-ready. The validation is organized into three phases, each building upon the previous.

## Architecture

### New Components

1. **Validation Module**: `src/xml_to_sql/sql/validator.py`
   - Core validation logic
   - Validation result classes
   - Validation severity levels

2. **Validation Result Types**:
   - `ValidationError`: Blocks conversion (critical issues)
   - `ValidationWarning`: Non-blocking (quality/performance issues)
   - `ValidationInfo`: Informational messages

3. **Integration Points**:
   - `src/xml_to_sql/sql/renderer.py`: Add validation hooks
   - `src/xml_to_sql/web/services/converter.py`: Return validation results
   - `src/xml_to_sql/web/api/models.py`: Add validation to API responses

---

## Phase 1: Critical Validations

**Goal**: Prevent invalid SQL from being generated. Catch structural errors and critical issues.

### 1.1 Create Validation Module

**File**: `src/xml_to_sql/sql/validator.py`

**Structure**:
```python
from dataclasses import dataclass
from enum import Enum
from typing import List, Optional

class ValidationSeverity(Enum):
    ERROR = "error"
    WARNING = "warning"
    INFO = "info"

@dataclass
class ValidationIssue:
    severity: ValidationSeverity
    message: str
    code: str
    line_number: Optional[int] = None
    column_number: Optional[int] = None

@dataclass
class ValidationResult:
    is_valid: bool
    errors: List[ValidationIssue]
    warnings: List[ValidationIssue]
    info: List[ValidationIssue]
    
    @property
    def has_errors(self) -> bool:
        return len(self.errors) > 0
```

### 1.2 SQL Structure Validation

**Function**: `validate_sql_structure(sql: str) -> ValidationResult`

**Checks**:
1. **Basic Syntax Structure**:
   - SQL is not empty
   - Contains at least one SELECT statement
   - Balanced parentheses in CTEs
   - Balanced quotes (single, double)
   - Proper CTE structure (WITH ... SELECT)

2. **CTE Validation**:
   - All CTEs have proper AS clauses
   - No duplicate CTE names
   - CTEs are properly comma-separated
   - Final SELECT exists

3. **Query Completeness**:
   - Final SELECT references valid CTE or table
   - All referenced CTEs are defined
   - No circular CTE dependencies

**Implementation**:
- Use regex patterns for basic structure
- Parse CTE definitions to extract names
- Validate CTE references in final SELECT

### 1.3 Query Completeness Validation

**Function**: `validate_query_completeness(scenario: Scenario, sql: str, ctx: RenderContext) -> ValidationResult`

**Checks**:
1. **Node References**:
   - All referenced nodes exist in scenario
   - All node inputs are valid
   - Final node exists and is reachable

2. **CTE References**:
   - All CTEs referenced in FROM/JOIN exist
   - No undefined CTE references
   - Proper CTE alias usage

3. **Data Source References**:
   - All data sources referenced exist
   - Schema names are valid (not empty, proper format)
   - Table/view names are valid

**Implementation**:
- Cross-reference SQL CTEs with scenario nodes
- Validate FROM clause references
- Check JOIN table references

### 1.4 Critical Warnings → Errors

**Upgrade these warnings to errors**:

1. **Cartesian Products**:
   - Current: Warning "Join {node_id} has no join conditions"
   - New: Error "Join {node_id} creates cartesian product (no join conditions)"

2. **Missing Final Node**:
   - Current: Warning "No terminal node found for final SELECT"
   - New: Error "No terminal node found - cannot generate valid SQL"

3. **Unsupported Node Types**:
   - Current: Warning "Unsupported node kind: {kind}"
   - New: Error "Unsupported node type {kind} - conversion not possible"

**Implementation**:
- Modify `src/xml_to_sql/sql/renderer.py`
- Change `ctx.warnings.append()` to raise `ValidationError` for critical issues
- Or collect errors separately and validate at end

### 1.5 Integration with Renderer

**File**: `src/xml_to_sql/sql/renderer.py`

**Changes**:
1. Add validation after SQL generation:
```python
def render_scenario(..., validate: bool = True) -> str | tuple[str, list[str]]:
    # ... existing rendering logic ...
    
    sql = _assemble_sql(ctes, final_select, ctx.warnings)
    
    if validate:
        from .validator import validate_sql_structure, validate_query_completeness
        structure_result = validate_sql_structure(sql)
        completeness_result = validate_query_completeness(scenario, sql, ctx)
        
        if structure_result.has_errors or completeness_result.has_errors:
            # Collect all errors
            all_errors = structure_result.errors + completeness_result.errors
            error_msg = "; ".join([e.message for e in all_errors])
            raise ValueError(f"SQL validation failed: {error_msg}")
        
        # Merge warnings
        ctx.warnings.extend([w.message for w in structure_result.warnings])
        ctx.warnings.extend([w.message for w in completeness_result.warnings])
    
    return (sql, ctx.warnings) if return_warnings else sql
```

### 1.6 Update API Models

**File**: `src/xml_to_sql/web/api/models.py`

**Add**:
```python
class ValidationIssue(BaseModel):
    severity: str  # "error", "warning", "info"
    message: str
    code: str
    line_number: Optional[int] = None

class ValidationResult(BaseModel):
    is_valid: bool
    errors: List[ValidationIssue] = Field(default_factory=list)
    warnings: List[ValidationIssue] = Field(default_factory=list)
    info: List[ValidationIssue] = Field(default_factory=list)

class ConversionResponse(BaseModel):
    # ... existing fields ...
    validation: Optional[ValidationResult] = None
```

### 1.7 Update Converter Service

**File**: `src/xml_to_sql/web/services/converter.py`

**Changes**:
- Add `validation` field to `ConversionResult`
- Capture validation results from renderer
- Return validation in API responses

---

## Phase 2: Enhanced Validation

**Goal**: Improve SQL quality with performance warnings and Snowflake-specific checks.

### 2.1 Performance Validation

**Function**: `validate_performance(sql: str, scenario: Scenario) -> ValidationResult`

**Checks**:
1. **Cartesian Product Detection**:
   - Detect `ON 1=1` in JOINs
   - Warn about potential large result sets
   - Suggest adding proper join conditions

2. **SELECT * Usage**:
   - Warn when SELECT * is used unnecessarily
   - Suggest explicit column lists
   - Check if logical model provides column list

3. **Missing Filters**:
   - Warn about queries without WHERE clauses on large tables
   - Suggest adding filters for performance

4. **Aggregation Without GROUP BY**:
   - Detect aggregation functions without GROUP BY
   - Validate aggregation correctness

**Implementation**:
- Parse SQL to detect patterns
- Use regex to find SELECT *, ON 1=1, etc.
- Analyze scenario structure for context

### 2.2 Snowflake-Specific Validation

**Function**: `validate_snowflake_specific(sql: str) -> ValidationResult`

**Checks**:

1. **Identifier Validation**:
   - Identifier length (max 255 characters for unquoted, unlimited for quoted)
   - Reserved keyword detection (must be quoted if used as identifier)
   - Special character validation (allowed in quoted identifiers)
   - Case sensitivity warnings (unquoted identifiers are uppercase)
   - Validate identifier quoting consistency
   - Check for invalid characters in unquoted identifiers (only alphanumeric and underscore)

2. **Schema/Table Naming**:
   - Schema name format validation
   - Table name format validation
   - Unqualified table references (warn - should use schema.table)
   - Three-part naming validation (database.schema.table)
   - Validate schema qualification in FROM/JOIN clauses

3. **Snowflake Function Syntax**:
   - **IFF() function**: Validate 3-parameter syntax (condition, then, else)
   - **String concatenation**: Validate `||` operator usage (not `+`)
   - **Date functions**: Validate TO_DATE(), DATE(), CURRENT_DATE() syntax
   - **Timestamp functions**: Validate TIMESTAMP_NTZ, TIMESTAMP_LTZ casting
   - **COALESCE()**: Validate NULL handling functions
   - **Window functions**: Validate OVER() clause syntax if present
   - **Aggregation functions**: Validate Snowflake-specific aggregations

4. **Data Type Validation**:
   - **Type casting syntax**: Validate `::TYPE` syntax (Snowflake-specific)
   - **Date literals**: Validate date format strings in TO_DATE()
   - **String literals**: Validate single-quote escaping (`''` for single quote)
   - **Numeric literals**: Validate numeric format
   - **Boolean values**: Validate TRUE/FALSE (not 1/0)

5. **CTE and Query Structure**:
   - **CTE syntax**: Validate WITH ... AS (...) syntax
   - **CTE limitations**: Warn if > 100 CTEs (Snowflake limit)
   - **Recursive CTEs**: Detect and validate RECURSIVE keyword if used
   - **Multiple CTEs**: Validate comma separation
   - **Final SELECT**: Must reference at least one CTE or table

6. **View Creation Syntax**:
   - **CREATE OR REPLACE VIEW**: Validate syntax if present
   - **View name**: Must be valid identifier
   - **View dependencies**: Check for circular dependencies

7. **JOIN Syntax**:
   - **JOIN types**: Validate INNER, LEFT OUTER, RIGHT OUTER, FULL OUTER
   - **ON clause**: Must have proper join conditions (not just 1=1)
   - **USING clause**: Validate if used (Snowflake supports USING)
   - **LATERAL joins**: Validate LATERAL keyword if used

8. **HANA to Snowflake Compatibility**:
   - **Detect HANA-specific functions**: Warn about functions not translated
   - **IF() vs IFF()**: Ensure IF() was translated to IFF()
   - **String concatenation**: Ensure `+` was translated to `||`
   - **SUBSTRING()**: Validate parameter count (Snowflake uses 1-based indexing)
   - **Date functions**: Check for HANA date function patterns

9. **Reserved Keywords**:
   - Maintain comprehensive list of Snowflake reserved keywords
   - Check identifiers against reserved keyword list
   - Warn if reserved keyword used without quoting
   - Common keywords: ACCOUNT, ADMIN, ALL, ALTER, AND, ANY, AS, BETWEEN, BY, CASE, CAST, CHECK, COLUMN, CONNECT, CONNECTION, CONSTRAINT, CREATE, CROSS, CURRENT, CURRENT_DATE, CURRENT_TIME, CURRENT_TIMESTAMP, CURRENT_USER, DATABASE, DELETE, DISTINCT, DROP, ELSE, END, EXISTS, FALSE, FOLLOWING, FOR, FOREIGN, FROM, FULL, FUNCTION, GRANT, GROUP, GGROUPING, HAVING, ILIKE, IN, INNER, INSERT, INTERSECT, INTO, IS, ISSUE, JOIN, LATERAL, LEFT, LIKE, LOCALTIME, LOCALTIMESTAMP, MINUS, NATURAL, NOT, NULL, NULLS, OF, ON, OR, ORDER, ORGANIZATION, OUTER, OVER, PARTITION, PRECEDING, PRIMARY, QUALIFY, REFERENCES, REVOKE, RIGHT, RLIKE, ROW, ROWS, SAMPLE, SCHEMA, SELECT, SET, SOME, START, TABLE, TABLESAMPLE, THEN, TO, TRIGGER, TRUE, TRY_CAST, UNION, UNIQUE, UPDATE, USING, VALUES, VIEW, WHEN, WHENEVER, WHERE, WITH

10. **SQL Statement Validation**:
    - **Only SELECT statements**: Ensure no DDL/DML mixed with SELECT
    - **No HANA-specific syntax**: Check for HANA calculation view syntax
    - **Proper statement termination**: Validate semicolon usage (optional in Snowflake)

11. **Performance-Specific Checks**:
    - **SAMPLE clause**: Validate SAMPLE syntax if used
    - **QUALIFY clause**: Validate QUALIFY syntax (Snowflake-specific)
    - **LIMIT/OFFSET**: Validate pagination syntax
    - **Window frame**: Validate ROWS/RANGE frame specifications

**Implementation Details**:

1. **Reserved Keywords List**:
```python
SNOWFLAKE_RESERVED_KEYWORDS = {
    'ACCOUNT', 'ADMIN', 'ALL', 'ALTER', 'AND', 'ANY', 'AS', 'BETWEEN',
    'BY', 'CASE', 'CAST', 'CHECK', 'COLUMN', 'CONNECT', 'CONNECTION',
    'CONSTRAINT', 'CREATE', 'CROSS', 'CURRENT', 'CURRENT_DATE',
    'CURRENT_TIME', 'CURRENT_TIMESTAMP', 'CURRENT_USER', 'DATABASE',
    'DELETE', 'DISTINCT', 'DROP', 'ELSE', 'END', 'EXISTS', 'FALSE',
    'FOLLOWING', 'FOR', 'FOREIGN', 'FROM', 'FULL', 'FUNCTION', 'GRANT',
    'GROUP', 'GROUPING', 'HAVING', 'ILIKE', 'IN', 'INNER', 'INSERT',
    'INTERSECT', 'INTO', 'IS', 'ISSUE', 'JOIN', 'LATERAL', 'LEFT',
    'LIKE', 'LOCALTIME', 'LOCALTIMESTAMP', 'MINUS', 'NATURAL', 'NOT',
    'NULL', 'NULLS', 'OF', 'ON', 'OR', 'ORDER', 'ORGANIZATION',
    'OUTER', 'OVER', 'PARTITION', 'PRECEDING', 'PRIMARY', 'QUALIFY',
    'REFERENCES', 'REVOKE', 'RIGHT', 'RLIKE', 'ROW', 'ROWS', 'SAMPLE',
    'SCHEMA', 'SELECT', 'SET', 'SOME', 'START', 'TABLE', 'TABLESAMPLE',
    'THEN', 'TO', 'TRIGGER', 'TRUE', 'TRY_CAST', 'UNION', 'UNIQUE',
    'UPDATE', 'USING', 'VALUES', 'VIEW', 'WHEN', 'WHENEVER', 'WHERE', 'WITH'
}
```

2. **Function Pattern Detection**:
   - Use regex to detect function calls
   - Validate parameter counts
   - Check for HANA-specific patterns

3. **Identifier Parsing**:
   - Parse quoted vs unquoted identifiers
   - Validate against reserved keywords
   - Check length constraints

4. **Type Casting Validation**:
   - Detect `::TYPE` patterns
   - Validate type names
   - Check for invalid type combinations

### 2.3 Query Complexity Analysis

**Function**: `analyze_query_complexity(sql: str, scenario: Scenario) -> ValidationResult`

**Checks**:
1. **CTE Count**:
   - Warn if > 20 CTEs (complexity)
   - Suggest breaking into views

2. **Join Count**:
   - Warn if > 10 joins in single query
   - Suggest query optimization

3. **Subquery Depth**:
   - Detect nested subqueries
   - Warn about deep nesting

**Implementation**:
- Count CTEs, JOINs, subqueries
- Set thresholds based on best practices
- Generate informational warnings

---

## Phase 3: Advanced Validation

**Goal**: Deep validation requiring schema introspection and type checking.

---

## Phase 4: Auto-Correction Engine

**Goal**: Automatically fix SQL issues detected during validation, improving SQL quality without manual intervention.

### 4.1 Auto-Correction Architecture

**New Component**: `src/xml_to_sql/sql/corrector.py`

**Structure**:
```python
from dataclasses import dataclass
from typing import List, Optional
from .validator import ValidationResult, ValidationIssue

@dataclass
class Correction:
    """Represents a single correction applied to SQL."""
    issue_code: str  # Code of the validation issue being fixed
    original_text: str  # Original SQL text that was replaced
    corrected_text: str  # Corrected SQL text
    line_number: Optional[int] = None
    description: str = ""  # Human-readable description of the fix

@dataclass
class CorrectionResult:
    """Result of auto-correction process."""
    corrected_sql: str
    corrections_applied: List[Correction]
    issues_fixed: List[str]  # Issue codes that were fixed
    issues_remaining: List[ValidationIssue]  # Issues that couldn't be auto-fixed
    auto_fix_enabled: bool
```

### 4.2 Auto-Correctable Issues

**Categories of issues that can be auto-corrected**:

1. **Syntax Fixes** (High Confidence):
   - **Unquoted Reserved Keywords**: Add quotes around reserved keywords used as identifiers
   - **String Concatenation**: Replace `+` with `||` for string concatenation
   - **IF() to IFF()**: Replace HANA `IF()` with Snowflake `IFF()`
   - **Missing Quotes**: Add quotes to identifiers that need them
   - **Unbalanced Quotes**: Fix quote escaping issues
   - **Type Casting**: Fix invalid type casting syntax

2. **Structure Fixes** (Medium Confidence):
   - **Missing Schema Qualification**: Add schema prefix to unqualified table references
   - **CTE Naming**: Fix duplicate CTE names by adding suffixes
   - **Identifier Length**: Truncate or quote identifiers exceeding 255 characters
   - **Case Sensitivity**: Normalize identifier casing (uppercase unquoted identifiers)

3. **HANA to Snowflake Translation** (High Confidence):
   - **Function Translation**: Apply function translations that were missed
   - **Date Function Syntax**: Convert HANA date functions to Snowflake equivalents
   - **Aggregation Syntax**: Fix aggregation function syntax differences

4. **Performance Fixes** (Low Confidence - Requires User Approval):
   - **SELECT * Replacement**: Replace SELECT * with explicit column lists (if logical model available)
   - **Cartesian Product Warnings**: Add comment suggesting proper join conditions (cannot auto-fix)

### 4.3 Auto-Correction Functions

**Function**: `auto_correct_sql(sql: str, validation_result: ValidationResult, scenario: Optional[Scenario] = None, auto_fix_config: Optional[Dict] = None) -> CorrectionResult`

**Parameters**:
- `sql`: Original SQL to correct
- `validation_result`: Validation results containing issues to fix
- `scenario`: Optional scenario IR for context-aware fixes
- `auto_fix_config`: Configuration for which fixes to apply

**Correction Functions**:

1. **`fix_reserved_keywords(sql: str, issues: List[ValidationIssue]) -> tuple[str, List[Correction]]`**:
   - Detects unquoted reserved keywords
   - Adds quotes around them
   - Returns corrected SQL and list of corrections

2. **`fix_string_concatenation(sql: str, issues: List[ValidationIssue]) -> tuple[str, List[Correction]]`**:
   - Finds `+` operators used for string concatenation
   - Replaces with `||`
   - Validates context (not numeric addition)

3. **`fix_function_calls(sql: str, issues: List[ValidationIssue]) -> tuple[str, List[Correction]]`**:
   - Replaces `IF()` with `IFF()`
   - Fixes function parameter counts
   - Translates HANA-specific functions

4. **`fix_identifier_quoting(sql: str, issues: List[ValidationIssue]) -> tuple[str, List[Correction]]`**:
   - Adds quotes to identifiers that need them
   - Fixes identifier length issues
   - Normalizes identifier casing

5. **`fix_schema_qualification(sql: str, issues: List[ValidationIssue], scenario: Optional[Scenario]) -> tuple[str, List[Correction]]`**:
   - Adds schema prefixes to unqualified tables
   - Uses schema from data sources in scenario
   - Applies schema overrides if available

6. **`fix_type_casting(sql: str, issues: List[ValidationIssue]) -> tuple[str, List[Correction]]`**:
   - Fixes invalid type casting syntax
   - Converts to Snowflake `::TYPE` syntax
   - Validates type names

### 4.4 Correction Confidence Levels

**Confidence Levels**:
- **High**: Safe to apply automatically (syntax fixes, function translations)
- **Medium**: Apply with warning (structural fixes, identifier changes)
- **Low**: Require user approval (SELECT * replacement, major structural changes)

**Configuration**:
```python
class AutoFixConfig:
    enable_high_confidence_fixes: bool = True
    enable_medium_confidence_fixes: bool = True
    enable_low_confidence_fixes: bool = False  # Require approval
    require_user_confirmation: bool = False  # Global confirmation flag
    max_corrections_per_issue_type: int = 10  # Prevent excessive changes
```

### 4.5 Integration with Validation

**Updated Flow**:
```python
def render_scenario(..., auto_fix: bool = False, auto_fix_config: Optional[Dict] = None) -> str | tuple[str, list[str]]:
    # ... existing rendering logic ...
    
    sql = _assemble_sql(ctes, final_select, ctx.warnings)
    
    # Validate
    validation_result = validate_sql(sql, scenario, ctx)
    
    # Auto-correct if enabled
    if auto_fix and validation_result.has_issues:
        from .corrector import auto_correct_sql
        correction_result = auto_correct_sql(sql, validation_result, scenario, auto_fix_config)
        
        if correction_result.corrections_applied:
            sql = correction_result.corrected_sql
            # Add correction notes to warnings
            for correction in correction_result.corrections_applied:
                ctx.warnings.append(f"Auto-fixed: {correction.description}")
    
    return (sql, ctx.warnings) if return_warnings else sql
```

### 4.6 Correction Reporting

**Add to API Models**:
```python
class CorrectionInfo(BaseModel):
    issue_code: str
    original_text: str
    corrected_text: str
    line_number: Optional[int] = None
    description: str

class CorrectionResult(BaseModel):
    corrected_sql: str
    corrections_applied: List[CorrectionInfo]
    issues_fixed: List[str]
    issues_remaining: List[ValidationIssue]
    auto_fix_enabled: bool

class ConversionResponse(BaseModel):
    # ... existing fields ...
    validation: Optional[ValidationResult] = None
    corrections: Optional[CorrectionResult] = None  # New field
```

### 4.7 User Control

**API Endpoints**:
- `POST /api/convert/single?auto_fix=true` - Enable auto-correction
- `POST /api/convert/single?auto_fix=false` - Disable auto-correction (default)
- `POST /api/convert/single?auto_fix_config={json}` - Custom auto-fix configuration

**Web UI**:
- Checkbox: "Auto-fix issues" in conversion form
- Show corrections applied in results
- Allow user to accept/reject corrections
- Preview corrected SQL before applying

### 4.8 Safety Measures

1. **Backup Original**: Always keep original SQL for comparison
2. **Correction Limits**: Limit number of corrections per issue type
3. **Validation After Correction**: Re-validate corrected SQL
4. **Rollback Capability**: Allow reverting to original SQL
5. **Confirmation for High-Impact Changes**: Require approval for structural changes

---

## Phase 3: Advanced Validation (Continued)

### 3.1 Column Reference Validation

**Function**: `validate_column_references(sql: str, scenario: Scenario, schema_metadata: Optional[Dict]) -> ValidationResult`

**Checks**:
1. **Column Existence**:
   - Verify columns exist in referenced tables
   - Check column names against schema
   - Validate qualified column references

2. **Column Type Compatibility**:
   - Check type compatibility in expressions
   - Validate aggregation compatibility
   - Check function parameter types

**Requirements**:
- Schema metadata connection (optional)
- Table/column introspection
- Type mapping knowledge

**Implementation**:
- Optional feature (requires Snowflake connection)
- Cache schema metadata
- Validate when metadata available

### 3.2 Expression Validation

**Function**: `validate_expressions(scenario: Scenario) -> ValidationResult`

**Checks**:
1. **Expression Syntax**:
   - Validate calculated attribute expressions
   - Check filter predicate syntax
   - Validate function calls

2. **Type Safety**:
   - Type inference for expressions
   - Type compatibility checks
   - Implicit conversion warnings

**Implementation**:
- Use existing `type_inference.py`
- Extend with validation logic
- Cross-reference with domain models

### 3.3 SQL Execution Testing (Optional)

**Function**: `test_sql_execution(sql: str, connection: Optional[Connection]) -> ValidationResult`

**Checks**:
1. **Syntax Validation**:
   - Execute EXPLAIN PLAN
   - Catch syntax errors
   - Validate query plan

2. **Execution Testing**:
   - Run with LIMIT 0 (dry run)
   - Check for runtime errors
   - Validate result structure

**Requirements**:
- Snowflake connection (optional)
- Configuration for test environment
- Error handling for connection issues

**Implementation**:
- Make completely optional
- Only run if connection provided
- Cache results to avoid repeated tests

---

## Implementation Order

### Step 1: Phase 1 Foundation
1. Create `src/xml_to_sql/sql/validator.py` with base classes
2. Implement `validate_sql_structure()`
3. Implement `validate_query_completeness()`
4. Integrate with `render_scenario()`
5. Update API models and responses
6. Add unit tests

### Step 2: Critical Warnings → Errors
1. Identify critical warnings in renderer
2. Create validation errors for critical cases
3. Update renderer to raise/collect errors
4. Test error handling

### Step 3: Phase 2 Enhancements
1. Implement performance validation
2. Implement Snowflake-specific validation
3. Add complexity analysis
4. Integrate with existing validation
5. Add tests

### Step 4: Phase 4 Auto-Correction (Core Features)
1. Create `src/xml_to_sql/sql/corrector.py` with base classes
2. Implement high-confidence fixes:
   - Reserved keyword quoting
   - String concatenation (`+` → `||`)
   - Function translation (`IF()` → `IFF()`)
   - Identifier quoting fixes
3. Integrate auto-correction into renderer
4. Add correction reporting to API
5. Add unit tests for corrections

### Step 5: Phase 4 Auto-Correction (Advanced Features)
1. Implement medium-confidence fixes:
   - Schema qualification
   - CTE naming conflicts
   - Identifier length/casing
2. Add configuration for auto-fix levels
3. Add user controls in API and UI
4. Add safety measures (backup, limits, re-validation)
5. Add tests

### Step 6: Phase 3 Advanced (Optional)
1. Design schema metadata interface
2. Implement column reference validation
3. Implement expression validation
4. Add SQL execution testing (if needed)
5. Make all Phase 3 features optional

---

## Testing Strategy

### Unit Tests
**File**: `tests/test_sql_validator.py`

**Test Cases**:

1. **SQL Structure Validation**:
   - Valid SQL with CTEs
   - Invalid SQL (missing SELECT)
   - Unbalanced parentheses
   - Unbalanced quotes
   - Missing final SELECT
   - Duplicate CTE names

2. **Query Completeness**:
   - Missing CTE references
   - Invalid node references
   - Missing final node
   - Circular dependencies

3. **Critical Error Detection**:
   - Cartesian products (ON 1=1)
   - Missing nodes
   - Unsupported node types

4. **Performance Warnings**:
   - SELECT * usage
   - Missing WHERE clauses
   - Large cartesian products

5. **Snowflake-Specific Validation**:
   - **Identifier Tests**:
     - Reserved keyword without quotes (should warn)
     - Identifier > 255 chars unquoted (should error)
     - Valid quoted identifiers with special chars
     - Invalid characters in unquoted identifiers
   
   - **Function Syntax Tests**:
     - IFF() with 3 parameters (valid)
     - IFF() with wrong parameter count (invalid)
     - String concatenation with || (valid)
     - String concatenation with + (should warn - HANA syntax)
     - TO_DATE() with valid format string
     - TO_DATE() with invalid format string
     - Type casting with :: syntax (valid)
     - Invalid type casting syntax
   
   - **CTE Tests**:
     - Valid WITH ... AS syntax
     - Invalid CTE syntax
     - > 100 CTEs (should warn)
     - Recursive CTE detection
   
   - **JOIN Tests**:
     - Valid JOIN types (INNER, LEFT OUTER, etc.)
     - Invalid JOIN syntax
     - USING clause validation
     - LATERAL join validation
   
   - **HANA Compatibility Tests**:
     - IF() function not translated (should warn)
     - String + not translated to || (should warn)
     - HANA date functions detected (should warn)
   
   - **Reserved Keywords Tests**:
     - Reserved keyword as identifier without quotes (error)
     - Reserved keyword as identifier with quotes (valid)
     - Common reserved keywords (SELECT, FROM, WHERE, etc.)

6. **Edge Cases**:
   - Empty SQL
   - Malformed CTEs
   - SQL with only comments
   - SQL with mixed case keywords
   - SQL with special characters in identifiers

7. **Auto-Correction Tests**:
   - Reserved keyword fixing (unquoted → quoted)
   - String concatenation fixing (`+` → `||`)
   - Function translation (`IF()` → `IFF()`)
   - Identifier quoting fixes
   - Schema qualification fixes
   - Correction rollback capability
   - Re-validation after correction
   - Correction limits enforcement
   - Multiple corrections in single SQL
   - Correction confidence levels

### Integration Tests
1. End-to-end conversion with validation
2. API responses with validation results
3. Error handling and reporting
4. End-to-end conversion with auto-correction
5. API responses with correction results
6. User acceptance/rejection of corrections

### Test Data
- Valid XML files (should pass all validations)
- Invalid XML files (should catch errors)
- Edge cases (zero nodes, complex queries, etc.)

---

## Configuration

### Validation Settings

**File**: `src/xml_to_sql/config/schema.py` (extend)

**Add**:
```python
class ValidationConfig:
    enable_structure_validation: bool = True
    enable_completeness_validation: bool = True
    enable_performance_validation: bool = True
    enable_snowflake_validation: bool = True
    enable_column_validation: bool = False  # Phase 3
    enable_execution_testing: bool = False  # Phase 3
    strict_mode: bool = False  # Treat warnings as errors
```

---

## Documentation Updates

1. **User Documentation**:
   - Explain validation levels
   - How to interpret validation results
   - Configuration options

2. **Developer Documentation**:
   - Validation architecture
   - Adding new validations
   - Testing validations

3. **API Documentation**:
   - Validation response format
   - Error codes and meanings
   - Best practices

---

## Migration Path

1. **Backward Compatibility**:
   - Validation is opt-in initially (default: enabled)
   - Existing code continues to work
   - Warnings still generated for compatibility

2. **Gradual Rollout**:
   - Phase 1: Critical validations (immediate)
   - Phase 2: Enhanced validations (after Phase 1 stable)
   - Phase 3: Advanced validations (optional, as needed)

3. **Breaking Changes**:
   - None in Phase 1 (errors only for truly invalid SQL)
   - Phase 2: New warnings (non-breaking)
   - Phase 3: Optional features (non-breaking)

---

## Success Criteria

### Phase 1
- All invalid SQL is caught before generation
- Critical issues (cartesian products, missing nodes) are errors
- Validation results included in API responses
- 100% test coverage for validation functions

### Phase 2
- Performance warnings for common issues
- Snowflake-specific validation catches compatibility issues
- Query complexity analysis provides actionable feedback

### Phase 3
- Column reference validation works with schema metadata
- Expression validation catches type errors
- SQL execution testing validates syntax (when enabled)

### Phase 4
- High-confidence issues are automatically fixed
- Corrected SQL passes validation
- Users can see what was corrected
- Safety measures prevent incorrect fixes
- Auto-correction improves SQL quality without manual intervention

---

## Estimated Effort

- **Phase 1**: 2-3 days
- **Phase 2**: 2-3 days
- **Phase 3**: 3-5 days (optional, as needed)
- **Phase 4**: 3-4 days (core: 2 days, advanced: 1-2 days)

**Total**: 
- **Phases 1-2**: 4-6 days (essential validations)
- **Phases 1-2 + Phase 4 Core**: 6-8 days (with basic auto-correction)
- **All Phases**: 10-15 days (complete solution with optional features)

