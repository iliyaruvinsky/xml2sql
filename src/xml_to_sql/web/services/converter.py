"""Service for converting XML to SQL."""

from __future__ import annotations

import json
from io import BytesIO
from pathlib import Path
from typing import Optional

from lxml import etree

from ...sql import render_scenario
from ...sql.corrector import AutoFixConfig, CorrectionResult, auto_correct_sql
from ...sql.validator import (
    ValidationResult,
    analyze_query_complexity,
    validate_expressions,
    validate_performance,
    validate_query_completeness,
    validate_snowflake_specific,
    validate_sql_structure,
)


class ConversionResult:
    """Result of a conversion operation."""

    def __init__(
        self,
        sql_content: str,
        scenario_id: Optional[str] = None,
        warnings: Optional[list[str]] = None,
        metadata: Optional[dict] = None,
        error: Optional[str] = None,
        validation: Optional[ValidationResult] = None,
        validation_logs: Optional[list[str]] = None,
        corrections: Optional[CorrectionResult] = None,
    ):
        self.sql_content = sql_content
        self.scenario_id = scenario_id
        self.warnings = warnings or []
        self.metadata = metadata or {}
        self.error = error
        self.validation = validation
        self.validation_logs = validation_logs or []
        self.corrections = corrections


def convert_xml_to_sql(
    xml_content: bytes,
    client: str = "PROD",
    language: str = "EN",
    schema_overrides: Optional[dict[str, str]] = None,
    currency_udf_name: Optional[str] = None,
    currency_rates_table: Optional[str] = None,
    currency_schema: Optional[str] = None,
    auto_fix: bool = False,
    auto_fix_config: Optional[AutoFixConfig] = None,
) -> ConversionResult:
    """
    Convert XML content to SQL.

    Args:
        xml_content: XML file content as bytes
        client: Default client value
        language: Default language value
        schema_overrides: Dictionary of schema name overrides
        currency_udf_name: Currency conversion UDF name
        currency_rates_table: Exchange rates table name
        currency_schema: Schema for currency artifacts

    Returns:
        ConversionResult with SQL content and metadata
    """
    try:
        # Parse XML from bytes
        tree = etree.parse(BytesIO(xml_content))
        root = tree.getroot()

        # Extract scenario ID from XML
        scenario_id = root.get("id")

        # Parse scenario to IR
        # parse_scenario expects a Path, so we create a temporary file
        import tempfile

        with tempfile.NamedTemporaryFile(mode="wb", suffix=".xml", delete=False) as tmp:
            tmp.write(xml_content)
            tmp_path = Path(tmp.name)

        try:
            from ...parser.scenario_parser import parse_scenario
            scenario_ir = parse_scenario(tmp_path)
        finally:
            # Clean up temp file
            tmp_path.unlink()

        # Build metadata
        nodes_count = len(scenario_ir.nodes)
        filters_count = sum(len(node.filters) for node in scenario_ir.nodes.values())
        calculated_count = sum(len(node.calculated_attributes) for node in scenario_ir.nodes.values())
        logical_model_present = scenario_ir.logical_model is not None

        metadata = {
            "scenario_id": scenario_ir.metadata.scenario_id,
            "nodes_count": nodes_count,
            "filters_count": filters_count,
            "calculated_attributes_count": calculated_count,
            "logical_model_present": logical_model_present,
        }

        # Render to SQL with warnings (disable validation to capture results separately)
        sql_content, warnings = render_scenario(
            scenario_ir,
            schema_overrides=schema_overrides or {},
            client=client,
            language=language,
            create_view=False,
            currency_udf=currency_udf_name,
            currency_schema=currency_schema,
            currency_table=currency_rates_table,
            return_warnings=True,
            validate=False,  # Validate separately to capture results
        )

        # Perform validation separately to capture results
        validation_result = ValidationResult()
        
        validation_logs: list[str] = []

        def _format_log(name: str, result: ValidationResult) -> str:
            status = "FAILED" if result.has_errors else "OK"
            return (
                f"{name}: {status} "
                f"(errors={len(result.errors)}, warnings={len(result.warnings)}, info={len(result.info)})"
            )

        # Phase 1: Structure validation
        structure_result = validate_sql_structure(sql_content)
        validation_result.merge(structure_result)
        validation_logs.append(_format_log("SQL Structure", structure_result))
        
        # Completeness validation (need render context)
        from ...sql.renderer import RenderContext, _topological_sort
        ctx = RenderContext(
            scenario_ir,
            schema_overrides or {},
            client,
            language,
            currency_udf_name,
            currency_schema,
            currency_rates_table,
        )
        # Populate CTE aliases for validation
        ordered_nodes = _topological_sort(scenario_ir)
        for node_id in ordered_nodes:
            if node_id in scenario_ir.data_sources:
                continue
            if node_id in scenario_ir.nodes:
                ctx.cte_aliases[node_id] = node_id.lower().replace("_", "_")
        
        completeness_result = validate_query_completeness(scenario_ir, sql_content, ctx)
        validation_result.merge(completeness_result)
        validation_logs.append(_format_log("Query Completeness", completeness_result))
        
        # Phase 2: Performance validation
        performance_result = validate_performance(sql_content, scenario_ir)
        validation_result.merge(performance_result)
        validation_logs.append(_format_log("Performance Checks", performance_result))
        
        # Phase 2: Snowflake-specific validation
        snowflake_result = validate_snowflake_specific(sql_content)
        validation_result.merge(snowflake_result)
        validation_logs.append(_format_log("Snowflake Specific Checks", snowflake_result))
        
        # Phase 2: Query complexity analysis
        complexity_result = analyze_query_complexity(sql_content, scenario_ir)
        validation_result.merge(complexity_result)
        validation_logs.append(_format_log("Query Complexity Analysis", complexity_result))

        # Phase 3: Advanced validation (optional - if schema metadata available)
        expression_result = validate_expressions(scenario_ir)
        validation_result.merge(expression_result)
        validation_logs.append(_format_log("Expression Validation", expression_result))

        # Phase 4: Auto-correction (if enabled)
        correction_result: Optional[CorrectionResult] = None
        final_sql = sql_content
        if auto_fix and validation_result.has_issues:
            if auto_fix_config is None:
                auto_fix_config = AutoFixConfig.default()
            
            correction_result = auto_correct_sql(
                sql_content,
                validation_result,
                scenario_ir,
                auto_fix_config,
            )
            
            if correction_result.corrections_applied:
                final_sql = correction_result.corrected_sql
                # Add correction notes to warnings
                for correction in correction_result.corrections_applied:
                    warnings.append(f"Auto-fixed: {correction.description}")
                
                # Re-validate corrected SQL (optional - can be disabled for performance)
                # For now, we'll skip re-validation to avoid double work

        return ConversionResult(
            sql_content=final_sql,
            scenario_id=scenario_id,
            warnings=warnings,
            metadata=metadata,
            validation=validation_result,
            validation_logs=validation_logs,
            corrections=correction_result,
        )

    except Exception as e:
        return ConversionResult(
            sql_content="",
            error=str(e),
            validation_logs=[],
        )

