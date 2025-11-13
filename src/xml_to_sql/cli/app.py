"""Typer-based command line interface for xml_to_sql."""

from __future__ import annotations

from pathlib import Path
from typing import List, Optional

import typer

from ..config import Config, ScenarioConfig, load_config
from ..parser import parse_scenario
from ..sql import render_scenario

app = typer.Typer(help="Convert SAP HANA calculation view XML to intermediate IR and SQL.")


@app.command()
def convert(
    config: Path = typer.Option(..., "--config", "-c", help="Path to a YAML configuration file."),
    scenario: Optional[List[str]] = typer.Option(
        None,
        "--scenario",
        "-s",
        help="Limit execution to specific scenario ids or output names.",
    ),
    list_only: bool = typer.Option(
        False,
        "--list-only",
        "-l",
        help="Do not parse files; only show which scenarios would be processed.",
    ),
) -> None:
    """Parse configured scenarios and (eventually) emit SQL artefacts."""

    config_obj = load_config(config)
    selected = config_obj.select_scenarios(scenario)

    if not selected:
        message = "No scenarios matched the requested filters." if scenario else "No scenarios enabled in config."
        typer.secho(message, fg=typer.colors.YELLOW)
        raise typer.Exit(code=1)

    for scenario_cfg in selected:
        source_path = scenario_cfg.resolve_source_path(config_obj.source_directory)
        target_path = config_obj.resolve_target_path(scenario_cfg)
        typer.echo(f"[plan] {source_path} -> {target_path}")
        if list_only:
            continue

        if not source_path.exists():
            typer.secho(f"  ERROR: Source file not found: {source_path}", fg=typer.colors.RED)
            continue

        try:
            scenario_ir = parse_scenario(source_path)
            _describe_scenario(scenario_ir, scenario_cfg, target_path)

            client = scenario_cfg.overrides.effective_client(config_obj.default_client)
            language = scenario_cfg.overrides.effective_language(config_obj.default_language)
            output_name = scenario_cfg.output_name or scenario_cfg.id

            sql_content = render_scenario(
                scenario_ir,
                schema_overrides=config_obj.schema_overrides,
                client=client,
                language=language,
                create_view=True,
                view_name=output_name,
                currency_udf=config_obj.currency.udf_name,
                currency_schema=config_obj.currency.schema,
                currency_table=config_obj.currency.rates_table,
            )

            target_path.parent.mkdir(parents=True, exist_ok=True)
            target_path.write_text(sql_content, encoding="utf-8")
            typer.secho(f"  ✓ SQL generated: {target_path}", fg=typer.colors.GREEN)

        except Exception as e:
            typer.secho(f"  ERROR: {e}", fg=typer.colors.RED)
            raise typer.Exit(code=1)


@app.command("list")
def list_scenarios(
    config: Path = typer.Option(..., "--config", "-c", help="Path to a YAML configuration file."),
) -> None:
    """Display scenarios defined in the configuration file."""

    config_obj = load_config(config)
    if not config_obj.scenarios:
        typer.echo("No scenarios defined.")
        raise typer.Exit()

    for scenario_cfg in config_obj.scenarios:
        status = "enabled" if scenario_cfg.enabled else "disabled"
        source_path = scenario_cfg.resolve_source_path(config_obj.source_directory)
        typer.echo(f"{scenario_cfg.id} [{status}] -> {source_path}")


def _describe_scenario(scenario_ir, scenario_cfg: ScenarioConfig, target_path: Path) -> None:
    nodes_count = len(scenario_ir.nodes)
    filters_count = sum(len(node.filters) for node in scenario_ir.nodes.values())
    calculated_count = sum(len(node.calculated_attributes) for node in scenario_ir.nodes.values())
    logical_model_status = "present" if scenario_ir.logical_model else "absent"

    typer.echo(f"  Scenario ID: {scenario_ir.metadata.scenario_id}")
    typer.echo(f"  Nodes parsed: {nodes_count}")
    typer.echo(f"  Filters detected: {filters_count}")
    typer.echo(f"  Calculated columns: {calculated_count}")
    typer.echo(f"  Logical model: {logical_model_status}")
    typer.echo(f"  Planned SQL target: {target_path}")


__all__ = ["app", "convert", "list_scenarios"]

