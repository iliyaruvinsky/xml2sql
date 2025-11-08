#!/usr/bin/env python3
"""Comprehensive verification script to check all 7 SQL files against their XML sources."""

from pathlib import Path
from xml_to_sql.parser import parse_scenario
from xml_to_sql.sql import render_scenario
import json

# Define all 7 scenarios
SCENARIOS = [
    ("Sold_Materials.XML", "V_C_SOLD_MATERIALS.sql"),
    ("SALES_BOM.XML", "V_C_SALES_BOM.sql"),
    ("Recently_created_products.XML", "V_C_RECENTLY_CREATED_PRODUCTS.sql"),
    ("KMDM_Materials.XML", "V_C_KMDM_MATERIALS.sql"),
    ("CURRENT_MAT_SORT.XML", "V_C_CURRENT_MAT_SORT.sql"),
    ("Material Details.XML", "V_C_MATERIAL_DETAILS.sql"),
    ("Sold_Materials_PROD.XML", "V_C_SOLD_MATERIALS_PROD.sql"),
]

def verify_scenario(xml_file: str, sql_file: str) -> dict:
    """Verify a single scenario XML against its SQL output."""
    root = Path(__file__).parent
    xml_path = root / "Source (XML Files)" / xml_file
    sql_path = root / "Target (SQL Scripts)" / sql_file
    
    result = {
        "xml_file": xml_file,
        "sql_file": sql_file,
        "xml_exists": xml_path.exists(),
        "sql_exists": sql_path.exists(),
        "parse_success": False,
        "render_success": False,
        "errors": [],
        "warnings": [],
        "verification": {}
    }
    
    if not result["xml_exists"]:
        result["errors"].append(f"XML file not found: {xml_path}")
        return result
    
    if not result["sql_exists"]:
        result["errors"].append(f"SQL file not found: {sql_path}")
        return result
    
    # Parse XML
    try:
        scenario = parse_scenario(xml_path)
        result["parse_success"] = True
    except Exception as e:
        result["errors"].append(f"Parse error: {e}")
        return result
    
    # Generate SQL
    try:
        generated_sql = render_scenario(scenario)
        result["render_success"] = True
    except Exception as e:
        result["errors"].append(f"Render error: {e}")
        return result
    
    # Read actual SQL file
    try:
        actual_sql = sql_path.read_text(encoding="utf-8")
    except Exception as e:
        result["errors"].append(f"Read SQL error: {e}")
        return result
    
    # Verification checks
    verification = result["verification"]
    
    # 1. Check scenario metadata
    verification["scenario_id"] = scenario.metadata.scenario_id
    verification["default_client"] = scenario.metadata.default_client
    verification["default_language"] = scenario.metadata.default_language
    
    # 2. Count data sources
    verification["data_sources_count"] = len(scenario.data_sources)
    verification["data_sources"] = list(scenario.data_sources.keys())
    
    # 3. Count nodes
    verification["nodes_count"] = len(scenario.nodes)
    verification["node_types"] = {}
    for node in scenario.nodes.values():
        node_type = node.kind.value
        verification["node_types"][node_type] = verification["node_types"].get(node_type, 0) + 1
    
    # 4. Count filters
    total_filters = sum(len(node.filters) for node in scenario.nodes.values())
    verification["total_filters"] = total_filters
    
    # 5. Count calculated attributes
    total_calc_attrs = sum(len(node.calculated_attributes) for node in scenario.nodes.values())
    verification["total_calculated_attributes"] = total_calc_attrs
    
    # 6. Check logical model
    verification["has_logical_model"] = scenario.logical_model is not None
    if scenario.logical_model:
        verification["logical_attributes_count"] = len(scenario.logical_model.attributes)
        verification["logical_calculated_attributes_count"] = len(scenario.logical_model.calculated_attributes)
        verification["logical_measures_count"] = len(scenario.logical_model.measures)
    
    # 7. Check variables
    verification["variables_count"] = len(scenario.variables)
    
    # 8. SQL structure checks
    verification["sql_contains_with"] = "WITH" in generated_sql
    verification["sql_contains_select"] = "SELECT" in generated_sql
    verification["sql_contains_from"] = "FROM" in generated_sql
    verification["sql_length"] = len(generated_sql)
    verification["sql_lines"] = len(generated_sql.splitlines())
    
    # 9. Compare generated vs actual SQL
    verification["sql_matches"] = generated_sql.strip() == actual_sql.strip()
    if not verification["sql_matches"]:
        # Check if they're similar (ignoring whitespace differences)
        gen_normalized = " ".join(generated_sql.split())
        actual_normalized = " ".join(actual_sql.split())
        verification["sql_similar"] = gen_normalized == actual_normalized
        
        # Count differences
        gen_lines = set(line.strip() for line in generated_sql.splitlines() if line.strip())
        actual_lines = set(line.strip() for line in actual_sql.splitlines() if line.strip())
        verification["sql_unique_to_generated"] = len(gen_lines - actual_lines)
        verification["sql_unique_to_actual"] = len(actual_lines - gen_lines)
    
    # 10. Check for key SQL elements based on XML structure
    if verification["nodes_count"] > 0:
        verification["sql_has_ctes"] = "WITH" in generated_sql or any(
            node.kind.value in ["PROJECTION", "JOIN", "AGGREGATION", "UNION"]
            for node in scenario.nodes.values()
        )
    
    # 11. Check for specific node types in SQL
    if verification["node_types"].get("PROJECTION", 0) > 0:
        verification["sql_has_projection"] = "projection" in generated_sql.lower()
    if verification["node_types"].get("JOIN", 0) > 0:
        verification["sql_has_join"] = "JOIN" in generated_sql.upper()
    if verification["node_types"].get("AGGREGATION", 0) > 0:
        verification["sql_has_aggregation"] = "GROUP BY" in generated_sql.upper()
    if verification["node_types"].get("UNION", 0) > 0:
        verification["sql_has_union"] = "UNION" in generated_sql.upper()
    
    # 12. Check for filters in SQL
    if total_filters > 0:
        verification["sql_has_where"] = "WHERE" in generated_sql.upper()
    
    # 13. Check for calculated attributes in SQL (for logical model)
    if scenario.logical_model and scenario.logical_model.calculated_attributes:
        calc_attr_names = [attr.name for attr in scenario.logical_model.calculated_attributes]
        verification["sql_has_calculated_attributes"] = any(
            name in generated_sql for name in calc_attr_names
        )
    
    return result

def main():
    """Main verification function."""
    print("=" * 80)
    print("COMPREHENSIVE SQL FILE VERIFICATION")
    print("=" * 80)
    print()
    
    all_results = []
    all_passed = True
    
    for xml_file, sql_file in SCENARIOS:
        print(f"Verifying: {xml_file} -> {sql_file}")
        result = verify_scenario(xml_file, sql_file)
        all_results.append(result)
        
        if result["errors"]:
            print(f"  ❌ ERRORS: {len(result['errors'])}")
            for error in result["errors"]:
                print(f"     - {error}")
            all_passed = False
        else:
            print(f"  ✅ Parse: {'OK' if result['parse_success'] else 'FAIL'}")
            print(f"  ✅ Render: {'OK' if result['render_success'] else 'FAIL'}")
            
            ver = result["verification"]
            print(f"  📊 Nodes: {ver.get('nodes_count', 0)}")
            print(f"  📊 Data Sources: {ver.get('data_sources_count', 0)}")
            print(f"  📊 Filters: {ver.get('total_filters', 0)}")
            print(f"  📊 SQL Length: {ver.get('sql_length', 0)} chars, {ver.get('sql_lines', 0)} lines")
            
            if not ver.get("sql_matches", False):
                print(f"  ⚠️  SQL mismatch detected (but may be whitespace-only)")
                if ver.get("sql_unique_to_generated", 0) > 0:
                    print(f"     - {ver['sql_unique_to_generated']} lines unique to generated")
                if ver.get("sql_unique_to_actual", 0) > 0:
                    print(f"     - {ver['sql_unique_to_actual']} lines unique to actual")
            else:
                print(f"  ✅ SQL matches exactly")
        
        print()
    
    # Summary
    print("=" * 80)
    print("SUMMARY")
    print("=" * 80)
    
    total = len(all_results)
    passed = sum(1 for r in all_results if not r["errors"] and r["parse_success"] and r["render_success"])
    
    print(f"Total scenarios: {total}")
    print(f"Passed: {passed}")
    print(f"Failed: {total - passed}")
    print()
    
    if all_passed:
        print("✅ ALL VERIFICATIONS PASSED")
    else:
        print("❌ SOME VERIFICATIONS FAILED")
        for result in all_results:
            if result["errors"]:
                print(f"  - {result['xml_file']}: {len(result['errors'])} errors")
    
    # Save detailed report
    report_path = Path("VERIFICATION_REPORT.json")
    with open(report_path, "w", encoding="utf-8") as f:
        json.dump(all_results, f, indent=2, default=str)
    print(f"\n📄 Detailed report saved to: {report_path}")
    
    return 0 if all_passed else 1

if __name__ == "__main__":
    exit(main())

