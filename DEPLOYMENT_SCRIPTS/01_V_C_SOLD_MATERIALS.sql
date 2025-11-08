-- ============================================================================
-- Deployment Script: V_C_SOLD_MATERIALS
-- ============================================================================
-- This script creates the V_C_SOLD_MATERIALS view in Snowflake
-- 
-- Instructions:
-- 1. Replace <YOUR_SCHEMA> with your actual schema name
-- 2. Execute this script in Snowflake
-- 3. Verify the view was created: SHOW VIEWS LIKE 'V_C_SOLD_MATERIALS' IN SCHEMA <YOUR_SCHEMA>;
-- ============================================================================

CREATE OR REPLACE VIEW <YOUR_SCHEMA>.V_C_SOLD_MATERIALS AS
WITH
  projection_1 AS (
    SELECT
        SAPK5D.VBAP.MATNR AS MATNR,
        SAPK5D.VBAP.ERDAT AS ERDAT,
        SAPK5D.VBAP.MEINS AS MEINS,
        SAPK5D.VBAP.MANDT AS MANDT
    FROM SAPK5D.VBAP
    WHERE SAPK5D.VBAP.ERDAT > 20140101
  ),
  aggregation_1 AS (
    SELECT
        projection_1.MANDT AS MANDT,
        projection_1.MATNR AS MATNR,
        projection_1.MEINS AS MEINS,
        MAX(projection_1.ERDAT) AS ERDAT
    FROM projection_1
    GROUP BY projection_1.MANDT, projection_1.MATNR, projection_1.MEINS
  )

SELECT * FROM aggregation_1;

