"""Translates HANA functions to Snowflake SQL equivalents."""

from __future__ import annotations

import re
from typing import List, Optional

from ..domain import Expression, ExpressionType


def translate_hana_function(func_name: str, args: List[Expression], ctx) -> str:
    """Translate a HANA function call to Snowflake SQL."""

    func_name_upper = func_name.upper()
    arg_strs = [ctx._render_expression(arg, ctx.table_alias) for arg in args] if hasattr(ctx, "_render_expression") else []

    if func_name_upper == "IF":
        if len(args) >= 3:
            condition = arg_strs[0] if arg_strs else "NULL"
            then_expr = arg_strs[1] if len(arg_strs) > 1 else "NULL"
            else_expr = arg_strs[2] if len(arg_strs) > 2 else "NULL"
            return f"IFF({condition}, {then_expr}, {else_expr})"

    if func_name_upper in {"CASE", "CASE_WHEN"}:
        if len(args) >= 2:
            parts: List[str] = ["CASE"]
            i = 0
            while i < len(args) - 1:
                parts.append(f"WHEN {arg_strs[i]} THEN {arg_strs[i + 1]}")
                i += 2
            if i < len(args):
                parts.append(f"ELSE {arg_strs[i]}")
            parts.append("END")
            return " ".join(parts)

    if func_name_upper == "SUBSTRING" or func_name_upper == "SUBSTR":
        if len(args) >= 2:
            return f"SUBSTRING({arg_strs[0]}, {arg_strs[1]}{f', {arg_strs[2]}' if len(args) > 2 else ''})"

    if func_name_upper in {"CONCAT", "CONCATENATE"}:
        if len(args) >= 2:
            return " || ".join(f"COALESCE({arg}, '')" for arg in arg_strs)

    if func_name_upper == "LENGTH":
        if args:
            return f"LENGTH({arg_strs[0]})"

    if func_name_upper in {"UPPER", "UCASE"}:
        if args:
            return f"UPPER({arg_strs[0]})"

    if func_name_upper in {"LOWER", "LCASE"}:
        if args:
            return f"LOWER({arg_strs[0]})"

    if func_name_upper == "TRIM":
        if args:
            return f"TRIM({arg_strs[0]})"

    if func_name_upper in {"ROUND", "CEIL", "FLOOR", "ABS"}:
        if args:
            return f"{func_name_upper}({arg_strs[0]}{f', {arg_strs[1]}' if len(args) > 1 else ''})"

    if func_name_upper in {"COALESCE", "NVL", "IFNULL"}:
        if args:
            return f"COALESCE({', '.join(arg_strs)})"

    if func_name_upper == "TO_DATE":
        if args:
            date_format = arg_strs[1] if len(args) > 1 else "'YYYYMMDD'"
            return f"TO_DATE({arg_strs[0]}, {date_format})"

    if func_name_upper == "TO_TIMESTAMP":
        if args:
            ts_format = f", {arg_strs[1]}" if len(args) > 1 else ""
            return f"TO_TIMESTAMP({arg_strs[0]}{ts_format})"

    return None


def translate_raw_formula(formula: str, ctx) -> str:
    """Translate a raw HANA formula expression to Snowflake SQL."""

    result = formula

    if not result:
        return "NULL"

    result = _substitute_placeholders(result, ctx)

    result = _translate_if_statements(result, ctx)
    result = _translate_string_concatenation(result)
    result = _translate_column_references(result, ctx)

    return result


def _substitute_placeholders(text: str, ctx) -> str:
    """Replace $$client$$ and $$language$$ placeholders."""
    result = text.replace("$$client$$", getattr(ctx, "client", "PROD"))
    result = result.replace("$$language$$", getattr(ctx, "language", "EN"))
    return result


def _translate_if_statements(formula: str, ctx) -> str:
    """Translate HANA if() function calls to Snowflake IFF()."""

    pattern = r'if\s*\(\s*([^,]+)\s*,\s*([^,]+)\s*,\s*([^)]+)\s*\)'
    def replace_if(match):
        condition = match.group(1).strip()
        then_expr = match.group(2).strip()
        else_expr = match.group(3).strip()
        return f"IFF({condition}, {then_expr}, {else_expr})"

    return re.sub(pattern, replace_if, formula, flags=re.IGNORECASE)


def _translate_string_concatenation(formula: str) -> str:
    """Translate HANA string concatenation to Snowflake || operator."""

    result = formula
    # Handle 'string'+column and column+'string' patterns
    # Replace '+ with || (string literal + something)
    result = re.sub(r"'\s*\+\s*", "' || ", result)
    # Replace +' with || (something + string literal)
    result = re.sub(r"\s*\+\s*'", " || '", result)
    # Replace + between non-string parts (column+column)
    result = re.sub(r'"([^"]+)"\s*\+\s*"([^"]+)"', r'"\1" || "\2"', result)
    result = re.sub(r'"([^"]+)"\s*\+\s*([^"+\s]+)', r'"\1" || \2', result)
    # Handle non-quoted column references before quoted ones
    result = re.sub(r"([^\"'\s]+)\s*\+\s*\"([^\"]+)\"", r'\1 || "\2"', result)
    return result


def _translate_column_references(formula: str, ctx) -> str:
    """Translate quoted column references to proper SQL identifiers."""

    def replace_quoted(match):
        col_name = match.group(1)
        return f'"{col_name.upper()}"'

    result = re.sub(r'"([^"]+)"', replace_quoted, formula)
    return result


__all__ = ["translate_hana_function", "translate_raw_formula"]

