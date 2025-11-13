"""Integration smoke tests for the XML scenario parser."""

from __future__ import annotations

from pathlib import Path

import pytest

from xml_to_sql.parser import parse_scenario
from xml_to_sql.sql.renderer import render_scenario


@pytest.mark.parametrize(
    "filename",
    [
        "Sold_Materials.XML",
        "SALES_BOM.XML",
        "Recently_created_products.XML",
    ],
)
def test_parse_scenario_smoke(filename: str) -> None:
    root = Path(__file__).resolve().parents[1]
    xml_path = root / "Source (XML Files)" / filename
    scenario = parse_scenario(xml_path)

    assert scenario.metadata.scenario_id == filename.split(".")[0]
    assert scenario.nodes, "Expected nodes to be parsed"


def test_parse_scenario_variables_and_logical_model() -> None:
    root = Path(__file__).resolve().parents[1]
    xml_path = root / "Source (XML Files)" / "Material Details.XML"
    scenario = parse_scenario(xml_path)

    variables = {variable.variable_id: variable for variable in scenario.variables}
    assert "Material_Type" in variables
    material_type = variables["Material_Type"]
    assert material_type.selection_type == "SingleValue"
    assert material_type.attribute_name == "MTART"

    logical_model = scenario.logical_model
    assert logical_model is not None
    attribute_names = {attribute.name for attribute in logical_model.attributes}
    assert {"MANDT", "MATNR", "ERSDA", "MTART"}.issubset(attribute_names)
    assert any(attribute.local_variable == "#Material_Type" for attribute in logical_model.attributes)


def test_parse_legacy_column_view() -> None:
    root = Path(__file__).resolve().parents[1]
    xml_path = root / "Source (XML Files)" / "OLD_HANA_VIEWS" / "CV_CNCLD_EVNTS.xml"
    scenario = parse_scenario(xml_path)

    assert scenario.metadata.scenario_id == "CV_CNCLD_EVNTS"
    assert "CTLEQR" in scenario.nodes
    assert "Union_1" in scenario.nodes
    assert scenario.logical_model is not None
    assert scenario.logical_model.base_node_id == "Aggregation"


def test_render_legacy_column_view_smoke() -> None:
    root = Path(__file__).resolve().parents[1]
    xml_path = root / "Source (XML Files)" / "OLD_HANA_VIEWS" / "CV_CT02_CT03.xml"
    scenario = parse_scenario(xml_path)

    sql = render_scenario(scenario, validate=False)
    assert "SELECT" in sql


def test_render_legacy_helpers_left_right_in() -> None:
    """Ensure legacy helper functions are rewritten in legacy column views."""

    root = Path(__file__).resolve().parents[1]
    xml_path = root / "Source (XML Files)" / "OLD_HANA_VIEWS" / "CV_CNCLD_EVNTS.xml"
    scenario = parse_scenario(xml_path)

    sql = render_scenario(scenario, validate=False)
    flattened = " ".join(sql.split())

    assert 'SUBSTRING("ZZTREAT_DATE", 1, 6)' in flattened
    assert 'RIGHT("CALMONTH", 2)' in flattened
    assert ' IN (' in flattened
    assert "'01'" in flattened and "'03'" in flattened


def test_render_legacy_helpers_match_lpad() -> None:
    """Ensure MATCH and LPAD helpers rewrite correctly."""

    root = Path(__file__).resolve().parents[1]
    xml_path = root / "Source (XML Files)" / "OLD_HANA_VIEWS" / "CV_CT02_CT03.xml"
    scenario = parse_scenario(xml_path)

    sql = render_scenario(scenario, validate=False)
    flattened = " ".join(sql.split())

    assert "REGEXP_LIKE(" in flattened
    assert "LPAD(" in flattened