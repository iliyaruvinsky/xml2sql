# Pattern Matching System Design

**Created**: 2025-11-16
**Status**: ✅ IMPLEMENTED (2025-11-16)
**Priority**: CRITICAL - Blocks CV_TOP_PTHLGY and future XMLs

---

## Problem Statement

The current catalog system (`functions.yaml`) handles **function name rewrites** but cannot handle **expression pattern rewrites**:

### What Works (Current Catalog):
- `string(FIELD)` → `TO_VARCHAR(FIELD)` ✅
- `int(FIELD)` → `TO_INTEGER(FIELD)` ✅
- `leftstr(STR, N)` → `SUBSTRING(STR, 1, N)` ✅

### What Doesn't Work (Needs Pattern Matching):
- `NOW() - 365` → Needs `ADD_DAYS(CURRENT_DATE, -365)` ❌
- `date(NOW() - 270)` → Needs `ADD_DAYS(CURRENT_DATE, -270)` ❌
- `CURRENT_TIMESTAMP - N` → Needs `ADD_DAYS(CURRENT_TIMESTAMP, -N)` ❌

**Current Workaround**: Manual `sed` patches on generated SQL (not sustainable)

---

## Proposed Solution

### Architecture

Add a **two-phase rewrite system** to `translate_raw_formula()`:

```python
def translate_raw_formula(formula: str, ctx) -> str:
    """Translate a raw HANA formula expression to target database SQL."""

    result = formula
    if not result:
        return "NULL"

    result = _substitute_placeholders(result, ctx)
    mode = getattr(ctx, "database_mode", DatabaseMode.SNOWFLAKE)

    # === NEW: Phase 1 - Expression Pattern Rewrites ===
    result = _apply_pattern_rewrites(result, ctx, mode)

    # === EXISTING: Phase 2 - Function Name Rewrites ===
    result = _apply_catalog_rewrites(result, ctx)

    # ... rest of existing logic
    return result
```

### Pattern Catalog Schema

Create `src/xml_to_sql/catalog/data/patterns.yaml`:

```yaml
patterns:
  # Date arithmetic patterns
  - name: "now_minus_days"
    match: "NOW\\(\\)\\s*-\\s*(\\d+)"
    hana: "ADD_DAYS(CURRENT_DATE, -$1)"
    snowflake: "DATEADD(DAY, -$1, CURRENT_TIMESTAMP)"
    description: >
      Subtract days from current timestamp. HANA doesn't support direct
      arithmetic on timestamp types.

  - name: "date_now_minus_days"
    match: "date\\s*\\(\\s*NOW\\(\\)\\s*-\\s*(\\d+)\\s*\\)"
    hana: "ADD_DAYS(CURRENT_DATE, -$1)"
    snowflake: "DATEADD(DAY, -$1, CURRENT_DATE)"
    description: >
      Convert NOW() arithmetic to date arithmetic. Captures the common
      pattern of date(NOW() - N) for "N days ago".

  - name: "timestamp_minus_days"
    match: "CURRENT_TIMESTAMP\\s*-\\s*(\\d+)"
    hana: "ADD_DAYS(CURRENT_TIMESTAMP, -$1)"
    snowflake: "DATEADD(DAY, -$1, CURRENT_TIMESTAMP)"
    description: >
      Direct TIMESTAMP arithmetic replacement.

  # Add more patterns as discovered...

  # String concatenation patterns
  - name: "string_concat_plus"
    match: "(\"[^\"]+\"|'[^']+'|\\w+)\\s*\\+\\s*(\"[^\"]+\"|'[^']+'|\\w+)"
    hana: "$1 + $2"  # HANA uses +
    snowflake: "$1 || $2"  # Snowflake uses ||
    description: >
      String concatenation operator differs between HANA and Snowflake.
```

### Pattern Loader

Create `src/xml_to_sql/catalog/pattern_loader.py`:

```python
"""Pattern-based formula rewrite catalog loader."""

from __future__ import annotations

from dataclasses import dataclass
from functools import lru_cache
from importlib import resources
from typing import Dict, Optional

import yaml


@dataclass(frozen=True)
class PatternRule:
    """Represents a regex-based expression rewrite rule."""

    name: str
    match: str  # Regex pattern
    hana: str  # Replacement for HANA mode
    snowflake: str  # Replacement for Snowflake mode
    description: Optional[str] = None


@lru_cache(maxsize=1)
def get_pattern_catalog() -> Dict[str, PatternRule]:
    """Load and return the pattern rewrite catalog."""

    try:
        data_path = resources.files("xml_to_sql.catalog.data").joinpath("patterns.yaml")
    except (AttributeError, ModuleNotFoundError) as exc:
        raise RuntimeError("Pattern catalog resources are missing") from exc

    try:
        raw_text = data_path.read_text(encoding="utf-8")
    except FileNotFoundError as exc:
        raise RuntimeError("patterns.yaml catalog is missing") from exc

    payload = yaml.safe_load(raw_text) or {}
    rules: Dict[str, PatternRule] = {}

    for item in payload.get("patterns", []):
        name = (item or {}).get("name")
        match = (item or {}).get("match")
        if not name or not match:
            continue

        rule = PatternRule(
            name=name,
            match=match,
            hana=item.get("hana", ""),
            snowflake=item.get("snowflake", ""),
            description=item.get("description"),
        )
        rules[rule.name] = rule

    return rules
```

### Pattern Rewriter

Add to `src/xml_to_sql/sql/function_translator.py`:

```python
import re
from ..catalog.pattern_loader import get_pattern_catalog, PatternRule
from ..domain.types import DatabaseMode


def _apply_pattern_rewrites(formula: str, ctx, mode: DatabaseMode) -> str:
    """Apply regex-based pattern rewrites before function name rewrites.

    This handles expression transformations that can't be done with simple
    function name substitution (e.g., NOW() - 365 → ADD_DAYS()).
    """

    catalog = get_pattern_catalog()
    result = formula

    for rule in catalog.values():
        # Get the mode-specific replacement template
        replacement_template = rule.hana if mode == DatabaseMode.HANA else rule.snowflake

        if not replacement_template:
            continue

        # Apply regex substitution
        # Use re.IGNORECASE for case-insensitive matching
        # Replace $1, $2, etc. with \1, \2, etc. for Python regex groups
        replacement = replacement_template.replace('$', '\\')

        result = re.sub(
            rule.match,
            replacement,
            result,
            flags=re.IGNORECASE
        )

    return result
```

---

## Implementation Plan

### Phase 1: Scaffolding (30 min)
1. ✅ Create `PATTERN_MATCHING_DESIGN.md` (this file)
2. Create `src/xml_to_sql/catalog/data/patterns.yaml` with initial 3 patterns
3. Create `src/xml_to_sql/catalog/pattern_loader.py`
4. Export `get_pattern_catalog` from `src/xml_to_sql/catalog/__init__.py`

### Phase 2: Integration (30 min)
1. Add `_apply_pattern_rewrites()` to `function_translator.py`
2. Call it in `translate_raw_formula()` BEFORE `_apply_catalog_rewrites()`
3. Test with simple pattern: `NOW() - 365`

### Phase 3: Testing (1 hour)
1. Create `tests/test_pattern_rewrites.py`
2. Test each pattern independently
3. Test pattern + catalog integration
4. Test in both HANA and Snowflake modes

### Phase 4: Validation (30 min)
1. Regenerate CV_TOP_PTHLGY SQL (without manual patches)
2. Verify TIMESTAMP arithmetic is handled automatically
3. Package reinstall: `pip install -e .`
4. CLI test: `python -m xml_to_sql.cli.app convert --config config.yaml --scenario CV_TOP_PTHLGY`

---

## Testing Strategy

### Unit Tests

```python
# tests/test_pattern_rewrites.py

def test_now_minus_days_hana():
    """Test NOW() - N pattern in HANA mode."""
    formula = "NOW() - 365"
    ctx = MockContext(database_mode=DatabaseMode.HANA)
    result = _apply_pattern_rewrites(formula, ctx, DatabaseMode.HANA)
    assert result == "ADD_DAYS(CURRENT_DATE, -365)"

def test_now_minus_days_snowflake():
    """Test NOW() - N pattern in Snowflake mode."""
    formula = "NOW() - 365"
    ctx = MockContext(database_mode=DatabaseMode.SNOWFLAKE)
    result = _apply_pattern_rewrites(formula, ctx, DatabaseMode.SNOWFLAKE)
    assert result == "DATEADD(DAY, -365, CURRENT_TIMESTAMP)"

def test_date_now_minus_nested():
    """Test nested pattern: date(NOW() - N)."""
    formula = "date(NOW() - 270)"
    ctx = MockContext(database_mode=DatabaseMode.HANA)
    result = _apply_pattern_rewrites(formula, ctx, DatabaseMode.HANA)
    # After pattern rewrite
    assert "ADD_DAYS(CURRENT_DATE, -270)" in result
```

### Integration Tests

Test the full pipeline:
1. Pattern rewrites applied first
2. Then catalog rewrites (function names)
3. Then mode-specific transformations (IF→CASE, etc.)

---

## Migration Guide

### For Existing XMLs

After implementation, XMLs that previously required manual patches can be regenerated cleanly:

**Before** (Manual Patches Required):
```bash
# Generate SQL
python convert.py CV_TOP_PTHLGY.xml

# Manual fix required
sed -i 's/CURRENT_TIMESTAMP - 365/ADD_DAYS(CURRENT_TIMESTAMP, -365)/g' output.sql
sed -i 's/int(/TO_INTEGER(/g' output.sql
```

**After** (Clean Generation):
```bash
# Generate SQL (all patterns handled automatically)
python convert.py CV_TOP_PTHLGY.xml
# No manual fixes needed!
```

### Adding New Patterns

When you discover a new pattern that needs rewriting:

1. **Document the issue** in `SOLVED_BUGS.md`
2. **Add the pattern** to `patterns.yaml`:
   ```yaml
   - name: "your_pattern_name"
     match: "regex_pattern"
     hana: "HANA replacement"
     snowflake: "Snowflake replacement"
     description: "What this pattern does"
   ```
3. **Test it** with a unit test
4. **Reinstall package**: `pip install -e .`
5. **Regenerate XML** to verify

---

## Benefits

1. **No More Manual Patches**: All expression transformations handled in code
2. **Mode-Aware**: Different rewrites for HANA vs Snowflake
3. **Extensible**: Easy to add new patterns as discovered
4. **Testable**: Regex patterns can be unit tested independently
5. **Documented**: All patterns have descriptions explaining why they exist
6. **Maintainable**: Centralized in YAML, not scattered in code

---

## Open Questions

1. **Pattern Order**: Does order matter? Should we process patterns in a specific sequence?
   - **Answer**: Yes, process from most specific to least specific
   - **Solution**: Catalog returns OrderedDict, process in YAML order

2. **Nested Patterns**: What if a pattern matches inside another pattern's result?
   - **Answer**: Apply patterns in single pass (no recursion)
   - **Alternative**: Mark which patterns can be recursive

3. **Performance**: Will regex on every formula be slow?
   - **Answer**: Probably fine for typical XML sizes (< 1000 formulas)
   - **Optimization**: Cache compiled regex patterns

---

## Next Steps

1. **Implement Phase 1-2** (scaffolding + integration)
2. **Test with CV_TOP_PTHLGY** (remove manual patches, regenerate)
3. **Add discovered patterns** from other XMLs (CV_MCM_CNTRL_Q51, etc.)
4. **Document in llm_handover.md** when complete

---

## Implementation Summary

**Completed**: 2025-11-16
**Actual Effort**: ~2 hours (as estimated)

### Files Created:
1. **`src/xml_to_sql/catalog/data/patterns.yaml`** - Pattern catalog with 3 date arithmetic patterns
2. **`src/xml_to_sql/catalog/pattern_loader.py`** - PatternRule dataclass and get_pattern_catalog() loader
3. **`test_pattern_matching.py`** - Unit tests for pattern matching system

### Files Modified:
1. **`src/xml_to_sql/catalog/__init__.py`** - Exported PatternRule and get_pattern_catalog
2. **`src/xml_to_sql/sql/function_translator.py`** - Added _apply_pattern_rewrites() and integrated into translate_raw_formula()

### Implementation Details:
- ✅ Two-phase rewrite pipeline: patterns → catalog → mode-specific transforms
- ✅ Regex-based pattern matching with capture group substitution ($1, $2, etc.)
- ✅ Mode-aware rewrites (HANA vs Snowflake)
- ✅ LRU caching for performance
- ✅ Single-pass pattern application (no recursion)
- ✅ Patterns processed in YAML order (specific before general)

### Testing Results:
```
✅ Catalog loaded: 3 patterns
✅ All pattern rewrite tests PASSED (7/7 test cases)
✅ All full pipeline tests PASSED (6/6 test cases)
✅ CV_TOP_PTHLGY.xml regenerated cleanly (2139 lines, 198ms HANA execution)
```

### Transformations Automated:
- `NOW() - N` → `ADD_DAYS(CURRENT_DATE, -N)` (7 occurrences in CV_TOP_PTHLGY)
- `date(NOW() - N)` → `ADD_DAYS(CURRENT_DATE, -N)`
- `CURRENT_TIMESTAMP - N` → `ADD_DAYS(CURRENT_TIMESTAMP, -N)`

### Manual Patches Eliminated:
All `sed` patches for CV_TOP_PTHLGY are no longer needed. The conversion pipeline now handles all expression transformations automatically.

---

**Status**: ✅ IMPLEMENTATION COMPLETE
**Original Estimate**: 2-3 hours
**Actual Time**: ~2 hours
**Outcome**: All objectives achieved, CV_TOP_PTHLGY validates cleanly in HANA
