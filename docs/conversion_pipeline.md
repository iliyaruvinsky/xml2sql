# Parser & SQL Generation Strategy

## Overview
Leverage the intermediate representation to transform SAP HANA calculation-view XML into Snowflake-ready SQL artifacts stored under `Target (SQL Scripts)`.

## Parser Pipeline
1. **Load XML** from `Source (XML Files)` using `lxml.etree` for namespace-aware parsing.
2. **Normalise namespaces** (strip `Calculation:` prefix) to ease XPath queries.
3. **Scenario Builder**
   - Extract scenario-level metadata (id, default client/language, privilege flags).
   - Register `DataSource` entries with schema/object references.
4. **Node Extraction**
   - Iterate `calculationViews/calculationView` elements in document order.
   - For each node:
     - Identify `xsi:type` and dispatch via `NodeFactory` to construct `ProjectionNode`, `JoinNode`, etc.
     - Parse `<viewAttributes>`, `<calculatedViewAttributes>`, `<input>` mappings, and filters into `Expression` / `Predicate` objects.
     - Maintain dependency graph by referencing source ids and upstream node ids (`#Projection_1`).
5. **Logical Model Parsing**
   - Map `<logicalModel>` attributes/measures to IR `Attribute` / `Measure` objects, including currency conversion definitions.
6. **Topological Ordering**
   - Perform dependency resolution to ensure generation order (Kahn algorithm). Detect cycles or missing references early.
7. **Validation**
   - Ensure all logical model references exist in node outputs.
   - Flag unsupported constructs (e.g., union, hierarchy) for future handling.

## SQL Generation Flow
1. **Context Setup**
   - Accept IR `Scenario` and optional runtime parameters (client, language, schema overrides).
   - Prepare symbol table mapping node outputs to CTE aliases.
2. **CTE Builder**
   - For each node in topological order:
     - Render SELECT statement representing node output.
     - Use consistent aliasing (`projection_1`, `join_2`, etc.).
     - Propagate filters into `WHERE` or `QUALIFY` clauses.
     - Handle calculated attributes via `ExpressionRenderer` translating HANA functions to Snowflake SQL (`if` → `IFF`/`CASE`, string functions mapping, etc.).
     - Join nodes produce explicit `JOIN` clauses with translated join types.
   - Accumulate CTE text segments.
3. **Measure Handling**
   - Final SELECT reads from terminal node (e.g., `join_3`).
   - Apply aggregations if logical model indicates measures with `aggregationType`.
   - Maintain column ordering per logical model attributes/measures.
4. **Currency Conversion Strategy**
   - Represent conversion logic as calls to Snowflake UDFs or JOIN against pre-staged rate tables.
   - Parser emits `CurrencyConversion` metadata; SQL generator decides whether to inline conversion (if rules available) or flag TODO comment when lacking configuration.
5. **Output Assembly**
   - Combine CTEs and final SELECT into `CREATE OR REPLACE VIEW <target>` script or plain SELECT saved under `Target (SQL Scripts)` with consistent naming (e.g., `<scenario_id>.sql`).
   - Optionally emit ancillary SQL (e.g., UDF definitions) in separate files when required.

## Supporting Components
- **ExpressionRenderer**: translates IR expressions to Snowflake SQL, with registry for function mappings and fallback warnings.
- **ParameterResolver**: replaces placeholders (`$$client$$`, `$$language$$`) with provided values or binds them as Snowflake session variables.
- **Error Reporter**: collects unsupported features, missing mappings, or ambiguous conversions; output as comments in SQL and structured logs.
- **Testing Utilities**: fixtures loading sample XML → IR → SQL, with snapshot tests stored under `tests/fixtures/`.

## File & Directory Conventions
- Source XMLs: `Source (XML Files)/*.xml|*.md|*.txt`
- Generated SQL: `Target (SQL Scripts)/<scenario_id>.sql`
- Documentation (this plan): `docs/`
- Future Python package: `src/xml_to_sql/`

## Next Implementation Steps
1. Implement IR data classes (`dataclasses` or `pydantic`).
2. Build parser modules for data sources and projection/join nodes.
3. Create SQL renderer for projections/joins and stub currency conversion translator.
4. Develop CLI wrapper to process a folder of XMLs into SQL targets.

