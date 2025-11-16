#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Test pattern matching system implementation."""

import sys
import os
from pathlib import Path

# Fix Windows console encoding
if sys.platform == 'win32':
    os.system('chcp 65001 > nul')
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')

print("=" * 70)
print("PATTERN MATCHING SYSTEM TEST")
print("=" * 70)

# Test 1: Pattern Catalog Loading
print("\n=== Test 1: Pattern Catalog Loading ===")
try:
    from src.xml_to_sql.catalog import get_pattern_catalog
    catalog = get_pattern_catalog()
    print(f"✅ Catalog loaded: {len(catalog)} patterns")
    for name, rule in catalog.items():
        print(f"  - {name}: {rule.match[:50]}...")
except Exception as e:
    print(f"❌ FAILED: {e}")
    sys.exit(1)

# Test 2: Pattern Rewrite Function
print("\n=== Test 2: Pattern Rewrite Function ===")
try:
    from src.xml_to_sql.sql.function_translator import _apply_pattern_rewrites
    from src.xml_to_sql.domain.types import DatabaseMode

    class MockContext:
        database_mode = DatabaseMode.HANA

    ctx = MockContext()

    test_cases = [
        ("NOW() - 365", "ADD_DAYS(CURRENT_DATE, -365)"),
        ("NOW() -365", "ADD_DAYS(CURRENT_DATE, -365)"),  # No space
        ("now() - 270", "ADD_DAYS(CURRENT_DATE, -270)"),  # Lowercase
        ("date(NOW() - 365)", "ADD_DAYS(CURRENT_DATE, -365)"),
        ("date(NOW() - 270)", "ADD_DAYS(CURRENT_DATE, -270)"),
        ("CURRENT_TIMESTAMP - 365", "ADD_DAYS(CURRENT_TIMESTAMP, -365)"),
        ("CURRENT_TIMESTAMP -100", "ADD_DAYS(CURRENT_TIMESTAMP, -100)"),
    ]

    all_passed = True
    for input_formula, expected in test_cases:
        result = _apply_pattern_rewrites(input_formula, ctx, DatabaseMode.HANA)
        if result == expected:
            print(f"✅ {input_formula:30} → {result}")
        else:
            print(f"❌ {input_formula:30} → {result}")
            print(f"   Expected: {expected}")
            all_passed = False

    if all_passed:
        print("\n✅ All pattern rewrite tests PASSED!")
    else:
        print("\n❌ Some pattern rewrite tests FAILED!")
        sys.exit(1)

except Exception as e:
    print(f"❌ FAILED: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

# Test 3: Integration with Full Pipeline
print("\n=== Test 3: Full Translation Pipeline ===")
try:
    from src.xml_to_sql.sql.function_translator import translate_raw_formula

    test_formulas = [
        # Pattern + Catalog rewrites
        ("NOW() - 365", "ADD_DAYS(CURRENT_DATE, -365)"),
        ("string(NOW() - 365)", "TO_VARCHAR(ADD_DAYS(CURRENT_DATE, -365))"),
        ("int(NOW() - 270)", "TO_INTEGER(ADD_DAYS(CURRENT_DATE, -270))"),

        # Just catalog rewrites (no pattern match)
        ("string(FIELD)", "TO_VARCHAR(FIELD)"),
        ("int(VALUE)", "TO_INTEGER(VALUE)"),
        ("adddays(DATE, -3)", "ADD_DAYS(DATE, -3)"),
    ]

    all_passed = True
    for input_formula, expected_contains in test_formulas:
        result = translate_raw_formula(input_formula, ctx)
        # For full pipeline, we just check if key transformations are present
        # (since other transformations might be applied too)
        if expected_contains in result:
            print(f"✅ {input_formula:35} → {result}")
        else:
            print(f"❌ {input_formula:35} → {result}")
            print(f"   Expected to contain: {expected_contains}")
            all_passed = False

    if all_passed:
        print("\n✅ All full pipeline tests PASSED!")
    else:
        print("\n❌ Some full pipeline tests FAILED!")
        sys.exit(1)

except Exception as e:
    print(f"❌ FAILED: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

print("\n" + "=" * 70)
print("🎉 ALL TESTS PASSED!")
print("=" * 70)
print("\nPattern matching system is working correctly!")
print("Next step: Reinstall package and regenerate CV_TOP_PTHLGY.xml")
