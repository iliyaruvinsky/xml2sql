-- Warnings:
--   Join Join_3 has no join conditions
--   Join Join_4 has no join conditions
--   Join Join_1 has no join conditions
--   Join Join_2 has no join conditions

WITH
  projection_1 AS (
    SELECT
        SAPK5D.MAST.MANDT AS MANDT,
        SAPK5D.MAST.MATNR AS MATNR,
        SAPK5D.MAST.WERKS AS WERKS,
        SAPK5D.MAST.STLAN AS STLAN,
        SAPK5D.MAST.STLNR AS STLNR,
        SAPK5D.MAST.STLAL AS STLAL
    FROM SAPK5D.MAST
    WHERE SAPK5D.MAST.STLAN = 5
  ),
  aggregation_1 AS (
    SELECT
        "/KMDM/CALCULATIONVIEWS/CURRENT_MAT_SORT".CODAPL AS CODAPL,
        "/KMDM/CALCULATIONVIEWS/CURRENT_MAT_SORT".LVLGRP AS LVLGRP,
        "/KMDM/CALCULATIONVIEWS/CURRENT_MAT_SORT".ENTITY AS ENTITY,
        MIN("/KMDM/CALCULATIONVIEWS/CURRENT_MAT_SORT".NUMGRP) AS NUMGRP
    FROM "/KMDM/CALCULATIONVIEWS/CURRENT_MAT_SORT"
    WHERE "/KMDM/CALCULATIONVIEWS/CURRENT_MAT_SORT".CODAPL = 01 AND "/KMDM/CALCULATIONVIEWS/CURRENT_MAT_SORT".LVLGRP = 029
    GROUP BY "/KMDM/CALCULATIONVIEWS/CURRENT_MAT_SORT".CODAPL, "/KMDM/CALCULATIONVIEWS/CURRENT_MAT_SORT".LVLGRP, "/KMDM/CALCULATIONVIEWS/CURRENT_MAT_SORT".ENTITY
  ),
  ynlg AS (
    SELECT
        SAPK5D.MARA.MANDT AS MANDT,
        SAPK5D.MARA.MATNR AS MATNR,
        SAPK5D.MARA.MTART AS MTART
    FROM SAPK5D.MARA
    WHERE SAPK5D.MARA.MTART = 'YNLG'
  ),
  projection_2 AS (
    SELECT
        SAPK5D.STPO.MANDT AS MANDT,
        SAPK5D.STPO.STLTY AS STLTY,
        SAPK5D.STPO.STLNR AS STLNR,
        SAPK5D.STPO.STLKN AS STLKN,
        SAPK5D.STPO.STPOZ AS STPOZ,
        SAPK5D.STPO.DATUV AS DATUV,
        SAPK5D.STPO.IDNRK AS IDNRK,
        SAPK5D.STPO.PSWRK AS PSWRK,
        SAPK5D.STPO.MEINS AS MEINS,
        SAPK5D.STPO.MENGE AS MENGE
    FROM SAPK5D.STPO
  ),
  fert AS (
    SELECT
        SAPK5D.MARA.MANDT AS MANDT,
        SAPK5D.MARA.MATNR AS MATNR,
        SAPK5D.MARA.MTART AS MTART
    FROM SAPK5D.MARA
    WHERE SAPK5D.MARA.MTART = 'FERT'
  ),
  join_3 AS (
    SELECT
        projection_1.MANDT AS MANDT,
        projection_1.MATNR AS MATNR,
        projection_1.WERKS AS WERKS,
        projection_1.STLAN AS STLAN,
        projection_1.STLNR AS STLNR,
        projection_1.STLAL AS STLAL,
        projection_1.MANDT AS MANDT,
        projection_1.MATNR AS MATNR
    FROM projection_1
    INNER JOIN ynlg ON 1=1
  ),
  join_4 AS (
    SELECT
        projection_2.IDNRK AS IDNRK,
        projection_2.PSWRK AS PSWRK,
        projection_2.MEINS AS MEINS,
        projection_2.MENGE AS MENGE,
        projection_2.MANDT AS MANDT,
        projection_2.STLNR AS STLNR,
        projection_2.MANDT AS MANDT,
        projection_2.MATNR AS IDNRK
    FROM projection_2
    INNER JOIN fert ON 1=1
  ),
  join_1 AS (
    SELECT
        join_3.STLAL AS STLAL,
        join_3.STLNR AS STLNR,
        join_3.STLAN AS STLAN,
        join_3.WERKS AS WERKS,
        join_3.MATNR AS MATNR,
        join_3.MANDT AS MANDT,
        join_3.MENGE AS MENGE,
        join_3.MEINS AS MEINS,
        join_3.PSWRK AS PSWRK,
        join_3.IDNRK AS IDNRK,
        join_3.MANDT AS MANDT,
        join_3.STLNR AS STLNR
    FROM join_3
    INNER JOIN join_4 ON 1=1
  ),
  join_2 AS (
    SELECT
        join_1.MANDT AS MANDT,
        join_1.MATNR AS MATNR,
        join_1.WERKS AS WERKS,
        join_1.STLAN AS STLAN,
        join_1.STLNR AS STLNR,
        join_1.STLAL AS STLAL,
        join_1.IDNRK AS IDNRK,
        join_1.PSWRK AS PSWRK,
        join_1.MEINS AS MEINS,
        join_1.MENGE AS MENGE,
        join_1.NUMGRP AS NUMGRP,
        join_1.ENTITY AS MATNR
    FROM join_1
    LEFT OUTER JOIN aggregation_1 ON 1=1
  ),
  aggregation_2 AS (
    SELECT
        join_2.MENGE AS MENGE,
        join_2.MEINS AS MEINS,
        join_2.PSWRK AS PSWRK,
        join_2.IDNRK AS IDNRK,
        join_2.STLAL AS STLAL,
        join_2.STLNR AS STLNR,
        join_2.STLAN AS STLAN,
        join_2.MATNR AS MATNR,
        join_2.MANDT AS MANDT,
        join_2.NUMGRP AS NUMGRP
    FROM join_2
    GROUP BY join_2.MENGE, join_2.MEINS, join_2.PSWRK, join_2.IDNRK, join_2.STLAL, join_2.STLNR, join_2.STLAN, join_2.MATNR, join_2.MANDT, join_2.NUMGRP
  )

SELECT * FROM aggregation_2