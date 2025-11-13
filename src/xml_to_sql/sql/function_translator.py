"""Translates HANA functions to Snowflake SQL equivalents."""

from __future__ import annotations

import re
from typing import List, Optional, Sequence, Tuple

from ..domain import Expression, ExpressionType
from ..catalog import FunctionRule, get_function_catalog


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
    result = _apply_catalog_rewrites(result, ctx)
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


def _apply_catalog_rewrites(formula: str, ctx) -> str:
    """Apply structured catalog rewrites for legacy helper functions."""

    catalog = get_function_catalog()
    rewritten = formula
    for rule in catalog.values():
        rewritten = _rewrite_function_calls(rewritten, rule, ctx)
    return rewritten


def _rewrite_function_calls(formula: str, rule: FunctionRule, ctx) -> str:
    """Rewrite all occurrences of a function according to the provided rule."""

    pattern = re.compile(rf"\b{re.escape(rule.name)}\s*\(", re.IGNORECASE)
    pos = 0
    parts: List[str] = []

    while True:
        match = pattern.search(formula, pos)
        if not match:
            parts.append(formula[pos:])
            break

        call_start = match.start()
        open_paren_index = match.end() - 1
        close_index, args = _extract_function_arguments(formula, open_paren_index)

        if close_index == -1 or args is None:
            # Unbalanced parentheses; keep original text
            parts.append(formula[pos:match.end()])
            pos = match.end()
            continue

        replacement = _build_replacement(rule, args, ctx)
        if replacement is None:
            parts.append(formula[pos:close_index])
        else:
            parts.append(formula[pos:call_start])
            parts.append(replacement)

        pos = close_index

    return "".join(parts)


def _extract_function_arguments(text: str, open_paren_index: int) -> Tuple[int, Optional[List[str]]]:
    """Extract argument list starting at open parenthesis index.

    Returns tuple of (index after closing parenthesis, argument list). If parentheses
    are unbalanced the second element will be None and the index -1.
    """

    depth = 0
    i = open_paren_index
    args_start = open_paren_index + 1

    while i < len(text):
        ch = text[i]
        if ch == "(":
            depth += 1
        elif ch == ")":
            depth -= 1
            if depth == 0:
                args_segment = text[args_start:i]
                return i + 1, _split_arguments(args_segment)
        i += 1

    return -1, None


def _split_arguments(arg_string: str) -> List[str]:
    """Split a comma-separated argument string, respecting nesting and quotes."""

    args: List[str] = []
    current: List[str] = []
    depth = 0
    in_quote = False
    idx = 0
    length = len(arg_string)

    while idx < length:
        ch = arg_string[idx]

        if ch == "'":
            if in_quote and idx + 1 < length and arg_string[idx + 1] == "'":
                current.append("''")
                idx += 2
                continue
            in_quote = not in_quote
            current.append(ch)
            idx += 1
            continue

        if not in_quote:
            if ch == "(":
                depth += 1
            elif ch == ")":
                depth = max(depth - 1, 0)
            elif ch == "," and depth == 0:
                argument = "".join(current).strip()
                if argument:
                    args.append(argument)
                current = []
                idx += 1
                continue

        current.append(ch)
        idx += 1

    argument = "".join(current).strip()
    if argument:
        args.append(argument)

    return args


def _build_replacement(rule: FunctionRule, args: Sequence[str], ctx) -> Optional[str]:
    """Build the replacement expression for the rule using parsed arguments."""

    handler = rule.handler.lower()

    if handler == "template" and rule.template:
        try:
            return rule.template.format(*args)
        except IndexError:
            return None

    if handler == "rename" and rule.target:
        return f"{rule.target}({', '.join(args)})"

    if handler == "regexp_like":
        if not args:
            return None
        target = args[0]
        pattern = args[1] if len(args) > 1 else "'*'"
        translated_pattern = (
            f"'^' || REPLACE(REPLACE({pattern}, '*', '.*'), '?', '.') || '$'"
        )
        return f"REGEXP_LIKE({target}, {translated_pattern})"

    if handler == "in_list":
        if len(args) < 2:
            return None
        target, *options = args
        normalized_options = [_normalize_scalar(arg) for arg in options]
        return f"({target} IN ({', '.join(normalized_options)}))"

    return None


def _normalize_scalar(argument: str) -> str:
    """Normalize scalar arguments (e.g., convert double-quoted literals to single-quoted)."""

    stripped = argument.strip()
    if stripped.startswith('"') and stripped.endswith('"'):
        inner = stripped[1:-1].replace("'", "''")
        return f"'{inner}'"
    return stripped


__all__ = ["translate_hana_function", "translate_raw_formula"]

