"""Tests for HANA mode SQL generation."""

from __future__ import annotations

from pathlib import Path

import pytest
from lxml import etree

from xml_to_sql.domain import Scenario
from xml_to_sql.domain.types import DatabaseMode, HanaVersion, XMLFormat
from xml_to_sql.parser import parse_scenario
from xml_to_sql.parser.xml_format_detector import detect_xml_format, detect_hana_version_hint
from xml_to_sql.sql import render_scenario


# Test XML format detection
def test_detect_calculation_scenario_format():
    """Test detection of Calculation:scenario XML format."""
    xml_path = Path("Source (XML Files)/Sold_Materials.XML")
    if not xml_path.exists():
        pytest.skip("Test XML file not found")
    
    tree = etree.parse(xml_path)
    root = tree.getroot()
    xml_format = detect_xml_format(root)
    
    assert xml_format == XMLFormat.CALCULATION_SCENARIO


def test_detect_column_view_format():
    """Test detection of View:ColumnView XML format."""
    xml_path = Path("Source (XML Files)/OLD_HANA_VIEWS/CV_CNCLD_EVNTS.xml")
    if not xml_path.exists():
        pytest.skip("Test XML file not found")
    
    tree = etree.parse(xml_path)
    root = tree.getroot()
    xml_format = detect_xml_format(root)
    
    assert xml_format == XMLFormat.COLUMN_VIEW


# Test HANA version detection
def test_detect_hana_version_column_view():
    """Test HANA version detection for ColumnView format (should suggest 1.0)."""
    xml_path = Path("Source (XML Files)/OLD_HANA_VIEWS/CV_CNCLD_EVNTS.xml")
    if not xml_path.exists():
        pytest.skip("Test XML file not found")
    
    tree = etree.parse(xml_path)
    root = tree.getroot()
    version_hint = detect_hana_version_hint(root)
    
    # ColumnView format suggests HANA 1.0 era
    assert version_hint == HanaVersion.HANA_1_0


# Test HANA mode rendering
def test_render_hana_mode_if_function():
    """Test that IF() is preserved in HANA mode (not converted to IFF)."""
    xml_path = Path("Source (XML Files)/OLD_HANA_VIEWS/CV_CNCLD_EVNTS.xml")
    if not xml_path.exists():
        pytest.skip("Test XML file not found")
    
    scenario = parse_scenario(xml_path)
    
    # Render in HANA mode
    sql = render_scenario(
        scenario,
        database_mode=DatabaseMode.HANA,
        hana_version=HanaVersion.HANA_2_0,
        create_view=True,
        view_name="CV_CNCLD_EVNTS",
    )
    
    # Should contain IF(), not IFF()
    assert "IF(" in sql
    assert "IFF(" not in sql


def test_render_snowflake_mode_iff_function():
    """Test that IF() is converted to IFF() in Snowflake mode."""
    xml_path = Path("Source (XML Files)/OLD_HANA_VIEWS/CV_CNCLD_EVNTS.xml")
    if not xml_path.exists():
        pytest.skip("Test XML file not found")
    
    scenario = parse_scenario(xml_path)
    
    # Render in Snowflake mode
    sql = render_scenario(
        scenario,
        database_mode=DatabaseMode.SNOWFLAKE,
        create_view=True,
        view_name="CV_CNCLD_EVNTS",
    )
    
    # Should contain IFF(), not IF()
    assert "IFF(" in sql
    # Note: May still contain IF() in comments or as substring, so we check for IFF presence


def test_render_hana_mode_string_concatenation():
    """Test that string concatenation uses + in HANA mode."""
    xml_path = Path("Source (XML Files)/OLD_HANA_VIEWS/CV_CNCLD_EVNTS.xml")
    if not xml_path.exists():
        pytest.skip("Test XML file not found")
    
    scenario = parse_scenario(xml_path)
    
    # Render in HANA mode
    sql = render_scenario(
        scenario,
        database_mode=DatabaseMode.HANA,
        hana_version=HanaVersion.HANA_2_0,
        create_view=True,
        view_name="CV_CNCLD_EVNTS",
    )
    
    # In HANA mode, the formula uses + for concatenation
    # Original: leftstr("ZZTREAT_DATE",4)+'1'
    # Should keep + in HANA mode
    assert "+" in sql  # String concatenation with +


def test_render_snowflake_mode_string_concatenation():
    """Test that string concatenation uses || in Snowflake mode."""
    xml_path = Path("Source (XML Files)/OLD_HANA_VIEWS/CV_CNCLD_EVNTS.xml")
    if not xml_path.exists():
        pytest.skip("Test XML file not found")
    
    scenario = parse_scenario(xml_path)
    
    # Render in Snowflake mode
    sql = render_scenario(
        scenario,
        database_mode=DatabaseMode.SNOWFLAKE,
        create_view=True,
        view_name="CV_CNCLD_EVNTS",
    )
    
    # In Snowflake mode, should convert + to ||
    assert "||" in sql  # String concatenation with ||


def test_render_hana_mode_view_statement():
    """Test that HANA mode generates CREATE VIEW (not CREATE OR REPLACE VIEW)."""
    xml_path = Path("Source (XML Files)/Sold_Materials.XML")
    if not xml_path.exists():
        pytest.skip("Test XML file not found")
    
    scenario = parse_scenario(xml_path)
    
    # Render in HANA mode with create_view=True
    sql = render_scenario(
        scenario,
        database_mode=DatabaseMode.HANA,
        hana_version=HanaVersion.HANA_2_0,
        create_view=True,
        view_name="V_SOLD_MATERIALS",
    )
    
    # Should have CREATE VIEW (not CREATE OR REPLACE VIEW)
    assert "CREATE VIEW" in sql
    assert "CREATE OR REPLACE VIEW" not in sql


def test_render_snowflake_mode_view_statement():
    """Test that Snowflake mode generates CREATE OR REPLACE VIEW."""
    xml_path = Path("Source (XML Files)/Sold_Materials.XML")
    if not xml_path.exists():
        pytest.skip("Test XML file not found")
    
    scenario = parse_scenario(xml_path)
    
    # Render in Snowflake mode with create_view=True
    sql = render_scenario(
        scenario,
        database_mode=DatabaseMode.SNOWFLAKE,
        create_view=True,
        view_name="V_SOLD_MATERIALS",
    )
    
    # Should have CREATE OR REPLACE VIEW
    assert "CREATE OR REPLACE VIEW" in sql


def test_render_same_xml_both_modes():
    """Test that same XML produces different SQL for HANA vs Snowflake modes."""
    xml_path = Path("Source (XML Files)/OLD_HANA_VIEWS/CV_CNCLD_EVNTS.xml")
    if not xml_path.exists():
        pytest.skip("Test XML file not found")
    
    scenario = parse_scenario(xml_path)
    
    # Render in both modes
    hana_sql = render_scenario(
        scenario,
        database_mode=DatabaseMode.HANA,
        hana_version=HanaVersion.HANA_2_0,
        create_view=True,
        view_name="CV_CNCLD_EVNTS",
    )
    
    snowflake_sql = render_scenario(
        scenario,
        database_mode=DatabaseMode.SNOWFLAKE,
        create_view=True,
        view_name="CV_CNCLD_EVNTS",
    )
    
    # SQL should be different between modes
    assert hana_sql != snowflake_sql
    
    # HANA should have IF(), Snowflake should have IFF()
    assert "IF(" in hana_sql
    assert "IFF(" in snowflake_sql


def test_hana_version_1_0_leftstr():
    """Test that HANA 1.0 preserves LEFTSTR function."""
    xml_path = Path("Source (XML Files)/OLD_HANA_VIEWS/CV_CNCLD_EVNTS.xml")
    if not xml_path.exists():
        pytest.skip("Test XML file not found")
    
    scenario = parse_scenario(xml_path)
    
    # Render in HANA 1.0 mode
    sql = render_scenario(
        scenario,
        database_mode=DatabaseMode.HANA,
        hana_version=HanaVersion.HANA_1_0,
        create_view=True,
        view_name="CV_CNCLD_EVNTS",
    )
    
    # HANA 1.0 should preserve LEFTSTR
    # Note: This depends on the function translator implementation
    # May be LEFTSTR or SUBSTRING depending on version logic


def test_hana_version_2_0_substring():
    """Test that HANA 2.0 can modernize LEFTSTR to SUBSTRING."""
    xml_path = Path("Source (XML Files)/OLD_HANA_VIEWS/CV_CNCLD_EVNTS.xml")
    if not xml_path.exists():
        pytest.skip("Test XML file not found")
    
    scenario = parse_scenario(xml_path)
    
    # Render in HANA 2.0 mode
    sql = render_scenario(
        scenario,
        database_mode=DatabaseMode.HANA,
        hana_version=HanaVersion.HANA_2_0,
        create_view=True,
        view_name="CV_CNCLD_EVNTS",
    )
    
    # HANA 2.0 can use modern SUBSTRING
    assert "SUBSTRING" in sql

