CREATE VIEW V_C_CURRENT_MAT_SORT AS
WITH
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
        projection_2.CODAPL AS CODAPL,
        projection_2.LVLGRP AS LVLGRP,
        projection_2.DATENT AS DATENT,
        projection_2.ENTITY AS ENTITY,
        projection_2.NUMGRP AS NUMGRP
    FROM aggregation_1
    INNER JOIN projection_2 ON aggregation_1.CODAPL = projection_2.CODAPL AND aggregation_1.DATENT = projection_2.DATENT AND aggregation_1.LVLGRP = projection_2.LVLGRP AND aggregation_1.ENTITY = projection_2.ENTITY AND aggregation_1.MANDT = projection_2.MANDT
  )

SELECT CODAPL, LVLGRP, DATENT, ENTITY, NUMGRP, MANDT FROM join_1