#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Test script to verify STRING -> TO_VARCHAR conversion."""

import sys
import os
from pathlib import Path

# Fix Windows console encoding
if sys.platform == 'win32':
    os.system('chcp 65001 > nul')
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')

# Test the catalog directly
print("=== Testing Catalog ===")
from src.xml_to_sql.catalog import get_function_catalog
catalog = get_function_catalog()
print(f"Catalog loaded: {len(catalog)} functions")
print(f"STRING in catalog: {'STRING' in catalog}")
if 'STRING' in catalog:
    rule = catalog['STRING']
    print(f"STRING rule: handler={rule.handler}, target={rule.target}")

# Test the rewrite function
print("\n=== Testing Rewrite Function ===")
from src.xml_to_sql.sql.function_translator import _apply_catalog_rewrites

class MockContext:
    database_mode = None

ctx = MockContext()
test_cases = [
    'string("RANK_COLUMN")',
    'leftstr(string(date(NOW() - 365)),4)',
    'string(TO_DATE(CURRENT_TIMESTAMP - 365))'
]

for test in test_cases:
    result = _apply_catalog_rewrites(test, ctx)
    print(f"  {test}")
    print(f"  -> {result}")
    print()

# Test a full conversion
print("=== Testing Full Conversion ===")
from src.xml_to_sql.parser.scenario_parser import parse_scenario
from src.xml_to_sql.sql.renderer import render_scenario
from src.xml_to_sql.domain.types import DatabaseMode

xml_path = Path("Source (XML Files)/HANA 1.XX XML Views/BW_ON_HANA/CV_TOP_PTHLGY.xml")

if not xml_path.exists():
    print(f"ERROR: XML file not found: {xml_path}")
    sys.exit(1)

print(f"Parsing XML from: {xml_path}")
scenario = parse_scenario(xml_path)

print(f"Rendering SQL in HANA mode with ABAP->SAPABAP1 schema override...")
schema_overrides = {"ABAP": "SAPABAP1"}
sql, warnings = render_scenario(scenario, schema_overrides=schema_overrides, database_mode=DatabaseMode.HANA, validate=False, return_warnings=True)

# Save SQL to file for inspection
output_path = Path("test_output.sql")
output_path.write_text(sql, encoding='utf-8')
print(f"\nSQL saved to: {output_path}")

# Check for string() in output (exact match, not substring)
import re
# Use word boundary to avoid matching substring in SUBSTRING
if re.search(r'\bstring\s*\(', sql, re.IGNORECASE):
    print("\n❌ FAILED: string() still present in output!")
    matches = re.findall(r'\bstring\s*\([^)]+\)', sql, re.IGNORECASE)
    print(f"Found {len(matches)} occurrences:")
    for i, match in enumerate(matches[:5], 1):
        print(f"  {i}. {match}")
else:
    print("\n✅ SUCCESS: No string() calls in output!")

# Check for TO_VARCHAR
if 'TO_VARCHAR' in sql:
    print(f"✅ TO_VARCHAR found in output")
    import re
    matches = re.findall(r'TO_VARCHAR\([^)]+\)', sql)
    print(f"Found {len(matches)} occurrences:")
    for i, match in enumerate(matches[:5], 1):
        print(f"  {i}. {match}")
else:
    print("❌ TO_VARCHAR not found in output")

print("\nDone!")
