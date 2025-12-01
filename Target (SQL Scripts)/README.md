# Target (SQL Scripts) - Validated SQL Repository

This folder contains **HANA-validated SQL scripts** and validation tracking.

## Purpose

**CRITICAL**: This folder prevents regressions by maintaining a library of SQL files that are proven to work in HANA. Before making any code changes, compare new output against these validated files to ensure we don't break working conversions.

## Folder Structure

```
Target (SQL Scripts)/
├── README.md                          # This file
├── GOLDEN_COMMIT.yaml                 # Last known good commit
├── REGRESSION_TEST_RESULTS.md         # Quick status dashboard
├── VALIDATION_LOG.md                  # Chronological history
├── VALIDATED/                         # Immutable validated SQL files
│   ├── CV_ELIG_TRANS_01_HANA.sql
│   └── ...
└── PATTERNS/                          # SQL pattern reference
    ├── WORKING_PATTERNS.md
    └── FAILED_PATTERNS.md
```

## Workflow

### 1. Test XML in HANA
- Upload XML to web UI at http://localhost:8000
- Download generated SQL
- Execute SQL in HANA Studio
- Note execution time and any errors/warnings

### 2. Report Results
Provide:
- XML filename
- ✅ Success / ❌ Fail
- Execution time (e.g., "82ms")
- Any HANA errors or warnings
- Any unexpected behavior

### 3. Validation (if successful)
- SQL is copied to `VALIDATED/` folder (immutable)
- `GOLDEN_COMMIT.yaml` is updated with current git commit
- `REGRESSION_TEST_RESULTS.md` is updated with new status
- `VALIDATION_LOG.md` records the session

### 4. Before Next Bug Fix
- Compare new SQL output against files in `VALIDATED/`
- Ensure changes don't deviate from working patterns
- Reference `PATTERNS/WORKING_PATTERNS.md`

### 5. After Bug Fix
- Re-test ALL validated files to catch regressions
- Update status if any previously working files now fail
- Add new patterns to `PATTERNS/` documentation

## Files Explained

### GOLDEN_COMMIT.yaml
Single source of truth for rollback:
- Git commit hash that produced all validated SQLs
- List of validated files
- Bugs fixed in this commit
- Use `git checkout <commit>` if regressions occur

### REGRESSION_TEST_RESULTS.md
Quick status dashboard:
- Table showing all tested XML files
- Current pass/fail status
- Execution times
- Notes about each file

### VALIDATION_LOG.md
Complete chronological history:
- All validation sessions
- Changes made in each session
- Test results
- Regressions found
- Template for future sessions

### VALIDATED/ folder
**IMMUTABLE** - SQL files proven to work:
- NEVER modify these files
- Only add new validated files
- Use for regression testing
- Reference for working SQL syntax

### PATTERNS/ folder
SQL pattern documentation:
- **WORKING_PATTERNS.md**: Proven-working SQL patterns
- **FAILED_PATTERNS.md**: Known failing SQL patterns
- Reference before making changes

## Rules

1. **NEVER modify files in VALIDATED/**
   - These are immutable golden references
   - Only add new files when validated

2. **Always update GOLDEN_COMMIT.yaml**
   - After validating new files
   - Tracks exact code state that produced working SQL

3. **Re-test after every fix**
   - Test ALL previously validated files
   - Catch regressions early

4. **Document everything**
   - Update VALIDATION_LOG.md after each session
   - Add new patterns to PATTERNS/ as discovered

## Example Validation Session

```bash
# User tests CV_ELIG_TRANS_01.xml in HANA
User: "CV_ELIG_TRANS_01 executed successfully in 82ms, no warnings"

# I validate and copy to VALIDATED/
$ cp output/CV_ELIG_TRANS_01_HANA.sql "Target (SQL Scripts)/VALIDATED/"

# I update GOLDEN_COMMIT.yaml
$ git log -1 --format="%H"  # Get current commit
$ edit GOLDEN_COMMIT.yaml   # Add to validated_files list

# I update REGRESSION_TEST_RESULTS.md
| CV_ELIG_TRANS_01 | ✅ PASS | 2025-11-21 | 82ms | - | No issues |

# I update VALIDATION_LOG.md
## Session 1 - 2025-11-21
...
| CV_ELIG_TRANS_01 | ✅ PASS | 82ms | - | No warnings |
```

## Current Status

**Validated Files**: 0
**Last Commit**: e809a4d31677b91c0aa5dbea5648a2b5838a9f6a
**Date**: 2025-11-21

## Next Steps

1. Upload CV_ELIG_TRANS_01.xml in web UI
2. Test generated SQL in HANA Studio
3. Report results
4. Validate and build the repository
