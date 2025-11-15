CREATE VIEW V_C_RECENTLY_CREATED_PRODUCTS AS
WITH
  sort_005 AS (
    SELECT
        SAPK5D.YGRPLNKF.MANDT AS MANDT,
        SAPK5D.YGRPLNKF.CODAPL AS CODAPL,
        SAPK5D.YGRPLNKF.LVLGRP AS LVLGRP,
        SAPK5D.YGRPLNKF.NUMGRP AS NUMGRP,
        SAPK5D.YGRPLNKF.ENTITY AS ENTITY
    FROM SAPK5D.YGRPLNKF
  ),
  sort_024 AS (
    SELECT
        SAPK5D.YGRPLNKF.MANDT AS MANDT,
        SAPK5D.YGRPLNKF.CODAPL AS CODAPL,
        SAPK5D.YGRPLNKF.LVLGRP AS LVLGRP,
        SAPK5D.YGRPLNKF.NUMGRP AS NUMGRP,
        SAPK5D.YGRPLNKF.ENTITY AS ENTITY
    FROM SAPK5D.YGRPLNKF
  ),
  projection_1 AS (
    SELECT
        SAPK5D.MARA.MATNR AS MATNR,
        SAPK5D.MARA.ERSDA AS ERSDA,
        SAPK5D.MARA.MTART AS MTART,
        SAPK5D.MARA.MANDT AS MANDT
    FROM SAPK5D.MARA
  ),
  projection_2 AS (
    SELECT
        SAPK5D.MARA.MANDT AS MANDT,
        SAPK5D.MARA.ERSDA AS ERSDA,
        SAPK5D.MARA.MATNR AS MATNR,
        SAPK5D.MARA.MTART AS MTART
    FROM SAPK5D.MARA
    WHERE SAPK5D.MARA.MANDT = 400
  ),
  union_1 AS (
    SELECT
        sort_005.ENTITY AS ENTITY,
        sort_005.MANDT AS MANDT
    FROM sort_005
    UNION ALL
    SELECT
        sort_024.ENTITY AS ENTITY,
        sort_024.MANDT AS MANDT
    FROM sort_024
  ),
  aggregation_1 AS (
    SELECT
        union_1.MANDT AS MANDT,
        union_1.ENTITY AS ENTITY
    FROM union_1
    GROUP BY union_1.MANDT, union_1.ENTITY
  ),
  join_1 AS (
    SELECT
        aggregation_1.MANDT AS MANDT,
        aggregation_1.ENTITY AS MATNR,
        projection_2.ERSDA AS ERSDA,
        projection_2.MTART AS MTART
    FROM aggregation_1
    LEFT OUTER JOIN projection_2 ON aggregation_1.ENTITY = projection_2.MATNR AND aggregation_1.MANDT = projection_2.MANDT
  ),
  projection_3 AS (
    SELECT
        join_1.MANDT AS MANDT,
        join_1.MATNR AS MATNR,
        join_1.ERSDA AS ERSDA,
        join_1.MTART AS MTART
    FROM join_1
  ),
  union_2 AS (
    SELECT
        projection_1.MATNR AS MATNR,
        projection_1.ERSDA AS ERSDA,
        projection_1.MANDT AS MANDT
    FROM projection_1
    UNION ALL
    SELECT
        projection_3.MATNR AS MATNR,
        projection_3.ERSDA AS ERSDA,
        projection_3.MANDT AS MANDT
    FROM projection_3
  ),
  aggregation_2 AS (
    SELECT
        union_2.MANDT AS MANDT,
        union_2.ERSDA AS ERSDA,
        union_2.MATNR AS MATNR
    FROM union_2
    GROUP BY union_2.MANDT, union_2.ERSDA, union_2.MATNR
  )

SELECT MANDT, ERSDA, MATNR FROM aggregation_2