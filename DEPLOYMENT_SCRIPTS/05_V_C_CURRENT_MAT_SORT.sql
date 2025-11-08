-- ============================================================================
-- Deployment Script: V_C_CURRENT_MAT_SORT
-- ============================================================================
-- This script creates the V_C_CURRENT_MAT_SORT view in Snowflake
-- 
-- Instructions:
-- 1. Replace <YOUR_SCHEMA> with your actual schema name
-- 2. Execute this script in Snowflake
-- 3. Verify the view was created: SHOW VIEWS LIKE 'V_C_CURRENT_MAT_SORT' IN SCHEMA <YOUR_SCHEMA>;
-- 
-- Note: This view contains warnings about joins without conditions (ON 1=1).
-- This is intentional based on the HANA calculation view definition.
-- ============================================================================

CREATE OR REPLACE VIEW <YOUR_SCHEMA>.V_C_CURRENT_MAT_SORT AS
-- Warnings:
--   Join Join_1 has no join conditions

WITH
  projection_2 AS (
    SELECT
        SAPK5D.YGRPLNKF.CODAPL AS CODAPL,
        SAPK5D.YGRPLNKF.LVLGRP AS LVLGRP,
        SAPK5D.YGRPLNKF.DATENT AS DATENT,
        SAPK5D.YGRPLNKF.ENTITY AS ENTITY,
        SAPK5D.YGRPLNKF.NUMGRP AS NUMGRP,
        SAPK5D.YGRPLNKF.MANDT AS MANDT
    FROM SAPK5D.YGRPLNKF
    WHERE SAPK5D.YGRPLNKF.CODAPL = 01
  ),
  projection_1 AS (
    SELECT
        SAPK5D.YGRPLNKF.CODAPL AS CODAPL,
        SAPK5D.YGRPLNKF.LVLGRP AS LVLGRP,
        SAPK5D.YGRPLNKF.DATENT AS DATENT,
        SAPK5D.YGRPLNKF.ENTITY AS ENTITY,
        SAPK5D.YGRPLNKF.NUMGRP AS NUMGRP,
        SAPK5D.YGRPLNKF.MANDT AS MANDT
    FROM SAPK5D.YGRPLNKF
    WHERE SAPK5D.YGRPLNKF.CODAPL = 01
  ),
  aggregation_1 AS (
    SELECT
        projection_1.MANDT AS MANDT,
        projection_1.CODAPL AS CODAPL,
        projection_1.LVLGRP AS LVLGRP,
        projection_1.ENTITY AS ENTITY,
        MAX(projection_1.DATENT) AS DATENT
    FROM projection_1
    GROUP BY projection_1.MANDT, projection_1.CODAPL, projection_1.LVLGRP, projection_1.ENTITY
  ),
  join_1 AS (
    SELECT
        aggregation_1.MANDT AS MANDT,
        aggregation_1.CODAPL AS "JOIN$CODAPL$CODAPL",
        aggregation_1.DATENT AS "JOIN$DATENT$DATENT",
        aggregation_1.LVLGRP AS "JOIN$LVLGRP$LVLGRP",
        aggregation_1.ENTITY AS "JOIN$ENTITY$ENTITY",
        aggregation_1.CODAPL AS CODAPL,
        aggregation_1.LVLGRP AS LVLGRP,
        aggregation_1.DATENT AS DATENT,
        aggregation_1.ENTITY AS ENTITY,
        aggregation_1.NUMGRP AS NUMGRP,
        aggregation_1.CODAPL AS "JOIN$CODAPL$CODAPL",
        aggregation_1.DATENT AS "JOIN$DATENT$DATENT",
        aggregation_1.LVLGRP AS "JOIN$LVLGRP$LVLGRP",
        aggregation_1.ENTITY AS "JOIN$ENTITY$ENTITY",
        aggregation_1.MANDT AS MANDT
    FROM aggregation_1
    INNER JOIN projection_2 ON 1=1
  )

SELECT * FROM join_1;

