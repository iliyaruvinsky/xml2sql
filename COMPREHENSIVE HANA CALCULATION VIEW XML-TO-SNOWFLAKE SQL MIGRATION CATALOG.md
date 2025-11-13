# COMPREHENSIVE HANA CALCULATION VIEW XML-TO-SNOWFLAKE SQL MIGRATION CATALOG

**Production-Ready Reference for xml2sql Converter Implementation**

This definitive catalog covers every artifact type, conversion rule, and edge case needed for migrating thousands of SAP HANA Calculation Views to Snowflake SQL.

---

## EXECUTIVE SUMMARY

SAP HANA Calculation Views are XML-defined semantic modeling objects (.calculationview files) that provide graphical data modeling through nodes (Projection, Join, Aggregation, Union, Rank, Star Join). Converting to Snowflake requires translating: (1) ViewNode structures to CTE patterns, (2) Data types with precision awareness, (3) Function syntax, (4) Parameters to UDTFs/session variables/secure views, (5) Advanced features like hierarchies, currency conversion, and temporal joins. This catalog enables 60-80% automation with clear flagging for manual intervention on complex scenarios.

---

## 1. VIEWNODE TYPES & CONVERSION PATTERNS

### 1.1 Projection Nodes (Calculation:ProjectionView)

**XML Structure:**
```xml
<calculationView xsi:type="Calculation:ProjectionView" id="Projection_1">
  <viewAttributes>
    <viewAttribute id="PRODUCT_ID" aggregationBehavior="none"/>
    <viewAttribute id="SALES_AMOUNT" aggregationBehavior="sum" semanticType="amount"/>
  </viewAttributes>
  <calculatedViewAttributes>
    <calculatedViewAttribute id="TAX_AMOUNT" datatype="DECIMAL" expressionLanguage="SQL">
      <formula>"SALES_AMOUNT" * 0.08</formula>
    </calculatedViewAttribute>
  </calculatedViewAttributes>
  <input node="#DataSource_1"/>
  <filter>"SALES_AMOUNT" > 100</filter>
</calculationView>
```

**HANA Semantics:** Selects columns and applies filters without aggregation. aggregationBehavior (sum/min/max/avg/none) controls higher-layer aggregation. semanticType (amount/quantity/date) provides metadata. Executes early filtering for performance.

**Snowflake Conversion:**
```sql
WITH Projection_1 AS (
  SELECT 
    PRODUCT_ID,
    SALES_AMOUNT,
    SALES_AMOUNT * 0.08 AS TAX_AMOUNT
  FROM DataSource_1
  WHERE SALES_AMOUNT > 100
)
```

**Edge Cases:** CP→LIKE, BT→BETWEEN. Hidden columns excluded from final SELECT. Nested calculated columns need CTEs. NULL-safe division with NULLIF(denominator, 0).

**Versions:** HANA 1.0 SP08+, all Snowflake versions.

---

### 1.2 Aggregation Nodes (Calculation:AggregationView)

**XML Structure:**
```xml
<calculationView xsi:type="Calculation:AggregationView" id="Aggregation_1">
  <viewAttributes>
    <viewAttribute id="REGION"/>
  </viewAttributes>
  <baseMeasures>
    <measure id="TOTAL_SALES" aggregationType="sum"/>
    <measure id="UNIQUE_CUSTOMERS" aggregationType="count" distinct="true"/>
  </baseMeasures>
  <input node="#Projection_1"/>
  <restrictedColumn id="SALES_WITH_CURRENCY">
    <attribute>CURRENCY_CODE</attribute>
  </restrictedColumn>
</calculationView>
```

**HANA Semantics:** Groups by dimensions, aggregates measures (sum/min/max/count/avg/count_distinct). restrictedColumn implements exception aggregation.

**Snowflake Conversion:**
```sql
WITH Aggregation_1 AS (
  SELECT 
    REGION,
    CURRENCY_CODE,
    SUM(TOTAL_SALES) AS TOTAL_SALES,
    COUNT(DISTINCT UNIQUE_CUSTOMERS) AS UNIQUE_CUSTOMERS
  FROM Projection_1
  GROUP BY REGION, CURRENCY_CODE
)
```

**Edge Cases:** COUNT_DISTINCT on high cardinality may need HLL_ACCUMULATE. Restricted attributes must be in GROUP BY. Calculated measures execute AFTER aggregation.

---

### 1.3 Join Nodes (Calculation:JoinView)

**XML Structure:**
```xml
<calculationView xsi:type="Calculation:JoinView" id="Join_1" 
                 joinType="inner|leftOuter|rightOuter|fullOuter|referential|textJoin"
                 cardinality="1..1|1..n|n..1|n..m">
  <input node="#Orders">
    <mapping target="CUSTOMER_ID" source="KUNNR"/>
  </input>
  <input node="#Customers">
    <mapping target="CUSTOMER_ID" source="CUSTOMER_ID"/>
  </input>
  <joinAttribute name="CUSTOMER_ID"/>
</calculationView>
```

**HANA Semantics:** joinType includes referential (optimized with dynamic pruning). Cardinality enables join pruning when columns not requested.

**Snowflake Conversion:**
```sql
WITH Join_1 AS (
  SELECT o.*, c.CUSTOMER_NAME
  FROM Orders o
  INNER JOIN Customers c ON o.KUNNR = c.CUSTOMER_ID
)
```

**Mappings:** inner→INNER JOIN, leftOuter→LEFT JOIN, referential→INNER JOIN (pruning lost), textJoin→LEFT JOIN with language filter.

**Edge Cases:** Multi-column joins use AND. n..m risks Cartesian explosion. NULL≠NULL in joins.

---

### 1.4 Union Nodes (Calculation:UnionView)

**XML Structure:**
```xml
<calculationView xsi:type="Calculation:UnionView" id="Union_1">
  <input node="#Source_A">
    <mapping target="TRANSACTION_ID" source="DOC_ID"/>
    <mapping xsi:type="Calculation:ConstantAttributeMapping" target="SOURCE" value="'SAP_ERP'"/>
  </input>
  <input node="#Source_B">
    <mapping target="TRANSACTION_ID" source="TRANS_NO"/>
    <mapping xsi:type="Calculation:ConstantAttributeMapping" target="SOURCE" value="'SFDC'"/>
  </input>
</calculationView>
```

**HANA Semantics:** UNION ALL (preserves duplicates). ConstantAttributeMapping adds literals for source tagging.

**Snowflake Conversion:**
```sql
WITH Union_1 AS (
  SELECT DOC_ID AS TRANSACTION_ID, 'SAP_ERP' AS SOURCE FROM Source_A
  UNION ALL
  SELECT TRANS_NO AS TRANSACTION_ID, 'SFDC' AS SOURCE FROM Source_B
)
```

**Edge Cases:** Always UNION ALL. Type compatibility requires explicit CAST. Column count must match across branches.

---

### 1.5 Rank Nodes (Calculation:RankView)

**XML Structure:**
```xml
<calculationView xsi:type="Calculation:RankView" id="Rank_1">
  <partitionViewAttributeName>REGION</partitionViewAttributeName>
  <order byViewAttributeName="SALES_AMOUNT" direction="DESC"/>
  <rankThreshold>10</rankThreshold>
  <rankViewAttributeName>RANK</rankViewAttributeName>
</calculationView>
```

**HANA Semantics:** Filters TOP N per partition.

**Snowflake Conversion:**
```sql
WITH Rank_1 AS (
  SELECT * FROM (
    SELECT *, 
      RANK() OVER (PARTITION BY REGION ORDER BY SALES_AMOUNT DESC) AS RANK
    FROM Projection_1
  ) WHERE RANK <= 10
)
```

**Function Selection:** RANK() (gaps for ties: 1,2,2,4), DENSE_RANK() (no gaps: 1,2,2,3), ROW_NUMBER() (continuous: 1,2,3,4).

**Edge Cases:** NULLS FIRST/LAST for NULL handling. Empty partition for global ranking.

---

### 1.6 Star Join Nodes (Calculation:StarJoinView)

**XML Structure:**
```xml
<calculationView xsi:type="Calculation:StarJoinView" id="StarJoin_1">
  <input node="#Fact_Sales" type="Fact"/>
  <input node="#Dim_Customer" type="Dimension"/>
  <input node="#Dim_Product" type="Dimension"/>
  <joinAttribute name="CUSTOMER_KEY"/>
  <joinAttribute name="PRODUCT_KEY"/>
</calculationView>
```

**HANA Semantics:** Star schema with one fact + multiple dimensions. All dimension inputs must be DIMENSION-type views.

**Snowflake Conversion:**
```sql
WITH StarJoin_1 AS (
  SELECT f.*, c.CUSTOMER_NAME, p.PRODUCT_NAME
  FROM Fact_Sales f
  LEFT JOIN Dim_Customer c ON f.CUSTOMER_ID = c.CUSTOMER_KEY
  LEFT JOIN Dim_Product p ON f.PRODUCT_ID = p.PRODUCT_KEY
)
```

**Edge Cases:** LEFT JOIN preserves facts when dimension lookup fails. Dimensions cannot contain measures.

---

### 1.7 Additional Node Types

**Intersect** (HANA 2.0 SPS01+): Returns common rows. Convert to `INTERSECT`.
**Minus** (HANA 2.0 SPS01+): Returns rows in first not in second. Convert to `EXCEPT`.
**Hierarchy** (HANA 2.0 SPS03+): Parent-child traversal. Convert to recursive CTE.
**Window Function** (HANA 2.0 SPS03+): Analytical functions. Convert directly to Snowflake window syntax.

---

## 2. DATA TYPE MAPPINGS

### 2.1 Complete Conversion Matrix

| HANA Type | Snowflake Type | Precision Notes | Critical Edge Cases |
|-----------|---------------|----------------|-------------------|
| VARCHAR(n) | VARCHAR(n) | HANA: 1-5000 bytes (ASCII)<br>Snowflake: 1-16MB (UTF-8) | HANA defaults: 1 (DDL) or 5000 (DML) |
| NVARCHAR(n) | VARCHAR(n) | Direct mapping | For multi-byte safety: VARCHAR(n*6) |
| CHAR(n) | VARCHAR(n) | Remove blank-padding | Comparison semantics differ |
| CLOB/NCLOB | VARCHAR | Max 16MB | For >16MB use external stage |
| INTEGER | NUMBER(38,0) | 32-bit signed | Compatible |
| BIGINT | NUMBER(38,0) | 64-bit signed | Compatible |
| SMALLINT | NUMBER(38,0) | 16-bit signed | Compatible |
| **TINYINT** | **SMALLINT** | ⚠️ HANA: UNSIGNED (0-255)<br>Snowflake: signed | **CRITICAL: Use SMALLINT for safety** |
| DECIMAL(p,s) | NUMBER(p,s) | ⚠️ Snowflake scale max 37 not 38 | DECIMAL(38,38)→NUMBER(38,37) |
| DOUBLE | FLOAT | 64-bit IEEE 754 | ~15 decimal digits |
| REAL | FLOAT | HANA: 32-bit → Snowflake: 64-bit | Precision upgraded |
| DATE | DATE | YYYY-MM-DD | Compatible |
| TIME | TIME(9) | Add nanosecond precision | Specify precision explicitly |
| TIMESTAMP | TIMESTAMP_NTZ(9) | No timezone | For wallclock time |
| SECONDDATE | TIMESTAMP_NTZ(0) | Second precision | Format: 2011-05-18 08:24:03.0 |
| BINARY(n) | BINARY(n) | Max 8MB | Snowflake 8MB limit |
| VARBINARY(n) | BINARY(n) | Max 8MB | Same as BINARY |
| BLOB | BINARY or External Stage | ⚠️ No native BLOB | Max 8MB inline, use stage for larger |
| BOOLEAN | BOOLEAN | TRUE/FALSE/NULL | Identical |
| ST_GEOMETRY | GEOGRAPHY/GEOMETRY | ⚠️ Requires WKT conversion | Export ST_asWKT(), import TO_GEOGRAPHY() |
| ST_POINT | GEOGRAPHY(POINT) | Convert via WKT | NEW ST_POINT(x,y)→ST_MAKEPOINT(x,y) |

### 2.2 XML Data Type Declaration

```xml
<logicalModel id="Semantics">
  <attributes>
    <attribute id="CustomerID" datatype="INTEGER"/>
    <attribute id="CustomerName" datatype="NVARCHAR" length="100"/>
    <attribute id="OrderDate" datatype="DATE"/>
  </attributes>
  <baseMeasures>
    <measure id="Revenue" datatype="DECIMAL" precision="15" scale="2" aggregationType="sum"/>
  </baseMeasures>
</logicalModel>
```

### 2.3 Critical Date Format Differences

**HANA accepts:**
```sql
WHERE ORDER_DATE > '20210101'  -- Works in HANA
```

**Snowflake requires:**
```sql
WHERE ORDER_DATE > '2021-01-01'  -- ISO format
-- OR explicit conversion
WHERE ORDER_DATE > TO_DATE('20210101', 'YYYYMMDD')
-- Safe for inconsistent data
WHERE ORDER_DATE > TRY_TO_DATE(date_string, 'YYYYMMDD')
```

---

## 3. FUNCTION CONVERSIONS

### 3.1 String Functions

| HANA | Snowflake | Notes |
|------|-----------|-------|
| CONCAT(a,b) | CONCAT(a,b,c,...) | Snowflake accepts unlimited args |
| SUBSTRING(s,start,len) | SUBSTRING(s,start,len) | Identical |
| LENGTH(s) | LENGTH(s) | Identical |
| UPPER/LOWER | UPPER/LOWER | Identical |
| TRIM/LTRIM/RTRIM | TRIM/LTRIM/RTRIM | Identical |
| REPLACE(s,search,replace) | REPLACE(s,search,replace) | Identical |
| STRING_AGG(col, delim ORDER BY col) | LISTAGG(col, delim) WITHIN GROUP (ORDER BY col) | Syntax differs |

### 3.2 Date Functions

| HANA | Snowflake | Parameter Order |
|------|-----------|-----------------|
| ADD_DAYS(date, n) | DATEADD(DAY, n, date) | ⚠️ Order reversed |
| ADD_MONTHS(date, n) | DATEADD(MONTH, n, date) or ADD_MONTHS(date, n) | Both work |
| DAYS_BETWEEN(d1, d2) | DATEDIFF(DAY, d1, d2) | Function name change |
| CURRENT_DATE | CURRENT_DATE | Identical |
| CURRENT_TIMESTAMP | CURRENT_TIMESTAMP | Identical |
| YEAR/MONTH/DAY | YEAR/MONTH/DAY | Identical |
| WEEKDAY(date) | DAYOFWEEK(date) | Function name |
| WORKDAYS_BETWEEN(d1,d2,cal) | ⚠️ NO EQUIVALENT | Requires custom UDF |

### 3.3 Numeric Functions

| HANA | Snowflake | Notes |
|------|-----------|-------|
| ROUND(n,d) | ROUND(n,d,'mode') | Snowflake adds rounding mode |
| FLOOR(n) | FLOOR(n,scale) | Snowflake adds scale |
| CEIL(n) | CEIL(n,scale) | Snowflake adds scale |
| ABS/MOD/POWER/SQRT | ABS/MOD/POWER/SQRT | Identical |

### 3.4 Window Functions

All identical with Snowflake addition of IGNORE NULLS option:
- ROW_NUMBER() OVER (...)
- RANK() OVER (...)
- DENSE_RANK() OVER (...)
- LAG/LEAD(col, offset, default) [IGNORE NULLS] OVER (...)
- FIRST_VALUE/LAST_VALUE(col) [IGNORE NULLS] OVER (...)

### 3.5 Conversion Functions

| HANA | Snowflake | Differences |
|------|-----------|------------|
| TO_VARCHAR(val,fmt) | TO_VARCHAR(val,fmt) or TO_CHAR(val,fmt) | Format strings slightly differ |
| TO_DECIMAL(val,p,s) | TO_DECIMAL(val,p,s) or TO_NUMBER(val,p,s) | Snowflake adds optional format |
| TO_DATE(str,fmt) | TRY_TO_DATE(str,fmt) | TRY_ returns NULL on error |
| TO_TIMESTAMP(str,fmt) | TRY_TO_TIMESTAMP(str,fmt) | TRY_ safer |
| CAST(expr AS type) | CAST(expr AS type) or expr::type | :: shorthand |

### 3.6 Calculated Column Conversions

**HANA XML:**
```xml
<calculatedViewAttribute id="FullName" datatype="NVARCHAR" length="100">
  <formula>concat("FirstName", concat(' ', "LastName"))</formula>
</calculatedViewAttribute>
<calculatedViewAttribute id="ProfitMargin" datatype="DECIMAL">
  <formula>("Revenue" - "Cost") / "Revenue" * 100</formula>
</calculatedViewAttribute>
```

**Snowflake:**
```sql
SELECT 
  CONCAT(first_name, ' ', last_name) AS full_name,
  (revenue - cost) / NULLIF(revenue, 0) * 100 AS profit_margin
FROM source_table
```

---

## 4. PARAMETER CONVERSIONS

### 4.1 HANA Input Parameter XML

```xml
<variable id="IP_FISCAL_YEAR" parameter="true">
  <variableProperties datatype="INTEGER" mandatory="true" defaultValue="2023">
    <selection multiLine="false" type="Single"/>
  </variableProperties>
</variable>

<variable id="IP_PLANT_LIST" parameter="true">
  <variableProperties datatype="VARCHAR" mandatory="false">
    <selection multiLine="true" type="Multiple"/>
  </variableProperties>
</variable>

<variable id="IP_DATE_RANGE" parameter="true">
  <variableProperties datatype="DATE" mandatory="true">
    <selection type="Interval"/>
  </variableProperties>
</variable>
```

**Usage in HANA:**
```sql
SELECT * FROM "_SYS_BIC"."package/VIEW"
(PLACEHOLDER."$$IP_FISCAL_YEAR$$" => '2023')
```

### 4.2 Snowflake Approach 1: UDTFs (Recommended)

**Single Parameter:**
```sql
CREATE OR REPLACE FUNCTION calc_view_by_year(p_year INTEGER DEFAULT 2023)
RETURNS TABLE (sales_org VARCHAR, amount NUMBER)
AS
$$ SELECT sales_org, amount FROM fact_sales WHERE fiscal_year = p_year $$;

-- Usage
SELECT * FROM TABLE(calc_view_by_year(2024));
```

**Multi-Value Parameter:**
```sql
CREATE OR REPLACE FUNCTION calc_view_by_plants(p_plant_list VARCHAR)
RETURNS TABLE (material VARCHAR, plant VARCHAR, stock NUMBER)
AS
$$
  SELECT material, plant, stock
  FROM material_stock
  WHERE plant IN (SELECT TRIM(VALUE) FROM TABLE(SPLIT_TO_TABLE(p_plant_list, ',')))
$$;

-- Usage
SELECT * FROM TABLE(calc_view_by_plants('1000,1001,1002'));
```

**Range Parameter:**
```sql
CREATE OR REPLACE FUNCTION calc_view_date_range(p_from DATE, p_to DATE)
RETURNS TABLE (doc_id VARCHAR, posting_date DATE, amount NUMBER)
AS
$$ SELECT doc_id, posting_date, amount FROM docs WHERE posting_date BETWEEN p_from AND p_to $$;

-- Usage
SELECT * FROM TABLE(calc_view_date_range('2023-01-01', '2023-12-31'));
```

### 4.3 Snowflake Approach 2: Session Variables

```sql
-- Create view with session variable
CREATE OR REPLACE VIEW sales_by_year AS
SELECT * FROM fact_sales WHERE fiscal_year = $year_param;

-- Set and query
SET year_param = 2023;
SELECT * FROM sales_by_year;
```

**Pros:** Simple, no procedures
**Cons:** Requires SET before query, session-scoped only

### 4.4 Snowflake Approach 3: Secure Views with Context Functions

```sql
CREATE OR REPLACE SECURE VIEW employee_data AS
SELECT employee_id, name, salary
FROM employees
WHERE employee_email = CURRENT_USER()
   OR CURRENT_ROLE() IN ('ADMIN', 'HR');
```

**Pros:** Automatic enforcement, data sharing compatible
**Cons:** Limited to user/role context

### 4.5 Snowflake Approach 4: Stored Procedures

```sql
CREATE OR REPLACE PROCEDURE sp_get_sales(p_year INT, p_region VARCHAR DEFAULT NULL)
RETURNS TABLE()
LANGUAGE SQL
AS
$$
DECLARE sql_query VARCHAR;
BEGIN
  sql_query := 'SELECT * FROM fact_sales WHERE fiscal_year = ' || p_year;
  IF (p_region IS NOT NULL) THEN
    sql_query := sql_query || ' AND region = ''' || p_region || '''';
  END IF;
  LET res RESULTSET := (EXECUTE IMMEDIATE :sql_query);
  RETURN TABLE(res);
END;
$$;

CALL sp_get_sales(2023, 'EMEA');
```

**Pros:** Maximum flexibility, optional parameters
**Cons:** SQL injection risk (sanitize inputs), complex

### 4.6 Parameter Conversion Decision Matrix

| HANA Parameter Type | Snowflake Approach | Complexity | Best For |
|---------------------|-------------------|-----------|----------|
| Single mandatory | UDTF | Low | Most scenarios |
| Single optional | UDTF with DEFAULT | Low | Optional filters |
| Multiple values (IN) | UDTF + SPLIT_TO_TABLE | Medium | Lists |
| Range (BETWEEN) | UDTF with 2 params | Low | Date/amount ranges |
| User-dependent | Secure View + CURRENT_USER | Low | Row-level security |
| Role-dependent | Secure View + CURRENT_ROLE | Low | Role-based access |
| Complex conditional | Stored Procedure | High | Dynamic filters |

---

## 5. ADVANCED FEATURES

### 5.1 Hierarchies

**Level-Based Hierarchies:**
```sql
-- Flatten to columns
CREATE VIEW product_hierarchy AS
SELECT 
  product_id,
  product_category AS level_1,
  product_subcategory AS level_2,
  product_name AS level_3
FROM products;
```

**Parent-Child Hierarchies:**
```sql
WITH RECURSIVE org_hierarchy AS (
  -- Root nodes
  SELECT employee_id, employee_name, manager_id, 1 AS level,
         CAST(employee_name AS VARCHAR(1000)) AS path
  FROM org_structure
  WHERE manager_id IS NULL
  
  UNION ALL
  
  -- Children
  SELECT e.employee_id, e.employee_name, e.manager_id, h.level + 1,
         h.path || ' > ' || e.employee_name
  FROM org_structure e
  INNER JOIN org_hierarchy h ON e.manager_id = h.employee_id
)
SELECT * FROM org_hierarchy;
```

**Alternative: Snowflake CONNECT BY:**
```sql
SELECT employee_id, employee_name, LEVEL AS hierarchy_level,
       SYS_CONNECT_BY_PATH(employee_name, ' > ') AS path
FROM org_structure
START WITH manager_id IS NULL
CONNECT BY PRIOR employee_id = manager_id;
```

### 5.2 Currency Conversion

**HANA uses TCUR* tables and CONVERT_CURRENCY function.**

**Snowflake Approach 1: Replicate TCUR* tables:**
```sql
-- Replicate TCURR table
CREATE TABLE tcurr (
  mandt VARCHAR(3), kurst VARCHAR(4), fcurr VARCHAR(5), tcurr VARCHAR(5),
  gdatu DATE, ukurs DECIMAL(9,5), ffact DECIMAL(9,5), tfact DECIMAL(9,5)
);

-- Create conversion function
CREATE OR REPLACE FUNCTION convert_currency_sap(
  amount DECIMAL(15,2), from_curr VARCHAR(5), to_curr VARCHAR(5),
  conv_date DATE, rate_type VARCHAR(4), client VARCHAR(3)
)
RETURNS DECIMAL(15,2)
AS
$$
  SELECT CASE 
    WHEN from_curr = to_curr THEN amount
    WHEN rate.ukurs IS NOT NULL THEN (amount * ABS(rate.ukurs) * rate.tfact) / rate.ffact
    ELSE NULL
  END
  FROM tcurr rate
  WHERE rate.mandt = client AND rate.kurst = rate_type
    AND rate.fcurr = from_curr AND rate.tcurr = to_curr
    AND rate.gdatu = (
      SELECT MAX(gdatu) FROM tcurr 
      WHERE mandt = client AND kurst = rate_type
        AND fcurr = from_curr AND tcurr = to_curr AND gdatu <= conv_date
    )
$$;

-- Use in views
SELECT sales_id, amount,
       convert_currency_sap(amount, doc_currency, 'USD', sales_date, 'M', '100') AS amount_usd
FROM sales;
```

**Snowflake Approach 2: Data Marketplace (Simpler):**
```sql
-- Use Knoema or other FX data from marketplace
SELECT s.*, s.amount * fx.exchange_rate AS amount_usd
FROM sales_fact s
LEFT JOIN snowflake_marketplace.fx_rates fx
  ON s.currency = fx.currency_code AND s.sales_date = fx.date AND fx.target_currency = 'USD';
```

### 5.3 Temporal Joins

**HANA XML:**
```xml
<join temporalJoin="true">
  <temporalCondition>
    <leftTemporalColumn>PostingDate</leftTemporalColumn>
    <rightTemporalFromColumn>ValidFrom</rightTemporalFromColumn>
    <rightTemporalToColumn>ValidTo</rightTemporalToColumn>
    <temporalOperator>includeBoth</temporalOperator>
  </temporalCondition>
</join>
```

**Snowflake Explicit Range Join:**
```sql
SELECT s.*, m.material_description
FROM sales s
INNER JOIN material_master m
  ON s.material_id = m.material_id
  AND s.posting_date BETWEEN m.valid_from AND m.valid_to;
```

**Snowflake ASOF Join (Better Performance):**
```sql
SELECT s.*, m.material_description
FROM sales s
ASOF JOIN material_master m
  MATCH_CONDITION (s.posting_date >= m.valid_from)
  ON s.material_id = m.material_id;
```

**SCD Type 2 Pattern:**
```sql
CREATE TABLE customer_scd (
  customer_key INT AUTOINCREMENT,
  customer_id VARCHAR(20),
  customer_name VARCHAR(100),
  valid_from DATE,
  valid_to DATE DEFAULT '9999-12-31',
  is_current BOOLEAN DEFAULT TRUE,
  version INT
);

-- Query current version
SELECT * FROM customer_scd WHERE is_current = TRUE;

-- Query as of specific date
SELECT * FROM customer_scd 
WHERE customer_id = 'C001' AND '2023-06-15' BETWEEN valid_from AND valid_to;
```

### 5.4 Restricted Measures

**HANA XML:**
```xml
<restrictedMeasures>
  <measure id="Revenue_2023" baseMeasure="Revenue">
    <restriction columnName="FiscalYear">
      <valueFilter value="2023"/>
    </restriction>
  </measure>
</restrictedMeasures>
```

**Snowflake Conversion:**
```sql
SELECT 
  product_id,
  SUM(CASE WHEN fiscal_year = 2023 THEN revenue ELSE 0 END) AS revenue_2023,
  SUM(revenue) AS revenue_total
FROM fact_sales
GROUP BY product_id;
```

---

## 6. MIGRATION PATTERNS & BEST PRACTICES

### 6.1 General Conversion Pattern

**HANA calculation views convert to CTE-based Snowflake SQL:**
```sql
WITH 
  Projection_1 AS (SELECT ... FROM source WHERE ...),
  Join_1 AS (SELECT ... FROM Projection_1 JOIN ...),
  Aggregation_1 AS (SELECT ... FROM Join_1 GROUP BY ...),
  Semantics AS (SELECT ... FROM Aggregation_1)
SELECT * FROM Semantics;
```

Build bottom-up from data sources through each node layer to final semantics.

### 6.2 XML Extraction

```sql
-- Extract from HANA repository
SELECT CDATA FROM _SYS_REPO.ACTIVE_OBJECT
WHERE PACKAGE_ID = 'package.name'
  AND OBJECT_NAME = 'CV_ViewName'
  AND OBJECT_SUFFIX = 'calculationview';
```

**Root XML Structure:**
```xml
<?xml version="1.0" encoding="UTF-8"?>
<Calculation:scenario xmlns:Calculation="http://www.sap.com/ndb/BiModelCalculation.ecore">
  <dataSources>
    <DataSource id="TABLE_NAME" type="DATA_BASE_TABLE">
      <resourceUri>/SCHEMA/TABLE_NAME</resourceUri>
    </DataSource>
  </dataSources>
  <calculationViews>
    <!-- Node definitions -->
  </calculationViews>
  <logicalModel id="Semantics">
    <attributes><attribute id="DIM"/></attributes>
    <baseMeasures><measure id="MEASURE" aggregationType="sum"/></baseMeasures>
  </logicalModel>
</Calculation:scenario>
```

### 6.3 Top 10 Production Migration Challenges

1. **Compilation Memory Exhausted**: Multi-system views create 100K+ line SQL. **Solution:** Request Snowflake 1MB→4MB increase, split views, materialize.

2. **Runtime Memory Issues**: Parallel jobs exhaust memory. **Solution:** Stagger schedules, split code.

3. **Blocking Transactions**: Parallel updates lock tables. **Solution:** Optimize updates, use temp tables, right-size warehouse.

4. **CTE Performance**: Mixing CTE and direct references causes partition scans. **Solution:** Be consistent—use CTE everywhere or nowhere.

5. **UDF with Table Queries**: "Unsupported subquery type" error. **Solution:** Join tables instead, or use JavaScript UDF (slower).

6. **Correlated Subquery Limits**: Multiple table references fail. **Solution:** Rewrite as CTE or JOIN.

7. **Date/Timestamp Format**: '20220109' format fails. **Solution:** TO_TIMESTAMP('20220109','YYYYMMDD'), use TRY_TO_TIMESTAMP.

8. **Object Renaming**: Schema consolidation needs reference tracking. **Solution:** Maintain migration master sheet.

9. **Special Characters**: CV_[XYZ]ABC needs renaming. **Solution:** Standardize naming conventions.

10. **Case Sensitivity**: "Object1" ≠ Object1 in Snowflake. **Solution:** Avoid double quotes, consistent naming.

### 6.4 Automation Architecture

**Parser Design (60-80% automation achievable):**

**Analyzer Phase:**
- Categorize views (simple/medium/complex)
- Build dependency graphs
- Estimate effort

**Converter Phase:**
- Parse_View_Definition_Fn (metadata)
- Parse_View_Body_Fn (main logic)
  - Parse_Projection_Fn → SELECT
  - Parse_Join_Fn → JOIN
  - Parse_Union_Fn → UNION ALL
  - Parse_Aggregation_Fn → GROUP BY
- Generate CTE-based SQL
- Flag sections needing manual work

**Available Tools:**
- **Open-source:** andrew-block-lab/SAP-HANA-View-XML-to-SQL (Python)
- **Commercial:** BladeBridge Converter (template-based, 15-27 day config)
- **Data integration:** HVR/Fivetran (replication not conversion)

### 6.5 Performance Optimization

**HANA Optimizations That Don't Translate:**
- In-Memory processing → Use clustering keys
- Calculation Engine → Materialize complex calcs
- Delta Merge → Use Streams and Tasks

**Snowflake Best Practices:**
- Clustering keys for large filtered tables
- Materialized views for complex aggregations (Enterprise)
- Search optimization for selective filters
- Result caching (24-hour automatic)
- Warehouse sizing: scale up for complexity, scale out for concurrency
- Break down large views into components
- Use dbt/Coalesce for modular design

### 6.6 Migration Timeline (12-16 weeks typical for 100-200 views)

**Week 1-2:** Analysis (export XMLs, categorize, dependencies)
**Week 3-4:** Tool setup, pilot conversion (5-10 views)
**Week 5-8:** Bulk conversion, optimization, dbt setup
**Week 9-10:** Testing, validation, reconciliation
**Week 11-12:** Performance tuning, cutover

**Resource Allocation:**
- 20% Analysis
- 40% Conversion
- 25% Testing
- 15% Optimization

**Success Metrics:**
- 70%+ automation
- 95%+ data accuracy
- <10% performance degradation

---

## 7. QUICK REFERENCE TABLES

### 7.1 ViewNode Quick Reference

| HANA Node | Snowflake Pattern | Complexity |
|-----------|------------------|-----------|
| Projection | SELECT ... WHERE | Low |
| Aggregation | GROUP BY | Low-Medium |
| Join | JOIN ... ON | Medium |
| Union | UNION ALL | Low |
| Rank | RANK() OVER ... WHERE | Medium |
| StarJoin | Multiple LEFT JOINs | Medium-High |
| Intersect | INTERSECT | Low |
| Minus | EXCEPT | Low |

### 7.2 Data Type Quick Reference

| HANA | Snowflake | Critical Notes |
|------|-----------|---------------|
| NVARCHAR(n) | VARCHAR(n) | Direct mapping |
| DECIMAL(p,s) | NUMBER(p,s) | Scale max 37 |
| TINYINT | SMALLINT | Unsigned→Signed |
| TIMESTAMP | TIMESTAMP_NTZ | No timezone |
| CLOB | VARCHAR | Max 16MB |
| BLOB | BINARY/Stage | Max 8MB inline |
| ST_GEOMETRY | GEOGRAPHY | WKT conversion |

### 7.3 Function Quick Reference

| Category | HANA | Snowflake | Notes |
|----------|------|-----------|-------|
| String Agg | STRING_AGG | LISTAGG(...) WITHIN GROUP | Syntax differs |
| Date Add | ADD_DAYS(d,n) | DATEADD(DAY,n,d) | Order reversed |
| Date Diff | DAYS_BETWEEN(d1,d2) | DATEDIFF(DAY,d1,d2) | Function name |
| Safe Convert | TO_DATE(s,f) | TRY_TO_DATE(s,f) | TRY_ returns NULL |
| Workdays | WORKDAYS_BETWEEN | Custom UDF | No equivalent |

### 7.4 Parameter Approach Quick Reference

| Parameter Type | Snowflake Approach | When to Use |
|---------------|-------------------|-------------|
| Single mandatory | UDTF | Most scenarios |
| Multi-value | UDTF + SPLIT_TO_TABLE | IN clauses |
| Range | UDTF with 2 params | BETWEEN |
| User/role-based | Secure View + CURRENT_USER/ROLE | Security |
| Complex dynamic | Stored Procedure | Conditional logic |

---

## 8. VERSION COMPATIBILITY

### 8.1 HANA Versions

- **HANA 1.0 SP08+**: Basic calculation views, Projection/Join/Aggregation/Union/Rank nodes
- **HANA 2.0 SP00+**: Enhanced features, spatial data types
- **HANA 2.0 SP01+**: Intersect/Minus nodes
- **HANA 2.0 SP03+**: Hierarchy functions, Window function nodes
- **HANA Cloud**: Modern HDI-based views, full CDS support

### 8.2 Snowflake Compatibility

- All current Snowflake versions support equivalent SQL patterns
- GEOGRAPHY/GEOMETRY requires appropriate edition/license
- Recursive CTEs supported in all versions
- ASOF JOIN available in all current versions
- Set TIMESTAMP_TYPE_MAPPING parameter for timestamp behavior

---

## 9. COMPLETE CONVERSION EXAMPLE

**HANA Calculation View XML (excerpt):**
```xml
<Calculation:scenario id="CV_SALES_ANALYSIS">
  <dataSources>
    <DataSource id="VBAK">
      <resourceUri>/SCHEMA/VBAK</resourceUri>
    </DataSource>
    <DataSource id="VBAP">
      <resourceUri>/SCHEMA/VBAP</resourceUri>
    </DataSource>
  </dataSources>
  
  <calculationViews>
    <calculationView xsi:type="Calculation:ProjectionView" id="Proj_Orders">
      <viewAttributes>
        <viewAttribute id="VBELN"/>
        <viewAttribute id="KUNNR"/>
        <viewAttribute id="ERDAT"/>
      </viewAttributes>
      <input node="#VBAK"/>
      <filter>"VBTYP" = 'C'</filter>
    </calculationView>
    
    <calculationView xsi:type="Calculation:ProjectionView" id="Proj_Items">
      <viewAttributes>
        <viewAttribute id="VBELN"/>
        <viewAttribute id="MATNR"/>
        <viewAttribute id="NETWR"/>
      </viewAttributes>
      <input node="#VBAP"/>
    </calculationView>
    
    <calculationView xsi:type="Calculation:JoinView" id="Join_Orders_Items" joinType="inner">
      <input node="#Proj_Orders">
        <mapping target="VBELN" source="VBELN"/>
      </input>
      <input node="#Proj_Items">
        <mapping target="VBELN" source="VBELN"/>
      </input>
      <joinAttribute name="VBELN"/>
    </calculationView>
    
    <calculationView xsi:type="Calculation:AggregationView" id="Agg_Sales">
      <viewAttributes>
        <viewAttribute id="KUNNR"/>
        <viewAttribute id="MATNR"/>
      </viewAttributes>
      <baseMeasures>
        <measure id="TOTAL_VALUE" aggregationType="sum"/>
      </baseMeasures>
      <input node="#Join_Orders_Items"/>
    </calculationView>
  </calculationViews>
  
  <logicalModel id="Semantics">
    <attributes>
      <attribute id="CustomerID" datatype="VARCHAR">
        <keyMapping columnObjectName="Agg_Sales" columnName="KUNNR"/>
      </attribute>
      <attribute id="MaterialID" datatype="VARCHAR">
        <keyMapping columnObjectName="Agg_Sales" columnName="MATNR"/>
      </attribute>
    </attributes>
    <baseMeasures>
      <measure id="TotalValue" datatype="DECIMAL" precision="15" scale="2" aggregationType="sum">
        <measureMapping columnObjectName="Agg_Sales" columnName="TOTAL_VALUE"/>
      </measure>
    </baseMeasures>
  </logicalModel>
</Calculation:scenario>
```

**Converted Snowflake SQL:**
```sql
CREATE OR REPLACE VIEW CV_SALES_ANALYSIS AS
WITH 
  Proj_Orders AS (
    SELECT 
      VBELN,
      KUNNR,
      ERDAT
    FROM SCHEMA.VBAK
    WHERE VBTYP = 'C'
  ),
  
  Proj_Items AS (
    SELECT 
      VBELN,
      MATNR,
      NETWR
    FROM SCHEMA.VBAP
  ),
  
  Join_Orders_Items AS (
    SELECT 
      o.VBELN,
      o.KUNNR,
      o.ERDAT,
      i.MATNR,
      i.NETWR
    FROM Proj_Orders o
    INNER JOIN Proj_Items i ON o.VBELN = i.VBELN
  ),
  
  Agg_Sales AS (
    SELECT 
      KUNNR,
      MATNR,
      SUM(NETWR) AS TOTAL_VALUE
    FROM Join_Orders_Items
    GROUP BY KUNNR, MATNR
  ),
  
  Semantics AS (
    SELECT 
      KUNNR AS CustomerID,
      MATNR AS MaterialID,
      TOTAL_VALUE AS TotalValue
    FROM Agg_Sales
  )

SELECT * FROM Semantics;
```

---

## 10. CRITICAL SUCCESS FACTORS

1. **Don't skip analyzer phase**: Understanding view complexity and dependencies is essential
2. **Choose approach based on complexity**: Lift-and-shift for simple views, re-engineering for complex nested structures
3. **Budget 40% time for manual optimization**: Automation handles 60-80%, remaining requires expert intervention
4. **Test thoroughly**: Parallel runs, row count reconciliation, column-level validation, performance benchmarking
5. **Use dbt/Coalesce for maintainability**: Modular transformation design scales better than monolithic views
6. **Document parameter conversions**: Clear mapping between HANA PLACEHOLDER syntax and Snowflake UDTF/procedure calls
7. **Performance tune incrementally**: Clustering keys, materialization, warehouse sizing based on actual query patterns
8. **Maintain migration master sheet**: Track all object renames, schema consolidations, dependency changes

---

## CONCLUSION

This comprehensive catalog provides definitive conversion rules for all major SAP HANA Calculation View artifacts to Snowflake SQL. Production xml2sql converters implementing these patterns should achieve 60-80% automation, with clear flagging for manual intervention on complex scenarios including:

- Nested hierarchies requiring recursive CTEs
- Currency conversion with TCUR* table replication
- HANA-specific functions without direct equivalents (WORKDAYS_BETWEEN)
- Multi-system views requiring decomposition for compilation limits
- Complex parameter scenarios with conditional logic

Always validate conversions against HANA baseline with representative data volumes, and optimize using Snowflake-native features like clustering keys, result caching, and appropriate warehouse sizing. The migration timeline of 12-16 weeks for 100-200 views is achievable with proper planning, tooling, and resource allocation following the patterns documented in this catalog.