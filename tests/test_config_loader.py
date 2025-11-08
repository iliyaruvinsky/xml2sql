"""Tests for configuration loading utilities."""

from __future__ import annotations

import textwrap
from pathlib import Path

from xml_to_sql.config import load_config


def write_config(tmp_path: Path, content: str) -> Path:
    config_path = tmp_path / "config.yaml"
    config_path.write_text(textwrap.dedent(content).strip() + "\n", encoding="utf-8")
    return config_path


def test_load_config_with_defaults(tmp_path: Path) -> None:
    config_path = write_config(
        tmp_path,
        """
        defaults:
          client: "PROD"
          language: "EN"
        scenarios:
          - id: "Sold_Materials"
            output: "V_C_SOLD_MATERIALS"
            overrides:
              client: "100"
        """,
    )

    config = load_config(config_path)

    assert config.default_client == "PROD"
    assert config.default_language == "EN"
    assert config.source_directory == (tmp_path / "Source (XML Files)").resolve()
    assert config.target_directory == (tmp_path / "Target (SQL Scripts)").resolve()
    assert len(config.scenarios) == 1

    scenario = config.scenarios[0]
    assert scenario.id == "Sold_Materials"
    assert scenario.overrides.client == "100"
    source_path = scenario.resolve_source_path(config.source_directory)
    assert source_path.name == "Sold_Materials.XML"


def test_select_scenarios_filters_disabled(tmp_path: Path) -> None:
    config_path = write_config(
        tmp_path,
        """
        scenarios:
          - id: "Enabled"
            enabled: true
          - id: "Disabled"
            enabled: false
        """,
    )
    config = load_config(config_path)

    selected = config.select_scenarios()
    assert [scenario.id for scenario in selected] == ["Enabled"]

    selected_specific = config.select_scenarios(["Disabled"])
    assert not selected_specific

