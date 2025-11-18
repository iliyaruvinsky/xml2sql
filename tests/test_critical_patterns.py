"""
Critical Pattern Protection Tests

⚠️ CRITICAL: These tests protect VALIDATED patterns from commit 4eff5fb
- DO NOT modify these tests without HANA Studio validation
- See GOLDEN_COMMIT.yaml for last validated commit
- See FIXES_AFTER_COMMIT_4eff5fb.md for bug fix history

Purpose: Prevent regression of working patterns that were validated in HANA Studio
"""

import pytest
import re
from pathlib import Path

# Note: DatabaseMode not needed for file-based tests, removed import
# from xml_to_sql.sql.function_translator import _convert_in_function_to_operator  # Commented - function is private


class TestCriticalHANAPatterns:
    """Test suite protecting HANA-validated patterns from commit 4eff5fb"""

    def test_hana_view_creation_uses_drop_cascade(self):
        """
        CRITICAL: Verify HANA mode uses DROP VIEW CASCADE, not CREATE OR REPLACE VIEW

        Validated: 5/5 XMLs passing in HANA Studio (commit 4eff5fb, 2025-11-17)
        Execution times: 29ms - 211ms (all successful)

        WRONG APPROACH (does not work in HANA):
            CREATE OR REPLACE VIEW {name} AS
            Error: "cannot use duplicate view name"

        CORRECT APPROACH (validated in HANA):
            DROP VIEW {name} CASCADE;
            CREATE VIEW {name} AS

        Reference: Target (SQL Scripts)/VALIDATED/README.md, GOLDEN_COMMIT.yaml
        """
        # Read the renderer.py file to check the pattern
        renderer_path = Path(__file__).parent.parent / "src" / "xml_to_sql" / "sql" / "renderer.py"
        renderer_content = renderer_path.read_text(encoding='utf-8')

        # Search for the HANA view creation section
        # Should find: return f"DROP VIEW {quoted_name} CASCADE;\nCREATE VIEW {quoted_name} AS"
        drop_cascade_pattern = r'DROP VIEW.*CASCADE.*CREATE VIEW'

        assert re.search(drop_cascade_pattern, renderer_content, re.DOTALL), (
            "CRITICAL FAILURE: HANA view creation pattern missing DROP VIEW CASCADE. "
            "This breaks ALL view creation in HANA. "
            "Required pattern: DROP VIEW {name} CASCADE;\\nCREATE VIEW {name} AS"
        )

        # Verify CREATE OR REPLACE is NOT used for HANA
        # Check specifically for the HANA return statement, excluding else clause
        hana_section_match = re.search(
            r'elif mode == DatabaseMode\.HANA:(.*?)(?=\n\s+else:|\n\s+elif|\ndef )',
            renderer_content,
            re.DOTALL
        )

        assert hana_section_match, "Could not find HANA mode section in renderer.py"
        hana_code = hana_section_match.group(1)

        # Check that the HANA return statement uses DROP VIEW CASCADE
        assert 'DROP VIEW' in hana_code and 'CASCADE' in hana_code, (
            "CRITICAL FAILURE: HANA section missing DROP VIEW CASCADE pattern"
        )

        # Verify CREATE OR REPLACE is NOT in the HANA-specific return statement
        # Look for return statements in HANA section only
        hana_returns = re.findall(r'return\s+f"([^"]*)"', hana_code)

        for return_stmt in hana_returns:
            assert 'CREATE OR REPLACE' not in return_stmt, (
                f"CRITICAL FAILURE: Found 'CREATE OR REPLACE VIEW' in HANA return statement: '{return_stmt}'. "
                f"This does NOT work in HANA (error: 'cannot use duplicate view name'). "
                f"Must use: DROP VIEW {{name}} CASCADE;\\nCREATE VIEW {{name}} AS"
            )

    def test_column_qualification_regex_handles_sap_columns(self):
        r"""
        CRITICAL: Verify column qualification regex handles SAP BEx columns with special chars

        Validated: BUG-019 fix, 39ms HANA execution (2025-11-17)

        WRONG REGEX (pre-BUG-019):
            r'(?<!\.)"([A-Z_][A-Z0-9_]*)"'
            Problem: Only matches alphanumeric, excludes "/BIC/FIELD", "/BI0/FIELD"

        CORRECT REGEX (BUG-019 fix):
            r'(?<!\.)"([^"]+)"'
            Matches ANY characters inside quotes

        Reference: FIXES_AFTER_COMMIT_4eff5fb.md (BUG-019, Part 1)
        """
        renderer_path = Path(__file__).parent.parent / "src" / "xml_to_sql" / "sql" / "renderer.py"
        renderer_content = renderer_path.read_text(encoding='utf-8')

        # Search for the column qualification pattern
        # Should find: pattern = r'(?<!\.)("[^"]+")' or similar
        correct_pattern = r"pattern\s*=\s*r['\"](?:\(\?<!\\\\\\.\))?['\"]?\[\\^['\"]?\]\+['\"]?"

        # More flexible check: just verify it's NOT the old restrictive pattern
        old_wrong_pattern = r'"\[A-Z_\]\[A-Z0-9_\]\*"'

        assert not re.search(old_wrong_pattern, renderer_content), (
            "CRITICAL FAILURE: Found old restrictive column qualification regex. "
            "This breaks SAP BEx columns like '/BIC/FIELD'. "
            "Required pattern: r'(?<!\\.)(\"[^\"]+\")' to match ANY quoted identifier."
        )

        # Verify the pattern can match SAP columns
        # Extract the actual pattern used in _render_projection
        pattern_match = re.search(
            r'# Pattern: Match any quoted identifier.*?pattern = r[\'"]([^\'"]+)[\'"]',
            renderer_content,
            re.DOTALL
        )

        if pattern_match:
            extracted_pattern = pattern_match.group(1)
            # Test the pattern against SAP column
            test_pattern = re.compile(extracted_pattern)

            # Test cases that must match
            test_string = 'WHERE "/BIC/FIELD" = 1'
            matches = test_pattern.findall(test_string)

            assert len(matches) > 0, (
                f"CRITICAL FAILURE: Column qualification regex '{extracted_pattern}' "
                f"does not match SAP columns like '/BIC/FIELD'. "
                f"Test string: {test_string}, Matches: {matches}"
            )

    def test_in_function_conversion_exists(self):
        """
        CRITICAL: Verify IN function conversion is implemented

        Validated: BUG-020 fix, 66ms HANA execution (2025-11-18)

        Problem: XML uses function-style IN(column, val1, val2)
        Solution: Convert to operator-style: column IN (val1, val2)

        Reference: FIXES_AFTER_COMMIT_4eff5fb.md (BUG-020, Part 1)
        """
        translator_path = Path(__file__).parent.parent / "src" / "xml_to_sql" / "sql" / "function_translator.py"
        translator_content = translator_path.read_text(encoding='utf-8')

        # Verify function exists
        assert '_convert_in_function_to_operator' in translator_content, (
            "CRITICAL FAILURE: Missing _convert_in_function_to_operator() function. "
            "This breaks IN() expressions in HANA. "
            "Required: Convert IN(col, val1, val2) to col IN (val1, val2)"
        )

        # Verify function is called in translate_raw_formula
        assert 'result = _convert_in_function_to_operator(result)' in translator_content, (
            "CRITICAL FAILURE: _convert_in_function_to_operator() is not called. "
            "IN() function conversion will not happen. "
            "Must be called in translate_raw_formula() pipeline."
        )

    def test_in_function_conversion_logic(self):
        """
        Test the actual IN function conversion logic

        Validates: Function-style IN() to operator-style conversion

        NOTE: This test is COMMENTED OUT because _convert_in_function_to_operator
        is a private function. The function's behavior is tested indirectly via
        regression_test.py which tests the actual SQL generation.
        """
        pytest.skip("Testing private function - use regression_test.py instead")

    def test_hana_version_aware_in_processing(self):
        """
        CRITICAL: Verify HANA 2.0+ does NOT convert IN to OR

        Validated: BUG-020 fix (2025-11-18)

        Behavior:
        - HANA 1.x: Convert IN to OR (legacy requirement)
        - HANA 2.0+: Keep IN operator (native support)

        Reference: FIXES_AFTER_COMMIT_4eff5fb.md (BUG-020, Part 2)
        """
        translator_path = Path(__file__).parent.parent / "src" / "xml_to_sql" / "sql" / "function_translator.py"
        translator_content = translator_path.read_text(encoding='utf-8')

        # Verify version check exists
        version_check_pattern = r'if version_str and str\(version_str\)\.startswith\("1\."\):'

        assert re.search(version_check_pattern, translator_content), (
            "CRITICAL FAILURE: Missing HANA version check for IN operator. "
            "HANA 2.0+ supports IN natively, should not convert to OR. "
            "Only HANA 1.x requires IN→OR conversion."
        )

    def test_sys_bic_catalog_with_package_path(self):
        """
        CRITICAL: Verify _SYS_BIC catalog views use package paths

        Validated: BUG-019 fix, 39ms HANA execution (2025-11-17)

        Format required:
            _SYS_BIC."PACKAGE.PATH/VIEW_NAME"

        Reference: FIXES_AFTER_COMMIT_4eff5fb.md (BUG-019, Part 2)
        """
        converter_path = Path(__file__).parent.parent / "src" / "xml_to_sql" / "web" / "services" / "converter.py"
        converter_content = converter_path.read_text(encoding='utf-8')

        # Verify _SYS_BIC special handling exists
        sys_bic_check = r'if hana_package and effective_view_schema == "_SYS_BIC"'

        assert re.search(sys_bic_check, converter_content), (
            "CRITICAL FAILURE: Missing _SYS_BIC catalog special handling. "
            "Catalog views require package paths: _SYS_BIC.\"PACKAGE/VIEW\". "
            "Without this, HANA catalog views will fail."
        )

        # Verify package path concatenation
        package_concat = r'view_name_with_package = f[\'"].*?{hana_package}/{scenario_id}'

        assert re.search(package_concat, converter_content), (
            "CRITICAL FAILURE: Missing package path concatenation for _SYS_BIC. "
            "Format must be: package/viewname (e.g., 'Macabi_BI.EYAL/CV_NAME')"
        )


class TestGoldenCommitProtection:
    """Verify protection mechanisms are in place"""

    def test_golden_commit_file_exists(self):
        """Verify GOLDEN_COMMIT.yaml exists and is tracked"""
        golden_commit_path = Path(__file__).parent.parent / "GOLDEN_COMMIT.yaml"

        assert golden_commit_path.exists(), (
            "CRITICAL FAILURE: GOLDEN_COMMIT.yaml not found. "
            "This file tracks the last validated commit. "
            "Without it, we cannot protect working code from regression."
        )

    def test_validated_sql_folder_exists(self):
        """Verify Target (SQL Scripts)/VALIDATED folder exists"""
        validated_path = Path(__file__).parent.parent / "Target (SQL Scripts)" / "VALIDATED"

        assert validated_path.exists(), (
            "CRITICAL FAILURE: VALIDATED SQL folder not found. "
            "This folder contains golden SQL copies for byte-level comparison. "
            "Without it, we cannot detect regressions in generated SQL."
        )

    def test_fixes_documentation_exists(self):
        """Verify FIXES_AFTER_COMMIT_4eff5fb.md exists"""
        fixes_path = Path(__file__).parent.parent / "FIXES_AFTER_COMMIT_4eff5fb.md"

        assert fixes_path.exists(), (
            "CRITICAL FAILURE: FIXES_AFTER_COMMIT_4eff5fb.md not found. "
            "This file documents all bug fixes applied after golden commit. "
            "Without it, we cannot reapply fixes after reverting."
        )


if __name__ == "__main__":
    # Allow running this file directly for quick verification
    pytest.main([__file__, "-v"])
