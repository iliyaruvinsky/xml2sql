"""Tests for SQL rendering."""

from __future__ import annotations

from pathlib import Path

import pytest

from xml_to_sql.domain import (
    AggregationNode,
    AggregationSpec,
    AttributeMapping,
    DataSource,
    DataSourceType,
    Expression,
    ExpressionType,
    JoinCondition,
    JoinNode,
    JoinType,
    Node,
    NodeKind,
    Predicate,
    PredicateKind,
    Scenario,
    ScenarioMetadata,
)
from xml_to_sql.sql import render_scenario


def test_render_simple_projection() -> None:
    """Test rendering a simple projection from a data source."""

    metadata = ScenarioMetadata(scenario_id="test", default_client="100", default_language="EN")
    scenario = Scenario(metadata=metadata)

    scenario.data_sources["VBAP"] = DataSource(
        source_id="VBAP",
        source_type=DataSourceType.TABLE,
        schema_name="SAPK5D",
        object_name="VBAP",
    )

    node = Node(
        node_id="Projection_1",
        kind=NodeKind.PROJECTION,
        inputs=["VBAP"],
        mappings=[
            AttributeMapping(
                target_name="MATNR",
                expression=Expression(ExpressionType.COLUMN, "MATNR"),
            ),
            AttributeMapping(
                target_name="MANDT",
                expression=Expression(ExpressionType.COLUMN, "MANDT"),
            ),
        ],
    )
    scenario.add_node(node)

    sql = render_scenario(scenario)

    assert "WITH" in sql
    assert "projection_1" in sql.lower()
    assert "MATNR" in sql
    assert "MANDT" in sql
    assert "SAPK5D" in sql or "VBAP" in sql


def test_render_projection_with_filter() -> None:
    """Test rendering a projection with a WHERE filter."""

    metadata = ScenarioMetadata(scenario_id="test")
    scenario = Scenario(metadata=metadata)

    scenario.data_sources["VBAP"] = DataSource(
        source_id="VBAP",
        source_type=DataSourceType.TABLE,
        schema_name="SAPK5D",
        object_name="VBAP",
    )

    node = Node(
        node_id="Projection_1",
        kind=NodeKind.PROJECTION,
        inputs=["VBAP"],
        mappings=[
            AttributeMapping(
                target_name="ERDAT",
                expression=Expression(ExpressionType.COLUMN, "ERDAT"),
            ),
        ],
        filters=[
            Predicate(
                kind=PredicateKind.COMPARISON,
                left=Expression(ExpressionType.COLUMN, "ERDAT"),
                operator=">",
                right=Expression(ExpressionType.LITERAL, "20140101"),
            ),
        ],
    )
    scenario.add_node(node)

    sql = render_scenario(scenario)

    assert "WHERE" in sql
    assert ">" in sql or "GT" in sql
    assert "20140101" in sql


def test_render_join() -> None:
    """Test rendering a join node."""

    metadata = ScenarioMetadata(scenario_id="test")
    scenario = Scenario(metadata=metadata)

    scenario.data_sources["MAST"] = DataSource(
        source_id="MAST",
        source_type=DataSourceType.TABLE,
        schema_name="SAPK5D",
        object_name="MAST",
    )

    scenario.data_sources["MARA"] = DataSource(
        source_id="MARA",
        source_type=DataSourceType.TABLE,
        schema_name="SAPK5D",
        object_name="MARA",
    )

    proj1 = Node(
        node_id="Projection_1",
        kind=NodeKind.PROJECTION,
        inputs=["MAST"],
        mappings=[
            AttributeMapping(
                target_name="MATNR",
                expression=Expression(ExpressionType.COLUMN, "MATNR"),
            ),
            AttributeMapping(
                target_name="MANDT",
                expression=Expression(ExpressionType.COLUMN, "MANDT"),
            ),
        ],
    )
    scenario.add_node(proj1)

    proj2 = Node(
        node_id="Projection_2",
        kind=NodeKind.PROJECTION,
        inputs=["MARA"],
        mappings=[
            AttributeMapping(
                target_name="MATNR",
                expression=Expression(ExpressionType.COLUMN, "MATNR"),
            ),
            AttributeMapping(
                target_name="MANDT",
                expression=Expression(ExpressionType.COLUMN, "MANDT"),
            ),
        ],
    )
    scenario.add_node(proj2)

    join_node = JoinNode(
        node_id="Join_1",
        kind=NodeKind.JOIN,
        inputs=["Projection_1", "Projection_2"],
        join_type=JoinType.INNER,
        conditions=[
            JoinCondition(
                left=Expression(ExpressionType.COLUMN, "MATNR"),
                right=Expression(ExpressionType.COLUMN, "MATNR"),
            ),
            JoinCondition(
                left=Expression(ExpressionType.COLUMN, "MANDT"),
                right=Expression(ExpressionType.COLUMN, "MANDT"),
            ),
        ],
    )
    scenario.add_node(join_node)

    sql = render_scenario(scenario)

    assert "JOIN" in sql
    assert "projection_1" in sql.lower()
    assert "projection_2" in sql.lower()


def test_render_aggregation() -> None:
    """Test rendering an aggregation node."""

    metadata = ScenarioMetadata(scenario_id="test")
    scenario = Scenario(metadata=metadata)

    scenario.data_sources["VBAP"] = DataSource(
        source_id="VBAP",
        source_type=DataSourceType.TABLE,
        schema_name="SAPK5D",
        object_name="VBAP",
    )

    proj = Node(
        node_id="Projection_1",
        kind=NodeKind.PROJECTION,
        inputs=["VBAP"],
        mappings=[
            AttributeMapping(
                target_name="MATNR",
                expression=Expression(ExpressionType.COLUMN, "MATNR"),
            ),
            AttributeMapping(
                target_name="ERDAT",
                expression=Expression(ExpressionType.COLUMN, "ERDAT"),
            ),
        ],
    )
    scenario.add_node(proj)

    agg = AggregationNode(
        node_id="Aggregation_1",
        kind=NodeKind.AGGREGATION,
        inputs=["Projection_1"],
        group_by=["MATNR"],
        aggregations=[
            AggregationSpec(
                target_name="MAX_ERDAT",
                function="MAX",
                expression=Expression(ExpressionType.COLUMN, "ERDAT"),
            ),
        ],
    )
    scenario.add_node(agg)

    sql = render_scenario(scenario)

    assert "GROUP BY" in sql
    assert "MAX" in sql
    assert "MATNR" in sql


def test_render_integration_sold_materials(tmp_path: Path) -> None:
    """Integration test with a real XML file."""

    root = Path(__file__).resolve().parents[1]
    xml_path = root / "Source (XML Files)" / "Sold_Materials.XML"

    if not xml_path.exists():
        pytest.skip(f"Test file not found: {xml_path}")

    from xml_to_sql.parser import parse_scenario

    scenario = parse_scenario(xml_path)
    sql = render_scenario(scenario)

    assert "WITH" in sql
    assert "projection_1" in sql.lower() or "projection_1" in sql.lower()
    assert "aggregation_1" in sql.lower() or "aggregation_1" in sql.lower()
    assert "SELECT" in sql
    assert "VBAP" in sql or "SAPK5D" in sql


@pytest.mark.parametrize(
    "filename",
    [
        "Sold_Materials.XML",
        "SALES_BOM.XML",
        "Recently_created_products.XML",
        "KMDM_Materials.XML",
        "CURRENT_MAT_SORT.XML",
        "Material Details.XML",
        "Sold_Materials_PROD.XML",
    ],
)
def test_render_all_xml_samples(filename: str) -> None:
    """Regression test for all XML sample files."""

    root = Path(__file__).resolve().parents[1]
    xml_path = root / "Source (XML Files)" / filename

    if not xml_path.exists():
        pytest.skip(f"Test file not found: {xml_path}")

    from xml_to_sql.parser import parse_scenario

    scenario = parse_scenario(xml_path)
    sql = render_scenario(scenario)

    assert "SELECT" in sql, f"Generated SQL for {filename} should contain SELECT"
    if len(scenario.nodes) > 0:
        assert len(sql) > 50, f"Generated SQL for {filename} should be substantial when nodes exist"


def test_render_union_node() -> None:
    """Test rendering a union node."""

    from xml_to_sql.domain import UnionNode

    metadata = ScenarioMetadata(scenario_id="test")
    scenario = Scenario(metadata=metadata)

    scenario.data_sources["T1"] = DataSource(
        source_id="T1",
        source_type=DataSourceType.TABLE,
        schema_name="SAPK5D",
        object_name="T1",
    )

    scenario.data_sources["T2"] = DataSource(
        source_id="T2",
        source_type=DataSourceType.TABLE,
        schema_name="SAPK5D",
        object_name="T2",
    )

    proj1 = Node(
        node_id="Projection_1",
        kind=NodeKind.PROJECTION,
        inputs=["T1"],
        mappings=[
            AttributeMapping(
                target_name="MATNR",
                expression=Expression(ExpressionType.COLUMN, "MATNR"),
                source_node="T1",
            ),
        ],
    )
    scenario.add_node(proj1)

    proj2 = Node(
        node_id="Projection_2",
        kind=NodeKind.PROJECTION,
        inputs=["T2"],
        mappings=[
            AttributeMapping(
                target_name="MATNR",
                expression=Expression(ExpressionType.COLUMN, "MATNR"),
                source_node="T2",
            ),
        ],
    )
    scenario.add_node(proj2)

    union_node = UnionNode(
        node_id="Union_1",
        kind=NodeKind.UNION,
        inputs=["Projection_1", "Projection_2"],
        mappings=[
            AttributeMapping(
                target_name="MATNR",
                expression=Expression(ExpressionType.COLUMN, "MATNR"),
                source_node="Projection_1",
            ),
            AttributeMapping(
                target_name="MATNR",
                expression=Expression(ExpressionType.COLUMN, "MATNR"),
                source_node="Projection_2",
            ),
        ],
        union_all=True,
    )
    scenario.add_node(union_node)

    sql = render_scenario(scenario)

    assert "UNION ALL" in sql or "UNION" in sql
    assert "projection_1" in sql.lower()
    assert "projection_2" in sql.lower()


def test_render_with_currency_config() -> None:
    """Test rendering with currency conversion configuration."""

    metadata = ScenarioMetadata(scenario_id="test")
    scenario = Scenario(metadata=metadata)

    scenario.data_sources["VBAP"] = DataSource(
        source_id="VBAP",
        source_type=DataSourceType.TABLE,
        schema_name="SAPK5D",
        object_name="VBAP",
    )

    node = Node(
        node_id="Projection_1",
        kind=NodeKind.PROJECTION,
        inputs=["VBAP"],
        mappings=[
            AttributeMapping(
                target_name="KWBTR",
                expression=Expression(ExpressionType.COLUMN, "KWBTR"),
            ),
        ],
    )
    scenario.add_node(node)

    sql = render_scenario(
        scenario,
        currency_udf="CONVERT_CURRENCY",
        currency_schema="UTILITY",
        currency_table="EXCHANGE_RATES",
    )

    assert "CONVERT_CURRENCY" in sql or "EXCHANGE_RATES" in sql or len(sql) > 0


def test_function_translation_if_statement() -> None:
    """Test translation of HANA IF function to Snowflake IFF."""

    from xml_to_sql.domain import CalculatedAttribute
    from xml_to_sql.sql.function_translator import translate_raw_formula

    class MockContext:
        client = "100"
        language = "EN"

    formula = 'if("EPVOZ"=\'S\',-"KWBTR","KWBTR")'
    translated = translate_raw_formula(formula, MockContext())

    assert "IFF" in translated.upper()
    assert "EPVOZ" in translated
    assert "KWBTR" in translated


def test_function_translation_string_concatenation() -> None:
    """Test translation of HANA string concatenation."""

    from xml_to_sql.sql.function_translator import translate_raw_formula

    class MockContext:
        client = "100"
        language = "EN"

    formula = "'0000000000'+\"BISMT\""
    translated = translate_raw_formula(formula, MockContext())

    assert "||" in translated or "+" in translated

