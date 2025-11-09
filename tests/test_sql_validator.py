"""Tests for SQL validation module."""

import pytest

from xml_to_sql.sql.validator import (
    ValidationIssue,
    ValidationResult,
    ValidationSeverity,
    analyze_query_complexity,
    validate_performance,
    validate_query_completeness,
    validate_snowflake_specific,
    validate_sql_structure,
)
from xml_to_sql.domain.models import Scenario, ScenarioMetadata, DataSource, DataSourceType
from xml_to_sql.sql.renderer import RenderContext


class TestValidationResult:
    """Tests for ValidationResult class."""

    def test_empty_result_is_valid(self):
        """Empty validation result should be valid."""
        result = ValidationResult()
        assert result.is_valid is True
        assert result.has_errors is False
        assert result.has_issues is False

    def test_add_error_makes_invalid(self):
        """Adding an error should make result invalid."""
        result = ValidationResult()
        result.add_error("Test error", "TEST_ERROR")
        assert result.is_valid is False
        assert result.has_errors is True
        assert len(result.errors) == 1

    def test_add_warning_keeps_valid(self):
        """Adding a warning should keep result valid."""
        result = ValidationResult()
        result.add_warning("Test warning", "TEST_WARNING")
        assert result.is_valid is True
        assert result.has_errors is False
        assert len(result.warnings) == 1

    def test_merge_results(self):
        """Merging results should combine all issues."""
        result1 = ValidationResult()
        result1.add_error("Error 1", "ERR1")
        result1.add_warning("Warning 1", "WARN1")

        result2 = ValidationResult()
        result2.add_error("Error 2", "ERR2")
        result2.add_info("Info 1", "INFO1")

        result1.merge(result2)
        assert result1.is_valid is False
        assert len(result1.errors) == 2
        assert len(result1.warnings) == 1
        assert len(result1.info) == 1


class TestValidateSqlStructure:
    """Tests for validate_sql_structure function."""

    def test_empty_sql_is_error(self):
        """Empty SQL should be an error."""
        result = validate_sql_structure("")
        assert result.has_errors
        assert any("empty" in str(e).lower() for e in result.errors)

    def test_whitespace_only_sql_is_error(self):
        """Whitespace-only SQL should be an error."""
        result = validate_sql_structure("   \n\t  ")
        assert result.has_errors

    def test_valid_select_statement(self):
        """Valid SELECT statement should pass."""
        sql = "SELECT * FROM table1"
        result = validate_sql_structure(sql)
        assert result.is_valid
        assert not result.has_errors

    def test_missing_select_is_error(self):
        """SQL without SELECT should be an error."""
        sql = "FROM table1"
        result = validate_sql_structure(sql)
        assert result.has_errors
        assert any("SELECT" in str(e) for e in result.errors)

    def test_unbalanced_parentheses(self):
        """Unbalanced parentheses should be an error."""
        sql = "SELECT * FROM (table1"
        result = validate_sql_structure(sql)
        assert result.has_errors
        assert any("parentheses" in str(e).lower() for e in result.errors)

    def test_balanced_parentheses(self):
        """Balanced parentheses should pass."""
        sql = "SELECT * FROM (SELECT * FROM table1)"
        result = validate_sql_structure(sql)
        assert result.is_valid

    def test_with_clause_structure(self):
        """WITH clause should have proper structure."""
        sql = """
        WITH cte1 AS (
            SELECT * FROM table1
        )
        SELECT * FROM cte1
        """
        result = validate_sql_structure(sql)
        assert result.is_valid

    def test_with_clause_no_select_after(self):
        """WITH clause without SELECT after should be an error."""
        sql = "WITH cte1 AS (SELECT * FROM table1)"
        result = validate_sql_structure(sql)
        assert result.has_errors
        assert any("SELECT" in str(e) for e in result.errors)

    def test_duplicate_cte_names(self):
        """Duplicate CTE names should be an error."""
        sql = """
        WITH cte1 AS (SELECT * FROM table1),
             cte1 AS (SELECT * FROM table2)
        SELECT * FROM cte1
        """
        result = validate_sql_structure(sql)
        assert result.has_errors
        assert any("duplicate" in str(e).lower() for e in result.errors)

    def test_multiple_ctes(self):
        """Multiple CTEs should be valid."""
        sql = """
        WITH cte1 AS (SELECT * FROM table1),
             cte2 AS (SELECT * FROM table2)
        SELECT * FROM cte1
        """
        result = validate_sql_structure(sql)
        assert result.is_valid


class TestValidateQueryCompleteness:
    """Tests for validate_query_completeness function."""

    def test_valid_scenario(self):
        """Valid scenario should pass completeness validation."""
        # Create minimal valid scenario
        metadata = ScenarioMetadata(scenario_id="test", name="Test")
        scenario = Scenario(metadata=metadata, nodes={}, data_sources={})
        sql = "SELECT * FROM table1"
        ctx = RenderContext(scenario, {}, "PROD", "EN", None, None, None)

        result = validate_query_completeness(scenario, sql, ctx)
        # Should not have errors for minimal scenario
        assert not result.has_errors

    def test_missing_node_reference(self):
        """Missing node reference should be an error."""
        metadata = ScenarioMetadata(scenario_id="test", name="Test")
        scenario = Scenario(metadata=metadata, nodes={}, data_sources={})
        sql = "SELECT * FROM table1"
        ctx = RenderContext(scenario, {}, "PROD", "EN", None, None, None)
        ctx.cte_aliases["missing_node"] = "missing_node"

        result = validate_query_completeness(scenario, sql, ctx)
        assert result.has_errors
        assert any("not found" in str(e).lower() for e in result.errors)

    def test_empty_schema_name_warning(self):
        """Empty schema name should be a warning."""
        metadata = ScenarioMetadata(scenario_id="test", name="Test")
        ds = DataSource(
            data_source_id="ds1",
            schema_name="",
            object_name="table1",
            data_source_type=DataSourceType.TABLE,
        )
        scenario = Scenario(metadata=metadata, nodes={}, data_sources={"ds1": ds})
        sql = "SELECT * FROM table1"
        ctx = RenderContext(scenario, {}, "PROD", "EN", None, None, None)

        result = validate_query_completeness(scenario, sql, ctx)
        assert any("schema" in str(w).lower() for w in result.warnings)

    def test_empty_object_name_warning(self):
        """Empty object name should be a warning."""
        metadata = ScenarioMetadata(scenario_id="test", name="Test")
        ds = DataSource(
            data_source_id="ds1",
            schema_name="schema1",
            object_name="",
            data_source_type=DataSourceType.TABLE,
        )
        scenario = Scenario(metadata=metadata, nodes={}, data_sources={"ds1": ds})
        sql = "SELECT * FROM table1"
        ctx = RenderContext(scenario, {}, "PROD", "EN", None, None, None)

        result = validate_query_completeness(scenario, sql, ctx)
        assert any("object" in str(w).lower() for w in result.warnings)

    def test_undefined_cte_reference_warning(self):
        """Undefined CTE reference should be a warning."""
        metadata = ScenarioMetadata(scenario_id="test", name="Test")
        scenario = Scenario(metadata=metadata, nodes={}, data_sources={})
        sql = "SELECT * FROM undefined_cte"
        ctx = RenderContext(scenario, {}, "PROD", "EN", None, None, None)

        result = validate_query_completeness(scenario, sql, ctx)
        assert any("undefined" in str(w).lower() for w in result.warnings)

    def test_table_reference_not_warning(self):
        """Table references (schema.table) should not be warnings."""
        metadata = ScenarioMetadata(scenario_id="test", name="Test")
        ds = DataSource(
            data_source_id="ds1",
            schema_name="schema1",
            object_name="table1",
            data_source_type=DataSourceType.TABLE,
        )
        scenario = Scenario(metadata=metadata, nodes={}, data_sources={"ds1": ds})
        sql = "SELECT * FROM schema1.table1"
        ctx = RenderContext(scenario, {}, "PROD", "EN", None, None, None)

        result = validate_query_completeness(scenario, sql, ctx)
        # Should not warn about schema.table references
        cte_warnings = [w for w in result.warnings if "undefined" in str(w).lower()]
        assert len(cte_warnings) == 0


class TestValidationIssue:
    """Tests for ValidationIssue class."""

    def test_issue_string_representation(self):
        """ValidationIssue should have proper string representation."""
        issue = ValidationIssue(
            ValidationSeverity.ERROR, "Test error", "TEST_ERROR", line_number=5
        )
        assert "ERROR" in str(issue)
        assert "TEST_ERROR" in str(issue)
        assert "Test error" in str(issue)
        assert "line 5" in str(issue)

    def test_issue_without_line_number(self):
        """ValidationIssue without line number should work."""
        issue = ValidationIssue(ValidationSeverity.WARNING, "Test warning", "TEST_WARNING")
        assert "WARNING" in str(issue)
        assert "line" not in str(issue) or "line None" not in str(issue)


class TestValidatePerformance:
    """Tests for validate_performance function."""

    def test_cartesian_product_detection(self):
        """Cartesian product should be detected."""
        sql = "SELECT * FROM table1 JOIN table2 ON 1 = 1"
        scenario = Scenario(metadata=ScenarioMetadata(scenario_id="test", name="Test"), nodes={}, data_sources={})
        result = validate_performance(sql, scenario)
        assert any("cartesian" in str(w).lower() for w in result.warnings)

    def test_select_star_warning(self):
        """SELECT * should generate warning when logical model available."""
        sql = "SELECT * FROM table1"
        metadata = ScenarioMetadata(scenario_id="test", name="Test")
        from xml_to_sql.domain.models import LogicalModel, Attribute, DataTypeSpec, SnowflakeType
        logical_model = LogicalModel(
            attributes=[Attribute(name="col1", data_type=DataTypeSpec(SnowflakeType.VARCHAR, length=100))]
        )
        scenario = Scenario(metadata=metadata, nodes={}, data_sources={}, logical_model=logical_model)
        result = validate_performance(sql, scenario)
        assert any("SELECT *" in str(w) for w in result.warnings)

    def test_missing_where_clause(self):
        """Missing WHERE clause should generate info."""
        sql = "SELECT * FROM table1"
        scenario = Scenario(metadata=ScenarioMetadata(scenario_id="test", name="Test"), nodes={}, data_sources={})
        result = validate_performance(sql, scenario)
        assert any("WHERE" in str(i) for i in result.info)

    def test_aggregation_without_groupby(self):
        """Aggregation without GROUP BY on multiple tables should warn."""
        sql = "SELECT COUNT(*) FROM table1 JOIN table2 ON table1.id = table2.id"
        scenario = Scenario(metadata=ScenarioMetadata(scenario_id="test", name="Test"), nodes={}, data_sources={})
        result = validate_performance(sql, scenario)
        assert any("GROUP BY" in str(w) for w in result.warnings)


class TestValidateSnowflakeSpecific:
    """Tests for validate_snowflake_specific function."""

    def test_reserved_keyword_warning(self):
        """Reserved keywords used as identifiers should warn."""
        sql = "SELECT TABLE FROM schema1.table1"  # TABLE is reserved
        result = validate_snowflake_specific(sql)
        assert any("reserved" in str(w).lower() for w in result.warnings)

    def test_string_concat_plus_warning(self):
        """String concatenation with + should warn."""
        sql = "SELECT 'hello' + 'world'"
        result = validate_snowflake_specific(sql)
        assert any("||" in str(w) or "concatenation" in str(w).lower() for w in result.warnings)

    def test_hana_if_not_translated(self):
        """HANA IF() function should warn."""
        sql = "SELECT IF(1=1, 'yes', 'no')"
        result = validate_snowflake_specific(sql)
        assert any("IFF" in str(w) or "HANA" in str(w) for w in result.warnings)

    def test_cte_count_exceeded(self):
        """CTE count exceeding 100 should error."""
        # Create SQL with 101 CTEs
        ctes = "WITH " + ", ".join([f"cte{i} AS (SELECT {i})" for i in range(101)])
        sql = ctes + " SELECT * FROM cte0"
        result = validate_snowflake_specific(sql)
        assert result.has_errors
        assert any("100" in str(e) for e in result.errors)

    def test_high_cte_count_warning(self):
        """CTE count > 20 should warn."""
        ctes = "WITH " + ", ".join([f"cte{i} AS (SELECT {i})" for i in range(25)])
        sql = ctes + " SELECT * FROM cte0"
        result = validate_snowflake_specific(sql)
        assert any("20" in str(w) for w in result.warnings)

    def test_view_name_reserved_keyword(self):
        """View name as reserved keyword should error."""
        sql = "CREATE VIEW TABLE AS SELECT 1"  # TABLE is reserved
        result = validate_snowflake_specific(sql)
        assert result.has_errors
        assert any("reserved" in str(e).lower() for e in result.errors)

    def test_join_without_on(self):
        """JOIN without ON clause should warn."""
        sql = "SELECT * FROM table1 LEFT JOIN table2"
        result = validate_snowflake_specific(sql)
        assert any("ON" in str(w) for w in result.warnings)

    def test_unqualified_table_reference(self):
        """Unqualified table references should info."""
        sql = "SELECT * FROM table1"
        result = validate_snowflake_specific(sql)
        assert any("schema" in str(i).lower() for i in result.info)


class TestAnalyzeQueryComplexity:
    """Tests for analyze_query_complexity function."""

    def test_high_cte_count(self):
        """High CTE count should warn."""
        ctes = "WITH " + ", ".join([f"cte{i} AS (SELECT {i})" for i in range(25)])
        sql = ctes + " SELECT * FROM cte0"
        scenario = Scenario(metadata=ScenarioMetadata(scenario_id="test", name="Test"), nodes={}, data_sources={})
        result = analyze_query_complexity(sql, scenario)
        assert any("20" in str(w) for w in result.warnings)

    def test_moderate_cte_count(self):
        """Moderate CTE count should info."""
        ctes = "WITH " + ", ".join([f"cte{i} AS (SELECT {i})" for i in range(15)])
        sql = ctes + " SELECT * FROM cte0"
        scenario = Scenario(metadata=ScenarioMetadata(scenario_id="test", name="Test"), nodes={}, data_sources={})
        result = analyze_query_complexity(sql, scenario)
        assert any("moderate" in str(i).lower() for i in result.info)

    def test_high_join_count(self):
        """High JOIN count should warn."""
        joins = "SELECT * FROM table1 " + " ".join([f"JOIN table{i} ON table1.id = table{i}.id" for i in range(2, 12)])
        scenario = Scenario(metadata=ScenarioMetadata(scenario_id="test", name="Test"), nodes={}, data_sources={})
        result = analyze_query_complexity(joins, scenario)
        assert any("10" in str(w) for w in result.warnings)

    def test_high_subquery_count(self):
        """High subquery count should warn."""
        sql = "SELECT * FROM (SELECT * FROM (SELECT * FROM (SELECT * FROM (SELECT * FROM (SELECT * FROM table1)))))"
        scenario = Scenario(metadata=ScenarioMetadata(scenario_id="test", name="Test"), nodes={}, data_sources={})
        result = analyze_query_complexity(sql, scenario)
        assert any("subquery" in str(w).lower() for w in result.warnings)

    def test_complex_scenario(self):
        """Complex scenario should info."""
        sql = "SELECT * FROM table1"
        # Create scenario with many nodes
        from xml_to_sql.domain.models import Node, NodeKind
        nodes = {f"node{i}": Node(node_id=f"node{i}", kind=NodeKind.PROJECTION, inputs=[]) for i in range(20)}
        scenario = Scenario(metadata=ScenarioMetadata(scenario_id="test", name="Test"), nodes=nodes, data_sources={})
        result = analyze_query_complexity(sql, scenario)
        assert any("complex" in str(i).lower() for i in result.info)
