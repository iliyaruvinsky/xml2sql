-- ============================================================================
-- Deployment Script: V_C_MATERIAL_DETAILS
-- ============================================================================
-- This script creates the V_C_MATERIAL_DETAILS view in Snowflake
-- 
-- Instructions:
-- 1. Replace <YOUR_SCHEMA> with your actual schema name
-- 2. Execute this script in Snowflake
-- 3. Verify the view was created: SHOW VIEWS LIKE 'V_C_MATERIAL_DETAILS' IN SCHEMA <YOUR_SCHEMA>;
-- 
-- Note: This view directly selects from the MARA table with calculated attributes.
-- ============================================================================

CREATE OR REPLACE VIEW <YOUR_SCHEMA>.V_C_MATERIAL_DETAILS AS
SELECT
    SAPK5D.MARA.MANDT AS MANDT,
    SAPK5D.MARA.MATNR AS MATNR,
    SAPK5D.MARA.ERSDA AS ERSDA,
    SAPK5D.MARA.MTART AS MTART,
    SAPK5D.MARA.BISMT AS BISMT,
    SAPK5D.MARA.MEINS AS MEINS,
    SAPK5D.MARA.NORMT AS NORMT,
    SAPK5D.MARA.LABOR AS LABOR,
    SAPK5D.MARA.LAEDA AS LAEDA,
    SAPK5D.MARA.AENAM AS AENAM,
    SAPK5D.MARA.MATKL AS MATKL,
    SAPK5D.MARA.GROES AS GROES,
    SAPK5D.MARA.BRGEW AS BRGEW,
    SAPK5D.MARA.NTGEW AS NTGEW,
    SAPK5D.MARA.GEWEI AS GEWEI,
    SAPK5D.MARA.VOLUM AS VOLUM,
    SAPK5D.MARA.VOLEH AS VOLEH,
    SAPK5D.MARA.EAN11 AS EAN11,
    SAPK5D.MARA.NUMTP AS NUMTP,
    SAPK5D.MARA.MSTAE AS MSTAE,
    SAPK5D.MARA.ZZIML_CODE AS ZZIML_CODE,
    SAPK5D.MARA.WRKST AS WRKST,
    '0000000000' || SAPK5D.MARA.BISMT AS LONG_OLD_NUMBER,
    '0000' || SAPK5D.MARA.NORMT AS KUNNR
FROM SAPK5D.MARA;

