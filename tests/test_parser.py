"""Integration smoke tests for the XML scenario parser."""

from __future__ import annotations

from pathlib import Path

import pytest

from xml_to_sql.parser import parse_scenario


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
