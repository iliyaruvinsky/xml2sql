# XML → SQL Converter Flow

```mermaid
flowchart TD
    A[Source XML Discovery]
    B[Parse Calculation Scenario]
    C[Build Intermediate Representation]
    D[Validate IR]
    E[Generate Snowflake SQL]
    F[Write Artifacts]
    G[Report & Metadata]

    subgraph Input Preparation
        A -->|Directory scan \nSource (XML Files)| B
    end

    subgraph Parsing Layer
        B -->|Normalize namespaces \n& collect data sources| C
    end

    subgraph Modeling Layer
        C -->|Nodes, expressions, measures| D
        D -->|Dependency & feature checks| E
    end

    subgraph Rendering Layer
        E -->|CTEs, joins, conversions| F
        F -->|Target (SQL Scripts) \n+ ancillary docs| G
    end

    G -->|Diagnostics \n& TODO warnings| A
```

## Step Details

1. **Source XML Discovery** – collect all calculation-view XML files from `Source (XML Files)`; capture per-file metadata for logging.
2. **Parse Calculation Scenario** – load XML with `lxml`, normalize namespaces, extract scenario metadata and data sources.
3. **Build Intermediate Representation** – instantiate IR objects (`Scenario`, `DataSource`, node graph, expressions, measures).
4. **Validate IR** – ensure dependencies resolve, highlight unsupported constructs, aggregate warnings for reporting.
5. **Generate Snowflake SQL** – traverse IR to build ordered CTEs, translate filters/calculations, prepare currency-conversion stubs.
6. **Write Artifacts** – emit SQL scripts to `Target (SQL Scripts)` and optional supporting files (UDF stubs, configs).
7. **Report & Metadata** – summarize actions, expose TODOs (e.g., manual currency tables), and loop feedback into subsequent runs.

