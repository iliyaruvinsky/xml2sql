"""SQL renderer that converts Scenario IR to Snowflake SQL."""

from __future__ import annotations

from collections import defaultdict, deque
from dataclasses import dataclass
from typing import Dict, List, Optional, Set

from ..domain import (
    AggregationNode,
    AggregationSpec,
    DataSource,
    Expression,
    ExpressionType,
    JoinNode,
    JoinType,
    Node,
    NodeKind,
    Predicate,
    PredicateKind,
    Scenario,
    UnionNode,
)
from .function_translator import translate_hana_function, translate_raw_formula


@dataclass(slots=True)
class RenderContext:
    """Context for SQL rendering."""

    scenario: Scenario
    schema_overrides: Dict[str, str]
    client: str
    language: str
    cte_aliases: Dict[str, str]
    warnings: List[str]
    currency_udf: Optional[str] = None
    currency_schema: Optional[str] = None
    currency_table: Optional[str] = None

    def __init__(
        self,
        scenario: Scenario,
        schema_overrides: Optional[Dict[str, str]] = None,
        client: Optional[str] = None,
        language: Optional[str] = None,
        currency_udf: Optional[str] = None,
        currency_schema: Optional[str] = None,
        currency_table: Optional[str] = None,
    ):
        self.scenario = scenario
        self.schema_overrides = schema_overrides or {}
        self.client = client or scenario.metadata.default_client or "PROD"
        self.language = language or scenario.metadata.default_language or "EN"
        self.cte_aliases = {}
        self.warnings = []
        self.currency_udf = currency_udf
        self.currency_schema = currency_schema
        self.currency_table = currency_table

    def get_cte_alias(self, node_id: str) -> str:
        """Get or create a CTE alias for a node."""
        if node_id not in self.cte_aliases:
            normalized = node_id.lower().replace("_", "_")
            self.cte_aliases[node_id] = normalized
        return self.cte_aliases[node_id]

    def resolve_schema(self, schema_name: str) -> str:
        """Resolve schema name with overrides."""
        return self.schema_overrides.get(schema_name, schema_name)


def render_scenario(
    scenario: Scenario,
    schema_overrides: Optional[Dict[str, str]] = None,
    client: Optional[str] = None,
    language: Optional[str] = None,
    create_view: bool = False,
    view_name: Optional[str] = None,
    currency_udf: Optional[str] = None,
    currency_schema: Optional[str] = None,
    currency_table: Optional[str] = None,
    return_warnings: bool = False,
    validate: bool = True,
) -> str | tuple[str, list[str]]:
    """Render a Scenario IR to Snowflake SQL.
    
    Args:
        return_warnings: If True, returns (sql, warnings) tuple; otherwise returns sql string only.
        validate: If True, validate the generated SQL (default: True).
    
    Returns:
        SQL string, or (sql, warnings) tuple if return_warnings=True.
    """

    ctx = RenderContext(
        scenario,
        schema_overrides,
        client,
        language,
        currency_udf,
        currency_schema,
        currency_table,
    )
    ordered_nodes = _topological_sort(scenario)
    ctes: List[str] = []

    for node_id in ordered_nodes:
        if node_id in scenario.data_sources:
            continue
        if node_id not in scenario.nodes:
            ctx.warnings.append(f"Node {node_id} referenced but not found")
            continue
        node = scenario.nodes[node_id]
        cte_sql = _render_node(ctx, node)
        if cte_sql:
            cte_alias = ctx.get_cte_alias(node_id)
            ctes.append(f"  {cte_alias} AS (\n    {cte_sql.replace(chr(10), chr(10) + '    ')}\n  )")

    final_node_id = _find_final_node(scenario, ordered_nodes)
    if not final_node_id:
        # Critical error: Missing final node
        error_msg = "No terminal node found - cannot generate valid SQL"
        ctx.warnings.append(error_msg)
        # If no CTEs exist, create a placeholder to avoid invalid SQL
        if not ctes:
            placeholder_cte = "  final AS (\n    SELECT NULL AS placeholder\n  )"
            ctes.append(placeholder_cte)
            ctx.cte_aliases["final"] = "final"
        final_select = "SELECT * FROM final" if ctes else ""
        sql = _assemble_sql(ctes, final_select, ctx.warnings)
        # Note: We still return SQL with placeholder, but validation will catch this as error
        if validate:
            from .validator import ValidationResult
            validation_result = ValidationResult()
            validation_result.add_error(error_msg, "MISSING_FINAL_NODE")
            if validation_result.has_errors:
                error_msg_full = "; ".join([str(e) for e in validation_result.errors])
                raise ValueError(f"SQL validation failed: {error_msg_full}")
        return (sql, ctx.warnings) if return_warnings else sql

    # Check if final_node_id is a data source (not a rendered CTE)
    if final_node_id in scenario.data_sources:
        # Use the data source directly in FROM clause
        from_clause = _render_from(ctx, final_node_id)
        
        # If we have a logical model, select its attributes instead of *
        if scenario.logical_model and scenario.logical_model.attributes:
            select_items: List[str] = []
            table_alias = final_node_id
            
            # Add regular attributes from logical model
            for attr in scenario.logical_model.attributes:
                if attr.column_name:
                    col_expr = f"{from_clause}.{attr.column_name}"
                    select_items.append(f"{col_expr} AS {_quote_identifier(attr.name)}")
            
            # Add calculated attributes from logical model
            for calc_attr in scenario.logical_model.calculated_attributes:
                # For RAW expressions, qualify column references with table name
                if calc_attr.expression.expression_type == ExpressionType.RAW:
                    formula = calc_attr.expression.value
                    # Replace quoted column names with qualified table.column references
                    import re
                    def qualify_column(match):
                        col_name = match.group(1)
                        return f"{from_clause}.{_quote_identifier(col_name)}"
                    formula = re.sub(r'"([^"]+)"', qualify_column, formula)
                    # Translate HANA syntax to Snowflake
                    from .function_translator import translate_raw_formula
                    # Create a minimal context for translation
                    class FormulaContext:
                        def __init__(self, ctx):
                            self.client = ctx.client
                            self.language = ctx.language
                    formula_ctx = FormulaContext(ctx)
                    col_expr = translate_raw_formula(formula, formula_ctx)
                else:
                    col_expr = _render_expression(ctx, calc_attr.expression, from_clause)
                select_items.append(f"{col_expr} AS {_quote_identifier(calc_attr.name)}")
            
            if select_items:
                select_clause = ",\n    ".join(select_items)
                final_select = f"SELECT\n    {select_clause}\nFROM {from_clause}"
            else:
                final_select = f"SELECT * FROM {from_clause}"
        else:
            final_select = f"SELECT * FROM {from_clause}"
        
        sql = _assemble_sql(ctes, final_select, ctx.warnings)
        return (sql, ctx.warnings) if return_warnings else sql

    final_alias = ctx.cte_aliases.get(final_node_id, "final")
    # If final_node_id is not in cte_aliases, the node wasn't rendered as a CTE
    # Create a placeholder CTE to avoid invalid SQL
    if final_node_id not in ctx.cte_aliases:
        if not ctes:
            placeholder_cte = "  final AS (\n    SELECT NULL AS placeholder\n  )"
            ctes.append(placeholder_cte)
            ctx.cte_aliases["final"] = "final"
            ctx.warnings.append(f"Final node {final_node_id} referenced but not found in CTEs; using placeholder CTE")
        else:
            # If we have CTEs but final_node_id is missing, use the last CTE
            ctx.warnings.append(f"Final node {final_node_id} referenced but not found in CTEs; using last CTE")
            final_alias = list(ctx.cte_aliases.values())[-1] if ctx.cte_aliases else "final"
    final_select = f"SELECT * FROM {final_alias}"

    if create_view:
        view = view_name or scenario.metadata.scenario_id
        sql = _assemble_sql(ctes, final_select, ctx.warnings, view_name=view)
    else:
        sql = _assemble_sql(ctes, final_select, ctx.warnings)
    
    # Validate SQL if enabled
    if validate:
        from .validator import (
            analyze_query_complexity,
            validate_performance,
            validate_query_completeness,
            validate_snowflake_specific,
            validate_sql_structure,
        )
        
        structure_result = validate_sql_structure(sql)
        completeness_result = validate_query_completeness(scenario, sql, ctx)
        performance_result = validate_performance(sql, scenario)
        snowflake_result = validate_snowflake_specific(sql)
        complexity_result = analyze_query_complexity(sql, scenario)
        
        # Merge validation results
        all_results = [structure_result, completeness_result, performance_result, snowflake_result, complexity_result]
        if any(r.has_errors for r in all_results):
            # Collect all errors
            all_errors = []
            for r in all_results:
                all_errors.extend(r.errors)
            error_msg = "; ".join([str(e) for e in all_errors])
            raise ValueError(f"SQL validation failed: {error_msg}")
        
        # Merge warnings into context warnings
        for result in all_results:
            for warning in result.warnings:
                ctx.warnings.append(warning.message)
            for info in result.info:
                ctx.warnings.append(f"Info: {info.message}")
    
    return (sql, ctx.warnings) if return_warnings else sql


def _topological_sort(scenario: Scenario) -> List[str]:
    """Topologically sort nodes and data sources by dependencies."""

    in_degree: Dict[str, int] = defaultdict(int)
    graph: Dict[str, List[str]] = defaultdict(list)
    all_ids: Set[str] = set(scenario.data_sources.keys()) | set(scenario.nodes.keys())

    for node_id, node in scenario.nodes.items():
        all_ids.add(node_id)
        for input_id in node.inputs:
            input_id = input_id.lstrip("#")
            if input_id in all_ids:
                graph[input_id].append(node_id)
                in_degree[node_id] += 1
            else:
                in_degree[node_id] += 0

    for ds_id in scenario.data_sources:
        in_degree[ds_id] = 0

    queue = deque([node_id for node_id in all_ids if in_degree[node_id] == 0])
    result: List[str] = []

    while queue:
        current = queue.popleft()
        result.append(current)
        for dependent in graph[current]:
            in_degree[dependent] -= 1
            if in_degree[dependent] == 0:
                queue.append(dependent)

    if len(result) < len(all_ids):
        missing = all_ids - set(result)
        return result + list(missing)

    return result


def _find_final_node(scenario: Scenario, ordered: List[str]) -> Optional[str]:
    """Find the terminal node (one that no other node depends on)."""

    if not ordered:
        return None

    if scenario.logical_model and scenario.logical_model.base_node_id:
        return scenario.logical_model.base_node_id

    referenced: Set[str] = set()
    for node in scenario.nodes.values():
        for input_id in node.inputs:
            referenced.add(input_id.lstrip("#"))

    for node_id in reversed(ordered):
        if node_id not in referenced and node_id in scenario.nodes:
            return node_id

    return ordered[-1] if ordered else None


def _render_node(ctx: RenderContext, node: Node) -> str:
    """Render a single node to SQL SELECT statement."""

    if node.kind == NodeKind.PROJECTION:
        return _render_projection(ctx, node)
    if node.kind == NodeKind.JOIN and isinstance(node, JoinNode):
        return _render_join(ctx, node)
    if node.kind == NodeKind.AGGREGATION and isinstance(node, AggregationNode):
        return _render_aggregation(ctx, node)
    if node.kind == NodeKind.UNION and isinstance(node, UnionNode):
        return _render_union(ctx, node)
    if node.kind == NodeKind.CALCULATION:
        return _render_calculation(ctx, node)

    # Critical error: Unsupported node type
    error_msg = f"Unsupported node type {node.kind} - conversion not possible"
    ctx.warnings.append(error_msg)
    # Still try to render something, but validation will catch this as error
    return "SELECT 1 AS placeholder"


def _render_projection(ctx: RenderContext, node: Node) -> str:
    """Render a projection node."""

    if not node.inputs:
        ctx.warnings.append(f"Projection {node.node_id} has no inputs")
        return "SELECT 1 AS placeholder"

    input_id = node.inputs[0].lstrip("#")
    from_clause = _render_from(ctx, input_id)

    columns: List[str] = []
    for mapping in node.mappings:
        col_expr = _render_expression(ctx, mapping.expression, from_clause)
        columns.append(f"{col_expr} AS {_quote_identifier(mapping.target_name)}")

    for calc_name, calc_attr in node.calculated_attributes.items():
        calc_expr = _render_expression(ctx, calc_attr.expression, from_clause)
        columns.append(f"{calc_expr} AS {_quote_identifier(calc_name)}")

    if not columns:
        columns = ["*"]

    select_clause = ",\n    ".join(columns)
    where_clause = _render_filters(ctx, node.filters, from_clause)

    sql = f"SELECT\n    {select_clause}\nFROM {from_clause}"
    if where_clause:
        sql += f"\nWHERE {where_clause}"

    return sql


def _render_join(ctx: RenderContext, node: JoinNode) -> str:
    """Render a join node."""

    if len(node.inputs) < 2:
        ctx.warnings.append(f"Join {node.node_id} has fewer than 2 inputs")
        return "SELECT 1 AS placeholder"

    left_id = node.inputs[0].lstrip("#")
    right_id = node.inputs[1].lstrip("#")
    left_alias = ctx.get_cte_alias(left_id)
    right_alias = ctx.get_cte_alias(right_id)

    join_type_str = _map_join_type_to_sql(node.join_type)

    conditions: List[str] = []
    for condition in node.conditions:
        left_expr = _render_expression(ctx, condition.left, left_alias)
        right_expr = _render_expression(ctx, condition.right, right_alias)
        conditions.append(f"{left_expr} = {right_expr}")

    if not conditions:
        # Critical error: Cartesian product
        error_msg = f"Join {node.node_id} creates cartesian product (no join conditions)"
        ctx.warnings.append(error_msg)
        # Still generate SQL with 1=1 but mark as critical issue
        conditions = ["1=1"]

    on_clause = " AND ".join(conditions)

    columns: List[str] = []
    seen_targets = set()  # Track columns already added to avoid duplicates
    for mapping in node.mappings:
        # Skip hidden columns - only include if in view_attributes list
        if node.view_attributes and mapping.target_name not in node.view_attributes:
            continue
        # Skip duplicate target names (keep first occurrence)
        if mapping.target_name in seen_targets:
            continue
        seen_targets.add(mapping.target_name)
        # Determine which alias to use based on source_node
        if mapping.source_node:
            # source_node is like "#Aggregation_1" or "#Projection_2"
            source_node_id = mapping.source_node.lstrip("#")
            source_alias = ctx.get_cte_alias(source_node_id)
        else:
            # Default to left alias if no source_node specified
            source_alias = left_alias
        source_expr = _render_expression(ctx, mapping.expression, source_alias)
        columns.append(f"{source_expr} AS {_quote_identifier(mapping.target_name)}")

    for calc_name, calc_attr in node.calculated_attributes.items():
        calc_expr = _render_expression(ctx, calc_attr.expression, left_alias)
        columns.append(f"{calc_expr} AS {_quote_identifier(calc_name)}")

    if not columns:
        columns = [f"{left_alias}.*", f"{right_alias}.*"]

    select_clause = ",\n    ".join(columns)
    where_clause = _render_filters(ctx, node.filters, left_alias)

    sql = f"SELECT\n    {select_clause}\nFROM {left_alias}\n{join_type_str} JOIN {right_alias} ON {on_clause}"
    if where_clause:
        sql += f"\nWHERE {where_clause}"

    return sql


def _render_aggregation(ctx: RenderContext, node: AggregationNode) -> str:
    """Render an aggregation node."""

    if not node.inputs:
        ctx.warnings.append(f"Aggregation {node.node_id} has no inputs")
        return "SELECT 1 AS placeholder"

    input_id = node.inputs[0].lstrip("#")
    from_clause = _render_from(ctx, input_id)

    group_by_cols: List[str] = []
    for col_name in node.group_by:
        col_expr = _render_column_ref(ctx, col_name, from_clause)
        group_by_cols.append(col_expr)

    select_items: List[str] = []
    for col_name in node.group_by:
        col_expr = _render_column_ref(ctx, col_name, from_clause)
        select_items.append(f"{col_expr} AS {_quote_identifier(col_name)}")

    for agg_spec in node.aggregations:
        agg_func = agg_spec.function.upper()
        agg_expr = _render_expression(ctx, agg_spec.expression, from_clause)
        select_items.append(f"{agg_func}({agg_expr}) AS {_quote_identifier(agg_spec.target_name)}")

    if not select_items:
        select_items = ["*"]

    select_clause = ",\n    ".join(select_items)
    where_clause = _render_filters(ctx, node.filters, from_clause)

    sql = f"SELECT\n    {select_clause}\nFROM {from_clause}"
    if where_clause:
        sql += f"\nWHERE {where_clause}"
    if group_by_cols:
        sql += f"\nGROUP BY {', '.join(group_by_cols)}"

    return sql


def _render_union(ctx: RenderContext, node: UnionNode) -> str:
    """Render a union node."""

    if len(node.inputs) < 2:
        ctx.warnings.append(f"Union {node.node_id} has fewer than 2 inputs")
        return "SELECT 1 AS placeholder"

    union_queries: List[str] = []
    target_columns = list(dict.fromkeys(mapping.target_name for mapping in node.mappings)) if node.mappings else []

    for input_id in node.inputs:
        input_id = input_id.lstrip("#")
        input_alias = ctx.get_cte_alias(input_id) if input_id in ctx.cte_aliases else _render_from(ctx, input_id)

        input_mappings = [m for m in node.mappings if (m.source_node or "").lstrip("#") == input_id]
        if input_mappings and target_columns:
            select_items: List[str] = []
            for target_col in target_columns:
                mapping = next((m for m in input_mappings if m.target_name == target_col), None)
                if mapping:
                    col_expr = _render_expression(ctx, mapping.expression, input_alias)
                    select_items.append(f"{col_expr} AS {_quote_identifier(target_col)}")
                else:
                    select_items.append(f"NULL AS {_quote_identifier(target_col)}")
            select_clause = ",\n    ".join(select_items)
        else:
            select_clause = "*"

        union_queries.append(f"SELECT\n    {select_clause}\nFROM {input_alias}")

    union_keyword = "UNION ALL" if node.union_all else "UNION"
    sql = f"\n{union_keyword}\n".join(union_queries)

    if node.filters:
        where_clause = _render_filters(ctx, node.filters, None)
        if where_clause:
            sql = f"SELECT * FROM (\n{sql}\n) AS union_result\nWHERE {where_clause}"

    return sql


def _render_calculation(ctx: RenderContext, node: Node) -> str:
    """Render a calculation node (fallback for unsupported node types)."""

    if not node.inputs:
        ctx.warnings.append(f"Calculation {node.node_id} has no inputs")
        return "SELECT 1 AS placeholder"

    input_id = node.inputs[0].lstrip("#")
    from_clause = _render_from(ctx, input_id)

    columns: List[str] = []
    for mapping in node.mappings:
        col_expr = _render_expression(ctx, mapping.expression, from_clause)
        columns.append(f"{col_expr} AS {_quote_identifier(mapping.target_name)}")

    if not columns:
        columns = ["*"]

    select_clause = ",\n    ".join(columns)
    where_clause = _render_filters(ctx, node.filters, from_clause)

    sql = f"SELECT\n    {select_clause}\nFROM {from_clause}"
    if where_clause:
        sql += f"\nWHERE {where_clause}"

    return sql


def _render_from(ctx: RenderContext, input_id: str) -> str:
    """Render FROM clause for a data source or CTE."""

    if input_id in ctx.scenario.data_sources:
        ds = ctx.scenario.data_sources[input_id]
        schema = ctx.resolve_schema(ds.schema_name)
        if schema:
            return f"{_quote_identifier(schema)}.{_quote_identifier(ds.object_name)}"
        return _quote_identifier(ds.object_name)

    if input_id in ctx.cte_aliases:
        return ctx.cte_aliases[input_id]

    return ctx.get_cte_alias(input_id)


def _render_expression(ctx: RenderContext, expr: Expression, table_alias: Optional[str] = None) -> str:
    """Render an expression to SQL."""

    if expr.expression_type == ExpressionType.COLUMN:
        return _render_column_ref(ctx, expr.value, table_alias)
    if expr.expression_type == ExpressionType.LITERAL:
        return _render_literal(expr.value, expr.data_type)
    if expr.expression_type == ExpressionType.RAW:
        translated = translate_raw_formula(expr.value, ctx)
        if translated != expr.value:
            return translated
        return _substitute_placeholders(expr.value, ctx)
    if expr.expression_type == ExpressionType.FUNCTION:
        return _render_function(ctx, expr, table_alias)

    ctx.warnings.append(f"Unsupported expression type: {expr.expression_type}")
    return "NULL"


def _render_column_ref(ctx: RenderContext, column_name: str, table_alias: Optional[str] = None) -> str:
    """Render a column reference."""

    if table_alias:
        return f"{table_alias}.{_quote_identifier(column_name)}"
    return _quote_identifier(column_name)


def _render_literal(value: str, data_type: Optional[object] = None) -> str:
    """Render a literal value."""

    if value.isdigit() or (value.startswith("-") and value[1:].isdigit()):
        return value
    if data_type and hasattr(data_type, "type"):
        from ..domain.types import SnowflakeType

        if data_type.type == SnowflakeType.DATE:
            if len(value) == 8 and value.isdigit():
                return f"TO_DATE('{value}', 'YYYYMMDD')"
            return f"'{value}'::DATE"
        if data_type.type == SnowflakeType.TIMESTAMP_NTZ:
            return f"'{value}'::TIMESTAMP_NTZ"

    return f"'{value.replace(chr(39), chr(39) + chr(39))}'"


def _render_function(ctx: RenderContext, expr: Expression, table_alias: Optional[str] = None) -> str:
    """Render a function call expression."""

    func_name = expr.value.upper()
    args = expr.arguments or []

    class FuncContext:
        def __init__(self, ctx, table_alias):
            self.ctx = ctx
            self.table_alias = table_alias
            self.client = ctx.client
            self.language = ctx.language

        def _render_expression(self, expr, alias):
            return _render_expression(self.ctx, expr, alias or self.table_alias)

    func_ctx = FuncContext(ctx, table_alias)
    translated = translate_hana_function(func_name, args, func_ctx)
    if translated:
        return translated

    arg_strs = [_render_expression(ctx, arg, table_alias) for arg in args]
    return f"{func_name}({', '.join(arg_strs)})"


def _render_filters(ctx: RenderContext, filters: List[Predicate], table_alias: Optional[str] = None) -> str:
    """Render WHERE clause from filters."""

    if not filters:
        return ""

    conditions: List[str] = []
    for pred in filters:
        if pred.kind == PredicateKind.COMPARISON:
            left = _render_expression(ctx, pred.left, table_alias)
            op = pred.operator or "="
            if pred.right:
                right = _render_expression(ctx, pred.right, table_alias)
                conditions.append(f"{left} {op} {right}")
        elif pred.kind == PredicateKind.IS_NULL:
            left = _render_expression(ctx, pred.left, table_alias)
            conditions.append(f"{left} IS NULL")
        else:
            ctx.warnings.append(f"Unsupported predicate kind: {pred.kind}")

    return " AND ".join(conditions) if conditions else ""


def _map_join_type_to_sql(join_type: JoinType) -> str:
    """Map JoinType enum to SQL JOIN keyword."""

    mapping = {
        JoinType.INNER: "INNER",
        JoinType.LEFT_OUTER: "LEFT OUTER",
        JoinType.RIGHT_OUTER: "RIGHT OUTER",
        JoinType.FULL_OUTER: "FULL OUTER",
    }
    return mapping.get(join_type, "INNER")


def _render_currency_conversion(
    ctx: RenderContext,
    amount_expr: str,
    source_currency_expr: str,
    target_currency_expr: str,
    reference_date_expr: str,
    rate_type: str = "M",
) -> str:
    """Render currency conversion using UDF or table join."""

    if ctx.currency_udf:
        schema_prefix = f"{ctx.currency_schema}." if ctx.currency_schema else ""
        return f"{schema_prefix}{ctx.currency_udf}({amount_expr}, {source_currency_expr}, {target_currency_expr}, {reference_date_expr}, '{rate_type}', '{ctx.client}')"

    if ctx.currency_table:
        schema_prefix = f"{ctx.currency_schema}." if ctx.currency_schema else ""
        ctx.warnings.append("Currency conversion via table join not yet implemented; using UDF placeholder")
        return f"-- TODO: Currency conversion for {amount_expr} from {source_currency_expr} to {target_currency_expr}"

    ctx.warnings.append("Currency conversion requested but no UDF or table configured")
    return amount_expr


def _substitute_placeholders(text: str, ctx: RenderContext) -> str:
    """Replace $$client$$ and $$language$$ placeholders."""

    result = text.replace("$$client$$", ctx.client)
    result = result.replace("$$language$$", ctx.language)
    return result


def _quote_identifier(name: str) -> str:
    """Quote a SQL identifier if needed."""

    if name and name[0].isalpha() and name.replace("_", "").isalnum():
        return name.upper()
    return f'"{name.upper()}"'


def _assemble_sql(ctes: List[str], final_select: str, warnings: List[str], view_name: Optional[str] = None) -> str:
    """Assemble final SQL with CTEs, warnings, and optional CREATE VIEW."""

    lines: List[str] = []

    if warnings:
        lines.append("-- Warnings:")
        for warning in warnings:
            lines.append(f"--   {warning}")
        lines.append("")

    if ctes:
        lines.append("WITH")
        lines.append(",\n".join(ctes))
        lines.append("")

    if view_name:
        lines.append(f"CREATE OR REPLACE VIEW {_quote_identifier(view_name)} AS")
        lines.append(final_select)
    else:
        lines.append(final_select)

    return "\n".join(lines)


__all__ = ["render_scenario"]

