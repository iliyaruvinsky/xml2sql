-- ============================================================================
-- Deployment Script: V_C_SOLD_MATERIALS_PROD
-- ============================================================================
-- This script creates the V_C_SOLD_MATERIALS_PROD view in Snowflake
-- 
-- Instructions:
-- 1. Replace <YOUR_SCHEMA> with your actual schema name
-- 2. Execute this script in Snowflake
-- 3. Verify the view was created: SHOW VIEWS LIKE 'V_C_SOLD_MATERIALS_PROD' IN SCHEMA <YOUR_SCHEMA>;
-- 
-- Note: This view contains warnings about joins without conditions (ON 1=1).
-- This is intentional based on the HANA calculation view definition.
-- ============================================================================

CREATE OR REPLACE VIEW <YOUR_SCHEMA>.V_C_SOLD_MATERIALS_PROD AS
-- Warnings:
--   Join Join_1 has no join conditions

WITH
  fert_materials AS (
    SELECT
        "/KMDM/CALCULATIONVIEWS/MATERIAL_DETAILS".MATNR AS MATNR,
        "/KMDM/CALCULATIONVIEWS/MATERIAL_DETAILS".LONG_OLD_NUMBER AS LONG_OLD_NUMBER,
        "/KMDM/CALCULATIONVIEWS/MATERIAL_DETAILS".KUNNR AS KUNNR,
        "/KMDM/CALCULATIONVIEWS/MATERIAL_DETAILS".MTART AS MTART,
        "/KMDM/CALCULATIONVIEWS/MATERIAL_DETAILS".MEINS AS MEINS,
        "/KMDM/CALCULATIONVIEWS/MATERIAL_DETAILS".MANDT AS MANDT
    FROM "/KMDM/CALCULATIONVIEWS/MATERIAL_DETAILS"
    WHERE "/KMDM/CALCULATIONVIEWS/MATERIAL_DETAILS".MTART = 'FERT'
  ),
  projection_1 AS (
    SELECT
        "/KMDM/CALCULATIONVIEWS/SOLD_MATERIALS".MANDT AS MANDT,
        "/KMDM/CALCULATIONVIEWS/SOLD_MATERIALS".MATNR AS MATNR,
        "/KMDM/CALCULATIONVIEWS/SOLD_MATERIALS".ERDAT AS ERDAT
    FROM "/KMDM/CALCULATIONVIEWS/SOLD_MATERIALS"
  ),
  aggregation_2 AS (
    SELECT
        "/KMDM/CALCULATIONVIEWS/SALES_BOM".MANDT AS MANDT,
        "/KMDM/CALCULATIONVIEWS/SALES_BOM".IDNRK AS IDNRK
    FROM "/KMDM/CALCULATIONVIEWS/SALES_BOM"
    GROUP BY "/KMDM/CALCULATIONVIEWS/SALES_BOM".MANDT, "/KMDM/CALCULATIONVIEWS/SALES_BOM".IDNRK
  ),
  union_1 AS (
    SELECT
        projection_1.ERDAT AS ERDAT,
        projection_1.MANDT AS MANDT,
        projection_1.MATNR AS MATNR
    FROM projection_1
    UNION ALL
    SELECT
        NULL AS ERDAT,
        aggregation_2.MANDT AS MANDT,
        aggregation_2.IDNRK AS MATNR
    FROM aggregation_2
  ),
  join_1 AS (
    SELECT
        union_1.MANDT AS MANDT,
        union_1.ERDAT AS ERDAT,
        union_1.MATNR AS "JOIN$MATNR$MATNR",
        union_1.LONG_OLD_NUMBER AS LONG_OLD_NUMBER,
        union_1.MEINS AS MEINS,
        union_1.MATNR AS "JOIN$MATNR$MATNR",
        union_1.MANDT AS MANDT
    FROM union_1
    INNER JOIN fert_materials ON 1=1
  ),
  aggregation_1 AS (
    SELECT
        join_1.LONG_OLD_NUMBER AS LONG_OLD_NUMBER,
        join_1.MEINS AS MEINS,
        join_1.MANDT AS MANDT,
        MAX(join_1.ERDAT) AS ERDAT
    FROM join_1
    GROUP BY join_1.LONG_OLD_NUMBER, join_1.MEINS, join_1.MANDT
  )

SELECT * FROM aggregation_1;

