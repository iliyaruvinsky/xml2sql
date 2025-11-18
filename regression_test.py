#!/usr/bin/env python
"""
Regression Testing Script - Compare Generated SQL with Golden Copies

⚠️ CRITICAL: Golden copies are byte-level references from commit 4eff5fb
- See GOLDEN_COMMIT.yaml for tracking
- See Target (SQL Scripts)/VALIDATED/ for golden SQL files

Usage:
    python regression_test.py                    # Normalized comparison (default)
    python regression_test.py --strict           # Byte-level comparison
    python regression_test.py --update-golden    # Update golden copies (requires HANA validation!)
"""
import sys
import argparse
from pathlib import Path
from xml_to_sql.web.services.converter import convert_xml_to_sql
import difflib

# Test cases: (xml_path, validated_sql_path, package_path)
TEST_CASES = [
    (
        "Source (XML Files)/HANA 1.XX XML Views/ECC_ON_HANA/CV_CNCLD_EVNTS.xml",
        "Target (SQL Scripts)/VALIDATED/CV_CNCLD_EVNTS.sql",
        "EYAL.EYAL_CTL"
    ),
    (
        "Source (XML Files)/HANA 1.XX XML Views/BW_ON_HANA/CV_INVENTORY_ORDERS.xml",
        "Target (SQL Scripts)/VALIDATED/CV_INVENTORY_ORDERS.sql",
        "Macabi_BI.EYAL.EYAL_CDS"
    ),
    (
        "Source (XML Files)/HANA 1.XX XML Views/BW_ON_HANA/CV_PURCHASE_ORDERS.xml",
        "Target (SQL Scripts)/VALIDATED/CV_PURCHASE_ORDERS.sql",
        "Macabi_BI.EYAL.EYAL_CDS"
    ),
    (
        "Source (XML Files)/HANA 1.XX XML Views/BW_ON_HANA/CV_EQUIPMENT_STATUSES.xml",
        "Target (SQL Scripts)/VALIDATED/CV_EQUIPMENT_STATUSES.sql",
        "Macabi_BI.EYAL.EYAL_CDS"
    ),
    (
        "Source (XML Files)/HANA 1.XX XML Views/BW_ON_HANA/CV_TOP_PTHLGY.xml",
        "Target (SQL Scripts)/VALIDATED/CV_TOP_PTHLGY.sql",
        "Macabi_BI.EYAL.EYAL_CDS"
    ),
]

def convert_xml(xml_path: str, package_path: str) -> tuple[str, list[str]]:
    """Convert XML to SQL."""
    with open(xml_path, 'rb') as f:
        xml_content = f.read()

    # Convert using the web converter service
    result = convert_xml_to_sql(
        xml_content=xml_content,
        database_mode='hana',
        hana_version='2.0',
        hana_package=package_path,
        view_schema='SAPABAP1',
        schema_overrides={'ABAP': 'SAPABAP1'},
        auto_fix=False
    )

    if result.error:
        raise ValueError(result.error)

    return result.sql_content, result.warnings

def compare_sql_strict(generated: str, validated: str) -> tuple[bool, str, list[str]]:
    """
    Byte-level comparison (strict mode).

    Returns: (is_identical, status_message, diff_lines)
    """
    if generated == validated:
        return True, "✅ IDENTICAL (byte-level)", []

    # Generate detailed diff
    diff = list(difflib.unified_diff(
        validated.splitlines(keepends=True),
        generated.splitlines(keepends=True),
        fromfile="Golden Copy",
        tofile="Generated",
        lineterm=''
    ))

    return False, f"❌ DIFFERENT (byte-level)", diff


def compare_sql_normalized(generated: str, validated: str) -> tuple[bool, str, list[str]]:
    """
    Normalized comparison (ignores whitespace differences).

    Returns: (is_identical, status_message, diff_lines)
    """
    # Normalize whitespace for comparison
    gen_lines = [line.strip() for line in generated.split('\n') if line.strip()]
    val_lines = [line.strip() for line in validated.split('\n') if line.strip()]

    if gen_lines == val_lines:
        return True, "✅ IDENTICAL (normalized)", []

    # Find differences
    diff_count = 0
    diff_lines = []
    for i, (gen_line, val_line) in enumerate(zip(gen_lines, val_lines)):
        if gen_line != val_line:
            diff_count += 1
            if diff_count <= 5:  # Show first 5 differences
                diff_lines.append(f"Line {i+1}:")
                diff_lines.append(f"  Golden:    {val_line[:100]}")
                diff_lines.append(f"  Generated: {gen_line[:100]}")

    if len(gen_lines) != len(val_lines):
        diff_lines.append(f"Line count: {len(val_lines)} vs {len(gen_lines)}")

    return False, f"❌ DIFFERENT ({diff_count} lines differ)", diff_lines

def main():
    """Run regression tests."""
    # Parse command-line arguments
    parser = argparse.ArgumentParser(
        description="Regression test: Compare generated SQL with golden copies"
    )
    parser.add_argument(
        '--strict',
        action='store_true',
        help='Use byte-level comparison instead of normalized comparison'
    )
    parser.add_argument(
        '--update-golden',
        action='store_true',
        help='Update golden copies with newly generated SQL (requires HANA validation!)'
    )
    parser.add_argument(
        '--show-diffs',
        action='store_true',
        help='Show detailed diffs for failed comparisons'
    )

    args = parser.parse_args()

    # Warning for update-golden
    if args.update_golden:
        print("⚠️  WARNING: You are about to update golden SQL copies")
        print("    This should ONLY be done after HANA Studio validation")
        response = input("    Are you sure? (yes/no): ")
        if response.lower() != 'yes':
            print("Aborted.")
            return 1

    print("=" * 80)
    print("REGRESSION TESTING - Validated XML Files")
    print("=" * 80)
    print(f"Comparison mode: {'STRICT (byte-level)' if args.strict else 'NORMALIZED (whitespace-agnostic)'}")
    print(f"Golden commit: 4eff5fb (2025-11-17)")
    print("=" * 80)
    print()

    results = []

    for xml_path, validated_sql_path, package_path in TEST_CASES:
        xml_name = Path(xml_path).name
        print(f"Testing: {xml_name}")
        print(f"  Package: {package_path}")

        try:
            # Convert XML
            generated_sql, warnings = convert_xml(xml_path, package_path)

            # Read validated SQL
            with open(validated_sql_path, 'r', encoding='utf-8') as f:
                validated_sql = f.read()

            # Compare (choose method based on --strict flag)
            if args.strict:
                match, status, diff_lines = compare_sql_strict(generated_sql, validated_sql)
            else:
                match, status, diff_lines = compare_sql_normalized(generated_sql, validated_sql)

            results.append((xml_name, match, status))
            print(f"  Result: {status}")

            # Show diffs if requested and test failed
            if not match and args.show_diffs and diff_lines:
                print("  Differences:")
                for line in diff_lines[:20]:  # Show first 20 lines
                    print(f"    {line}")
                if len(diff_lines) > 20:
                    print(f"    ... {len(diff_lines) - 20} more lines")

            if warnings:
                print(f"  Warnings: {len(warnings)}")

            # Update golden copy if requested
            if args.update_golden:
                print(f"  Updating golden copy: {validated_sql_path}")
                with open(validated_sql_path, 'w', encoding='utf-8') as f:
                    f.write(generated_sql)
                print("  ✅ Golden copy updated")

        except Exception as e:
            results.append((xml_name, False, f"❌ ERROR: {str(e)}"))
            print(f"  Result: ❌ ERROR: {str(e)}")

        print()

    # Summary
    print("=" * 80)
    print("SUMMARY")
    print("=" * 80)

    passed = sum(1 for _, match, _ in results if match)
    total = len(results)

    for xml_name, match, status in results:
        print(f"  {xml_name}: {status}")

    print()
    print(f"PASSED: {passed}/{total} ({passed*100//total if total > 0 else 0}%)")
    print("=" * 80)

    if passed < total:
        print()
        print("⚠️  REGRESSION DETECTED - Generated SQL differs from golden copies")
        print("    1. Review differences with --show-diffs flag")
        print("    2. If changes are intentional and HANA-validated:")
        print("       python regression_test.py --update-golden")
        print("    3. Update GOLDEN_COMMIT.yaml with new commit hash")
        print("    4. Commit both updated SQL files and GOLDEN_COMMIT.yaml")

    return 0 if passed == total else 1

if __name__ == '__main__':
    sys.exit(main())
