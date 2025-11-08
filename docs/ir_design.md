# Intermediate Representation (IR) Blueprint

## Goals
- Capture SAP HANA calculation-view semantics in a serialisable form.
- Decouple XML parsing from SQL generation.
- Support incremental extension to new node types and metadata.

## Core Entities

### Scenario
- `id`: calculation view identifier.
- `metadata`: attributes such as `default_client`, `default_language`, privilege flags.
- `data_sources`: map of source id → `DataSource`.
- `nodes`: ordered dictionary of node id → `Node` subclass.
- `logical_model`: measures and attributes exposed externally.

### DataSource
- `id`, `schema`, `object_name`, `type` (table, view).
- `columns`: optional explicit column list when `allViewAttributes` is false.

### Node (abstract)
- `id`, `type` (projection, join, aggregation, union, rank, etc.).
- `inputs`: list of input node references (source ids or node ids).
- `mappings`: output attribute name → `Expression` (renamed, literal, calc).
- `filters`: list of `Predicate` objects applied at node level.
- `properties`: node-specific metadata (e.g., join type, join order).

#### ProjectionNode
- Inherits `Node`.
- `inputs` length = 1 (source or node).
- `mappings`: direct attribute passthrough or expressions.

#### JoinNode
- `join_type`: inner, left_outer, etc.
- `conditions`: list of `JoinCondition` (left attr, right attr, operator).
- `calculated_attributes`: optional derived columns defined inside join.

#### AggregationNode (for future XMLs)
- `group_by`: ordered list of attributes.
- `aggregations`: output name → aggregation expression.

#### CalculationNode (generic formula container)
- `expressions`: dictionary output attr → `Expression`.
- Used for calculated columns like `Calc_KWBTR`.

### Expression
- `type`: column_ref, literal, function_call, case_when.
- `value`: payload dependent on type (e.g., column path, literal value).
- `metadata`: hints such as original HANA function signature, required casts.

### Predicate
- `kind`: comparison, between, in_list, is_null.
- `left`, `operator`, `right`: references to `Expression` objects.
- For AccessControl filters, store `including` flag.

### Measure / Attribute (Logical Model)
- `id`, `source_column`, `order`, `semantic_type`.
- `aggregation`: sum, min, etc.
- `currency_handling`: currency attribute, fixed currency, conversion info.
- Keep currency conversion block serialized for translation layer.

### CurrencyConversion
- `source_currency_expr`
- `target_currency_expr` or literal.
- `client_expr`, `reference_date_expr`.
- `rate_type`, `schema`.

## Relationships
- Nodes reference other nodes by id; the IR stores topological order for generation.
- Logical model attributes reference node outputs (usually final join node).
- Currency conversions refer to measures defined in logical model.

## Serialization
- Provide JSON/YAML dump for debugging and unit tests.
- Ensure IR objects are hashable or comparably stable to support caching.

## Extensibility Hooks
- `NodeFactory` maps XML `xsi:type` to Node subclass.
- `ExpressionFactory` handles HANA-specific functions with pluggable translators.
- Reserved fields for analytic privilege propagation, hierarchies, parameters.

## Open Questions
- How to persist analytic privilege constraints in SQL layer?
- Strategy for placeholders (`$$client$$`, `$$language$$`) when running outside HANA.
- Best way to store column data types (collect from XML vs. catalog lookup).

