# SQL Feature Support Map (v2.2.0)

This matrix summarises how the xml2sql converter (version 2.2.0) handles the SQL constructs generated from SAP HANA Calculation Views. Status definitions:

- **Supported** – Generated out-of-the-box and validated automatically.
- **Partially Supported** – Generated when present in the XML; additional manual review recommended.
- **Not Supported** – Currently rejected or requires manual implementation.

## Core Query Structure
| Feature | Converter Behaviour | Status | Notes |
|---------|--------------------|--------|-------|
| `SELECT` projections | Generated for every node; preserves logical-model ordering | Supported | Emits `CREATE OR REPLACE VIEW … AS` followed by a CTE-driven `SELECT`. |
| Common Table Expressions (`WITH` / CTEs) | Each HANA node becomes a Snowflake CTE with deterministic aliasing | Supported | Duplicate aliases prevented; validator checks structure and count. |
| Final view select | Auto-detected terminal node, rendered as final `SELECT` | Supported | Logical model determines exposed columns; warnings raised if missing. |
| Parameter placeholders (`$$client$$`, `$$language$$`) | Substituted from configuration/runtime context | Supported | Defaults: `client=PROD`, `language=EN`; override via UI/CLI. |

## Data Sources & Joins
| Feature | Converter Behaviour | Status | Notes |
|---------|--------------------|--------|-------|
| Schema-qualified tables/views | `schema.object` emitted for every data source | Supported | Empty schema/object names trigger validator warnings. |
| Projection nodes | Column passthrough, renaming, constants | Supported | Calculated attributes rendered via expression translator. |
| Join nodes (`INNER`, `LEFT OUTER`) | Rendered as Snowflake joins with translated conditions | Supported | Join type carried from XML; Cartesian products flagged by validator. |
| Other join types (`RIGHT`, `FULL`, `REFERENTIAL`, `TEXT`) | Currently normalised to the nearest supported join | Partially Supported | Most legacy ColumnViews use projections/inner/left joins. |
| `UNION ALL` | Generated for HANA union nodes | Supported | Union branches type-aligned; validator checks branch counts. |
| `UNION` (distinct) | Not auto-generated | Not Supported | Requires post-processing if distinct unions are needed. |

## Expressions & Functions
| Feature | Converter Behaviour | Status | Notes |
|---------|--------------------|--------|-------|
| Calculated attributes (`formula`) | Evaluated via `translate_raw_formula` | Supported | Covers arithmetic, comparisons, nested expressions. |
| Legacy helpers (`LEFTSTR`, `RIGHTSTR`, `in(...)`, `match(...)`, `lpad(...)`) | Translated via structured catalog to Snowflake equivalents | Supported | Introduced in v2.2.0; see regression tests for `OLD_HANA_VIEWS`. |
| HANA IF → Snowflake `IFF` | Auto-corrected and validated | Supported | Validator warns if raw `IF` remains. |
| String concatenation `+` → `||` | Auto-corrected | Supported | Validator flags legacy `+` usage. |
| Aggregations (`SUM`, `MAX`, `COUNT`, `AVG`) | Emitted from aggregation nodes with `GROUP BY` | Supported | Missing `GROUP BY` on multi-source queries raises warnings. |
| Window functions / rank nodes | Emitted when present; limited coverage | Partially Supported | HANA rank nodes convert to Snowflake window constructs; manual review advised. |
| HANA-specific functions without mapping (e.g. `WORKDAYS_BETWEEN`) | Passed through and flagged for review | Partially Supported | Validator adds informational warnings; manual adaptation required. |

## Filters & Predicates
| Feature | Converter Behaviour | Status | Notes |
|---------|--------------------|--------|-------|
| Node-level filters (`WHERE`) | Raw expressions rendered per node | Supported | Empty expressions flagged by validator. |
| Multi-branch `in(...)` predicates | Converted to Snowflake `IN` lists | Supported | Values normalised to quoted literals. |
| Complex boolean logic | Maintained as-is; parentheses preserved | Supported | Validator checks for missing WHERE clauses on multi-table queries. |

## Output & Deployment
| Feature | Converter Behaviour | Status | Notes |
|---------|--------------------|--------|-------|
| View creation script | Emits `CREATE OR REPLACE VIEW <target>` | Supported | Target name comes from scenario metadata or config overrides. |
| Downloadable SQL/XML | Available in UI & history | Supported | Includes auto-correction summary and validation logs. |
| CLI batch conversion | `xml_to_sql.cli` supports list/convert operations | Supported | Refer to `START_HERE.md` and `CLIENT_DEPLOYMENT_GUIDE.md`. |

## Validation & Auto-Correction Coverage
| Area | Highlights | Status |
|------|------------|--------|
| Structure validation | Empty SQL, missing `SELECT`, CTE structure, duplicate aliases | Supported |
| Completeness validation | Missing nodes, undefined CTE references, empty schema/object names | Supported |
| Performance validation | Cartesian joins, `SELECT *`, missing `WHERE`, aggregation checks | Supported |
| Snowflake-specific rules | Reserved keywords, identifier quoting, high CTE count, legacy helpers | Supported |
| Query complexity metrics | CTE/join/subquery counts, scenario node counts | Supported |
| Auto-correction engine | Reserved keywords, string concatenation, IF→IFF, legacy helper rewrites | Supported |

## Known Gaps / Manual Review Required
- HANA features beyond projections/joins/aggregations/unions (e.g. spatial data types, hierarchy nodes, stored procedures) are **not automatically converted**.
- Right/full outer joins, referential/text joins require manual verification.
- Validator unit tests (`tests/test_sql_validator.py`) target the legacy API; regression tests in `tests/test_sql_renderer.py` and `tests/test_parser.py` cover the v2.2.0 functionality.

For any constructs not listed above, please consult the migration catalog (`COMPREHENSIVE HANA CALCULATION VIEW XML-TO-SNOWFLAKE SQL MIGRATION CATALOG.md`) and update the conversion catalog (`src/xml_to_sql/catalog/data/functions.yaml`) as required.

