# Conversion Rules Implementation Plan

**Date**: 2025-11-13  
**Status**: Addressing feedback on rules catalog structure

---

## Summary of Implemented Changes

### ✅ Point 1: Version-Keyed Rules Table

**Addressed**: Created `src/xml_to_sql/catalog/data/conversion_rules.yaml`

**Structure**:
```yaml
rules:
  - rule_id: HANA_1_0_IF_TO_CASE
    target_database: hana
    target_version: ">=1.0"
    source_pattern: "IF(condition, then, else)"
    target_pattern: "CASE WHEN ... END"
    applies_to: conditional
    priority: 40
    description: Full explanation
```

**Key Features**:
- **Database-specific**: Rules tagged with `target_database` (hana, snowflake, databricks)
- **Version-specific**: Rules tagged with `target_version` ("1.0", ">=2.0", etc.)
- **Priority-ordered**: Execution order from 10-80 (10 = first, 80 = last)
- **Empirically validated**: Includes rules discovered through CV_CNCLD_EVNTS.xml testing

**Current Coverage**:
- **HANA 1.0 rules**: 11 rules (IF→CASE, IN→OR, parameter removal, etc.)
- **HANA 2.0+ rules**: 2 rules (LEFTSTR/RIGHTSTR modernization)
- **Snowflake rules**: 5 rules (IF→IFF, legacy function conversions, etc.)

**Example Rules**:
| Rule ID | Database | Version | Transformation |
|---------|----------|---------|----------------|
| HANA_1_0_IF_TO_CASE | hana | >=1.0 | IF() → CASE WHEN |
| HANA_1_0_IN_TO_OR | hana | >=1.0 | IN (...) → OR conditions |
| HANA_1_0_LEFTSTR_PRESERVE | hana | 1.0 | Keep LEFTSTR as-is |
| HANA_2_0_LEFTSTR_MODERNIZE | hana | >=2.0 | LEFTSTR → SUBSTRING |
| SNOWFLAKE_IF_TO_IFF | snowflake | >=1.0 | IF() → IFF() |

### ✅ Point 2: Rules Table Used by Tool

**Current Status**: Partially implemented

**What's Already Using Rules**:
- `src/xml_to_sql/catalog/data/functions.yaml` - Function-level rewrites (LEFTSTR, RIGHTSTR, IN, MATCH, LPAD)
- `src/xml_to_sql/catalog/loader.py` - Loads function catalog
- `src/xml_to_sql/sql/function_translator.py` - Applies catalog rewrites

**What's Hardcoded** (needs migration to rules table):
- IF→CASE conversion (`_convert_if_to_case_for_hana()`)
- IN→OR conversion (`_convert_in_to_or_for_hana()`)
- String concatenation (`_translate_string_concat_to_hana()`)
- Subquery wrapping logic (in `_render_projection()`)
- Column qualification logic (in `_render_projection()`)
- Parameter removal (`_substitute_placeholders()`)

**Proposed Enhancement**:
Create `src/xml_to_sql/catalog/rules_engine.py` to:
1. Load `conversion_rules.yaml`
2. Match rules by database + version
3. Apply rules in priority order
4. Replace hardcoded logic with rule-driven transformations

**Benefits**:
- ✅ Easy to add new database targets (just add YAML rules)
- ✅ Version-specific rules without code changes
- ✅ Clear audit trail of transformations
- ✅ User-visible transformation steps

### ✅ Point 3: Conversion Steps Presented to User

**Current Implementation**:
- ✅ Web UI tracks conversion stages (`ConversionStage` model)
- ✅ Stages displayed in UI (SqlPreview component)
- ✅ Current stages:
  1. Parse XML
  2. Build IR
  3. Generate SQL (now includes database_mode, hana_version, xml_format)
  4. Validate SQL
  5. Auto-Correct (if enabled)

**Enhanced for HANA Mode** (just implemented):
- Stage 3 (Generate SQL) now includes:
  - `database_mode`: "hana" or "snowflake"
  - `hana_version`: "1.0", "2.0", etc.
  - `xml_format`: "column_view" or "calculation_scenario"

**Proposed Enhancement** (for later):
Add detailed transformation substages:
```json
{
  "stage_name": "Generate SQL",
  "substages": [
    {
      "name": "Apply Catalog Rewrites",
      "rules_applied": ["in() → IN", "leftstr() → LEFTSTR"],
      "duration_ms": 2
    },
    {
      "name": "Uppercase IF",
      "rules_applied": ["if( → IF("],
      "duration_ms": 1
    },
    {
      "name": "Convert IN to OR",
      "rules_applied": ["HANA_1_0_IN_TO_OR"],
      "transformations_count": 12,
      "duration_ms": 5
    },
    {
      "name": "Convert IF to CASE WHEN",
      "rules_applied": ["HANA_1_0_IF_TO_CASE"],
      "transformations_count": 12,
      "duration_ms": 8
    },
    {
      "name": "Expand Calculated Columns",
      "rules_applied": ["HANA_1_0_CALC_COL_EXPANSION"],
      "expansions": ["CALMONTH in CALQUARTER"],
      "duration_ms": 3
    },
    {
      "name": "Wrap Subqueries",
      "rules_applied": ["HANA_1_0_SUBQUERY_WRAP"],
      "ctes_wrapped": ["ctleqr", "ctleqa", "ctleqm"],
      "duration_ms": 2
    },
    {
      "name": "Qualify Columns",
      "rules_applied": ["HANA_1_0_COLUMN_QUALIFICATION"],
      "qualifications_count": 48,
      "duration_ms": 3
    },
    {
      "name": "Remove Parameters",
      "rules_applied": ["HANA_1_0_PARAMETER_REMOVAL"],
      "parameters_removed": ["$$IP_TREAT_DATE$$", "$$IP_CALMONTH$$", ...],
      "duration_ms": 2
    }
  ]
}
```

---

## Implementation Roadmap

### Phase 1: Document Current State ✅ COMPLETE
- [x] Create `HANA_MODE_CONVERSION_RULES.md` with all rules
- [x] Create `conversion_rules.yaml` with structured rules
- [x] Update `FEATURE_SUPPORT_MAP.md` with HANA transformation summary
- [x] Enhance conversion stages with mode/version info

### Phase 2: Rules Engine (Future)
- [ ] Create `src/xml_to_sql/catalog/rules_engine.py`
- [ ] Implement rule matcher (by database + version)
- [ ] Implement rule applier (priority-ordered execution)
- [ ] Migrate hardcoded logic to rules engine
- [ ] Add rule execution tracking

### Phase 3: Enhanced UI Display (Future)
- [ ] Add transformation substages to `ConversionStage` model
- [ ] Track which rules were applied in each substage
- [ ] Display substages in UI (expandable tree view)
- [ ] Show before/after for each transformation
- [ ] Add transformation count metrics

### Phase 4: User-Editable Rules (Future)
- [ ] UI for viewing conversion rules
- [ ] UI for enabling/disabling specific rules
- [ ] Custom rule priority ordering
- [ ] Import/export custom rule sets

---

## Current Architecture

### Rules Application Flow

**Current** (v2.3.0):
```
XML → Parser → IR → Renderer (calls function_translator) → SQL
                              ↓
                        Hardcoded transformations:
                        1. Catalog rewrites
                        2. Uppercase IF
                        3. IN → OR
                        4. IF → CASE
                        5. String concat
                        6. Column refs
                        7. Calc col expansion
                        8. Subquery wrap
                        9. Column qualification
                        10. Parameter removal
```

**Proposed** (Future):
```
XML → Parser → IR → Renderer (calls rules_engine) → SQL
                              ↓
                        Rules Engine:
                        1. Load conversion_rules.yaml
                        2. Filter rules by database + version
                        3. Sort by priority
                        4. Apply each rule in order
                        5. Track transformations
                        6. Return transformed SQL + metadata
```

---

## Files Structure

### Existing
- `src/xml_to_sql/catalog/data/functions.yaml` - Function-level catalog (basic)
- `src/xml_to_sql/catalog/loader.py` - Catalog loader

### New
- `src/xml_to_sql/catalog/data/conversion_rules.yaml` - **NEW** - Complete rules catalog
- `HANA_MODE_CONVERSION_RULES.md` - **NEW** - Human-readable rules documentation

### To Create (Future)
- `src/xml_to_sql/catalog/rules_engine.py` - Rule matching and application engine
- `src/xml_to_sql/catalog/transformation_tracker.py` - Track which rules were applied

---

## Benefits of Rules-Driven Approach

1. **Maintainability**: Rules in YAML, not scattered in code
2. **Traceability**: Each transformation tracked and auditable
3. **Extensibility**: Add new databases by adding YAML rules
4. **User Control**: Users can enable/disable specific rules
5. **Documentation**: YAML serves as living documentation
6. **Testing**: Test rules individually, not entire pipelines
7. **UI Integration**: Rules metadata displayed to users

---

## Next Steps

1. **Continue empirical testing** with remaining XMLs (use current implementation)
2. **Document new rules** as discovered through testing
3. **Plan rules engine** implementation (Phase 2)
4. **Design enhanced UI** for transformation display (Phase 3)

---

**Status**: Point 1 ✅ Complete, Point 2 ✅ Partially Complete (foundation laid), Point 3 ✅ Enhanced (mode info now tracked)

