Microsoft Windows [Version 10.0.26200.6899]
(c) Microsoft Corporation. All rights reserved.

C:\Users\USER>cd "C:\Users\USER\Google Drive\SW_PLATFORM\15. AI\MY_LATEST_FILES\EXODUS\XML to SQL"

C:\Users\USER\Google Drive\SW_PLATFORM\15. AI\MY_LATEST_FILES\EXODUS\XML to SQL>.\venv\Scripts\Activate.ps1

C:\Users\USER\Google Drive\SW_PLATFORM\15. AI\MY_LATEST_FILES\EXODUS\XML to SQL>python -m pip install -e ".[dev]"
Obtaining file:///C:/Users/USER/Google%20Drive/SW_PLATFORM/15.%20AI/MY_LATEST_FILES/EXODUS/XML%20to%20SQL
  Installing build dependencies ... done
  Checking if build backend supports build_editable ... done
  Getting requirements to build editable ... done
  Preparing editable metadata (pyproject.toml) ... done
Requirement already satisfied: lxml>=5.2.0 in c:\users\user\appdata\local\programs\python\python311\lib\site-packages (from xml-to-sql==0.1.0) (6.0.0)
Collecting typer>=0.12.3 (from xml-to-sql==0.1.0)
  Using cached typer-0.20.0-py3-none-any.whl.metadata (16 kB)
Collecting pyyaml>=6.0.1 (from xml-to-sql==0.1.0)
  Using cached pyyaml-6.0.3-cp311-cp311-win_amd64.whl.metadata (2.4 kB)
Collecting pytest>=8.2.0 (from xml-to-sql==0.1.0)
  Using cached pytest-8.4.2-py3-none-any.whl.metadata (7.7 kB)
Requirement already satisfied: colorama>=0.4 in c:\users\user\appdata\local\programs\python\python311\lib\site-packages (from pytest>=8.2.0->xml-to-sql==0.1.0) (0.4.6)
Requirement already satisfied: iniconfig>=1 in c:\users\user\appdata\local\programs\python\python311\lib\site-packages (from pytest>=8.2.0->xml-to-sql==0.1.0) (2.1.0)
Requirement already satisfied: packaging>=20 in c:\users\user\appdata\local\programs\python\python311\lib\site-packages (from pytest>=8.2.0->xml-to-sql==0.1.0) (25.0)
Requirement already satisfied: pluggy<2,>=1.5 in c:\users\user\appdata\local\programs\python\python311\lib\site-packages (from pytest>=8.2.0->xml-to-sql==0.1.0) (1.6.0)
Requirement already satisfied: pygments>=2.7.2 in c:\users\user\appdata\local\programs\python\python311\lib\site-packages (from pytest>=8.2.0->xml-to-sql==0.1.0) (2.19.2)
Requirement already satisfied: click>=8.0.0 in c:\users\user\appdata\local\programs\python\python311\lib\site-packages (from typer>=0.12.3->xml-to-sql==0.1.0) (8.1.7)
Requirement already satisfied: typing-extensions>=3.7.4.3 in c:\users\user\appdata\local\programs\python\python311\lib\site-packages (from typer>=0.12.3->xml-to-sql==0.1.0) (4.14.0)
Collecting shellingham>=1.3.0 (from typer>=0.12.3->xml-to-sql==0.1.0)
  Using cached shellingham-1.5.4-py2.py3-none-any.whl.metadata (3.5 kB)
Requirement already satisfied: rich>=10.11.0 in c:\users\user\appdata\local\programs\python\python311\lib\site-packages (from typer>=0.12.3->xml-to-sql==0.1.0) (13.5.2)
Requirement already satisfied: markdown-it-py>=2.2.0 in c:\users\user\appdata\local\programs\python\python311\lib\site-packages (from rich>=10.11.0->typer>=0.12.3->xml-to-sql==0.1.0) (3.0.0)
Requirement already satisfied: mdurl~=0.1 in c:\users\user\appdata\local\programs\python\python311\lib\site-packages (from markdown-it-py>=2.2.0->rich>=10.11.0->typer>=0.12.3->xml-to-sql==0.1.0) (0.1.2)
Using cached pytest-8.4.2-py3-none-any.whl (365 kB)
Using cached pyyaml-6.0.3-cp311-cp311-win_amd64.whl (158 kB)
Using cached typer-0.20.0-py3-none-any.whl (47 kB)
Using cached shellingham-1.5.4-py2.py3-none-any.whl (9.8 kB)
Building wheels for collected packages: xml-to-sql
  Building editable for xml-to-sql (pyproject.toml) ... done
  Created wheel for xml-to-sql: filename=xml_to_sql-0.1.0-0.editable-py3-none-any.whl size=1680 sha256=01595ec2826719a32024b64ac998678e936f5dbbc5d5932f9731efed2edca2cc
  Stored in directory: C:\Users\USER\AppData\Local\Temp\pip-ephem-wheel-cache-slxhjgdf\wheels\b3\40\5a\1b75fb9f3bdd9357fe1971ade0e6ea2eb569eb061db00d4b36
Successfully built xml-to-sql
Installing collected packages: shellingham, pyyaml, pytest, typer, xml-to-sql
  Attempting uninstall: pytest
    Found existing installation: pytest 7.4.3
    Uninstalling pytest-7.4.3:
      Successfully uninstalled pytest-7.4.3
Successfully installed pytest-8.4.2 pyyaml-6.0.3 shellingham-1.5.4 typer-0.20.0 xml-to-sql-0.1.0

C:\Users\USER\Google Drive\SW_PLATFORM\15. AI\MY_LATEST_FILES\EXODUS\XML to SQL>venv\Scripts\python -m pytest -v
================================================= test session starts =================================================
platform win32 -- Python 3.11.9, pytest-8.4.2, pluggy-1.6.0 -- C:\Users\USER\Google Drive\SW_PLATFORM\15. AI\MY_LATEST_FILES\EXODUS\XML to SQL\venv\Scripts\python.exe
cachedir: .pytest_cache
rootdir: C:\Users\USER\Google Drive\SW_PLATFORM\15. AI\MY_LATEST_FILES\EXODUS\XML to SQL
configfile: pyproject.toml
collected 23 items

tests/test_config_loader.py::test_load_config_with_defaults PASSED                                               [  4%]
tests/test_config_loader.py::test_select_scenarios_filters_disabled PASSED                                       [  8%]
tests/test_parser.py::test_parse_scenario_smoke[Sold_Materials.XML] PASSED                                       [ 13%]
tests/test_parser.py::test_parse_scenario_smoke[SALES_BOM.XML] PASSED                                            [ 17%]
tests/test_parser.py::test_parse_scenario_smoke[Recently_created_products.XML] PASSED                            [ 21%]
tests/test_parser.py::test_parse_scenario_variables_and_logical_model PASSED                                     [ 26%]
tests/test_skeleton.py::test_import_package PASSED                                                               [ 30%]
tests/test_sql_renderer.py::test_render_simple_projection PASSED                                                 [ 34%]
tests/test_sql_renderer.py::test_render_projection_with_filter PASSED                                            [ 39%]
tests/test_sql_renderer.py::test_render_join PASSED                                                              [ 43%]
tests/test_sql_renderer.py::test_render_aggregation PASSED                                                       [ 47%]
tests/test_sql_renderer.py::test_render_integration_sold_materials PASSED                                        [ 52%]
tests/test_sql_renderer.py::test_render_all_xml_samples[Sold_Materials.XML] PASSED                               [ 56%]
tests/test_sql_renderer.py::test_render_all_xml_samples[SALES_BOM.XML] PASSED                                    [ 60%]
tests/test_sql_renderer.py::test_render_all_xml_samples[Recently_created_products.XML] PASSED                    [ 65%]
tests/test_sql_renderer.py::test_render_all_xml_samples[KMDM_Materials.XML] PASSED                               [ 69%]
tests/test_sql_renderer.py::test_render_all_xml_samples[CURRENT_MAT_SORT.XML] PASSED                             [ 73%]
tests/test_sql_renderer.py::test_render_all_xml_samples[Material Details.XML] PASSED                             [ 78%]
tests/test_sql_renderer.py::test_render_all_xml_samples[Sold_Materials_PROD.XML] PASSED                          [ 82%]
tests/test_sql_renderer.py::test_render_union_node PASSED                                                        [ 86%]
tests/test_sql_renderer.py::test_render_with_currency_config PASSED                                              [ 91%]
tests/test_sql_renderer.py::test_function_translation_if_statement PASSED                                        [ 95%]
tests/test_sql_renderer.py::test_function_translation_string_concatenation PASSED                                [100%]

================================================= 23 passed in 0.14s ==================================================

C:\Users\USER\Google Drive\SW_PLATFORM\15. AI\MY_LATEST_FILES\EXODUS\XML to SQL>Copy-Item config.example.yaml config.yaml
'Copy-Item' is not recognized as an internal or external command,
operable program or batch file.

C:\Users\USER\Google Drive\SW_PLATFORM\15. AI\MY_LATEST_FILES\EXODUS\XML to SQL>Copy-Item config.example.yaml config.yaml
'Copy-Item' is not recognized as an internal or external command,
operable program or batch file.

C:\Users\USER\Google Drive\SW_PLATFORM\15. AI\MY_LATEST_FILES\EXODUS\XML to SQL>Copy-Item config.example.yaml config.yaml
'Copy-Item' is not recognized as an internal or external command,
operable program or batch file.

C:\Users\USER\Google Drive\SW_PLATFORM\15. AI\MY_LATEST_FILES\EXODUS\XML to SQL>powershell -Command "Copy-Item config.example.yaml config.yaml"

C:\Users\USER\Google Drive\SW_PLATFORM\15. AI\MY_LATEST_FILES\EXODUS\XML to SQL>Copy-Item config.examp
'Copy-Item' is not recognized as an internal or external command,
operable program or batch file.

C:\Users\USER\Google Drive\SW_PLATFORM\15. AI\MY_LATEST_FILES\EXODUS\XML to SQL>Copy-Item config.example.yaml config.yaml
'Copy-Item' is not recognized as an internal or external command,
operable program or batch file.

C:\Users\USER\Google Drive\SW_PLATFORM\15. AI\MY_LATEST_FILES\EXODUS\XML to SQL>venv\Scripts\python -m xml_to_sql.cli.app convert --config config.yaml --scenario Sold_Materials
<frozen runpy>:128: RuntimeWarning: 'xml_to_sql.cli.app' found in sys.modules after import of package 'xml_to_sql.cli', but prior to execution of 'xml_to_sql.cli.app'; this may result in unpredictable behaviour

C:\Users\USER\Google Drive\SW_PLATFORM\15. AI\MY_LATEST_FILES\EXODUS\XML to SQL>REM Using Python module

C:\Users\USER\Google Drive\SW_PLATFORM\15. AI\MY_LATEST_FILES\EXODUS\XML to SQL>venv\Scripts\python -m xml_to_sql.cli.app convert --config config.yaml --scenario Sold_Materials
<frozen runpy>:128: RuntimeWarning: 'xml_to_sql.cli.app' found in sys.modules after import of package 'xml_to_sql.cli', but prior to execution of 'xml_to_sql.cli.app'; this may result in unpredictable behaviour

C:\Users\USER\Google Drive\SW_PLATFORM\15. AI\MY_LATEST_FILES\EXODUS\XML to SQL>venv\Scripts\python --version
Python 3.11.9

C:\Users\USER\Google Drive\SW_PLATFORM\15. AI\MY_LATEST_FILES\EXODUS\XML to SQL>venv\Scripts\python -m pip list | findstr "lxml typer pyyaml pytest"
lxml              6.0.2
pytest            8.4.2
typer             0.20.0

[notice] A new release of pip is available: 24.0 -> 25.3
[notice] To update, run: C:\Users\USER\Google Drive\SW_PLATFORM\15. AI\MY_LATEST_FILES\EXODUS\XML to SQL\venv\Scripts\python.exe -m pip install --upgrade pip

C:\Users\USER\Google Drive\SW_PLATFORM\15. AI\MY_LATEST_FILES\EXODUS\XML to SQL>venv\Scripts\python -m pytest -v
=========================================================================================================== test session starts ===========================================================================================================
platform win32 -- Python 3.11.9, pytest-8.4.2, pluggy-1.6.0 -- C:\Users\USER\Google Drive\SW_PLATFORM\15. AI\MY_LATEST_FILES\EXODUS\XML to SQL\venv\Scripts\python.exe
cachedir: .pytest_cache
rootdir: C:\Users\USER\Google Drive\SW_PLATFORM\15. AI\MY_LATEST_FILES\EXODUS\XML to SQL
configfile: pyproject.toml
collected 23 items

tests/test_config_loader.py::test_load_config_with_defaults PASSED                                                                                                                                                                   [  4%]
tests/test_config_loader.py::test_select_scenarios_filters_disabled PASSED                                                                                                                                                           [  8%]
tests/test_parser.py::test_parse_scenario_smoke[Sold_Materials.XML] PASSED                                                                                                                                                           [ 13%]
tests/test_parser.py::test_parse_scenario_smoke[SALES_BOM.XML] PASSED                                                                                                                                                                [ 17%]
tests/test_parser.py::test_parse_scenario_smoke[Recently_created_products.XML] PASSED                                                                                                                                                [ 21%]
tests/test_parser.py::test_parse_scenario_variables_and_logical_model PASSED                                                                                                                                                         [ 26%]
tests/test_skeleton.py::test_import_package PASSED                                                                                                                                                                                   [ 30%]
tests/test_sql_renderer.py::test_render_simple_projection PASSED                                                                                                                                                                     [ 34%]
tests/test_sql_renderer.py::test_render_projection_with_filter PASSED                                                                                                                                                                [ 39%]
tests/test_sql_renderer.py::test_render_join PASSED                                                                                                                                                                                  [ 43%]
tests/test_sql_renderer.py::test_render_aggregation PASSED                                                                                                                                                                           [ 47%]
tests/test_sql_renderer.py::test_render_integration_sold_materials PASSED                                                                                                                                                            [ 52%]
tests/test_sql_renderer.py::test_render_all_xml_samples[Sold_Materials.XML] PASSED                                                                                                                                                   [ 56%]
tests/test_sql_renderer.py::test_render_all_xml_samples[SALES_BOM.XML] PASSED                                                                                                                                                        [ 60%]
tests/test_sql_renderer.py::test_render_all_xml_samples[Recently_created_products.XML] PASSED                                                                                                                                        [ 65%]
tests/test_sql_renderer.py::test_render_all_xml_samples[KMDM_Materials.XML] PASSED                                                                                                                                                   [ 69%]
tests/test_sql_renderer.py::test_render_all_xml_samples[CURRENT_MAT_SORT.XML] PASSED                                                                                                                                                 [ 73%]
tests/test_sql_renderer.py::test_render_all_xml_samples[Material Details.XML] PASSED                                                                                                                                                 [ 78%]
tests/test_sql_renderer.py::test_render_all_xml_samples[Sold_Materials_PROD.XML] PASSED                                                                                                                                              [ 82%]
tests/test_sql_renderer.py::test_render_union_node PASSED                                                                                                                                                                            [ 86%]
tests/test_sql_renderer.py::test_render_with_currency_config PASSED                                                                                                                                                                  [ 91%]
tests/test_sql_renderer.py::test_function_translation_if_statement PASSED                                                                                                                                                            [ 95%]
tests/test_sql_renderer.py::test_function_translation_string_concatenation PASSED                                                                                                                                                    [100%]

=========================================================================================================== 23 passed in 0.14s ============================================================================================================

C:\Users\USER\Google Drive\SW_PLATFORM\15. AI\MY_LATEST_FILES\EXODUS\XML to SQL>venv\Scripts\python -m pytest tests/test_config_loader.py -v
=========================================================================================================== test session starts ===========================================================================================================
platform win32 -- Python 3.11.9, pytest-8.4.2, pluggy-1.6.0 -- C:\Users\USER\Google Drive\SW_PLATFORM\15. AI\MY_LATEST_FILES\EXODUS\XML to SQL\venv\Scripts\python.exe
cachedir: .pytest_cache
rootdir: C:\Users\USER\Google Drive\SW_PLATFORM\15. AI\MY_LATEST_FILES\EXODUS\XML to SQL
configfile: pyproject.toml
collected 2 items

tests/test_config_loader.py::test_load_config_with_defaults PASSED                                                                                                                                                                   [ 50%]
tests/test_config_loader.py::test_select_scenarios_filters_disabled PASSED                                                                                                                                                           [100%]

============================================================================================================ 2 passed in 0.05s ============================================================================================================

C:\Users\USER\Google Drive\SW_PLATFORM\15. AI\MY_LATEST_FILES\EXODUS\XML to SQL>venv\Scripts\python -m pytest tests/test_parser.py -v
=========================================================================================================== test session starts ===========================================================================================================
platform win32 -- Python 3.11.9, pytest-8.4.2, pluggy-1.6.0 -- C:\Users\USER\Google Drive\SW_PLATFORM\15. AI\MY_LATEST_FILES\EXODUS\XML to SQL\venv\Scripts\python.exe
cachedir: .pytest_cache
rootdir: C:\Users\USER\Google Drive\SW_PLATFORM\15. AI\MY_LATEST_FILES\EXODUS\XML to SQL
configfile: pyproject.toml
collected 4 items

tests/test_parser.py::test_parse_scenario_smoke[Sold_Materials.XML] PASSED                                                                                                                                                           [ 25%]
tests/test_parser.py::test_parse_scenario_smoke[SALES_BOM.XML] PASSED                                                                                                                                                                [ 50%]
tests/test_parser.py::test_parse_scenario_smoke[Recently_created_products.XML] PASSED                                                                                                                                                [ 75%]
tests/test_parser.py::test_parse_scenario_variables_and_logical_model PASSED                                                                                                                                                         [100%]

============================================================================================================ 4 passed in 0.05s ============================================================================================================

C:\Users\USER\Google Drive\SW_PLATFORM\15. AI\MY_LATEST_FILES\EXODUS\XML to SQL>venv\Scripts\python -m pytest tests/test_sql_renderer.py -v
=========================================================================================================== test session starts ===========================================================================================================
platform win32 -- Python 3.11.9, pytest-8.4.2, pluggy-1.6.0 -- C:\Users\USER\Google Drive\SW_PLATFORM\15. AI\MY_LATEST_FILES\EXODUS\XML to SQL\venv\Scripts\python.exe
cachedir: .pytest_cache
rootdir: C:\Users\USER\Google Drive\SW_PLATFORM\15. AI\MY_LATEST_FILES\EXODUS\XML to SQL
configfile: pyproject.toml
collected 16 items

tests/test_sql_renderer.py::test_render_simple_projection PASSED                                                                                                                                                                     [  6%]
tests/test_sql_renderer.py::test_render_projection_with_filter PASSED                                                                                                                                                                [ 12%]
tests/test_sql_renderer.py::test_render_join PASSED                                                                                                                                                                                  [ 18%]
tests/test_sql_renderer.py::test_render_aggregation PASSED                                                                                                                                                                           [ 25%]
tests/test_sql_renderer.py::test_render_integration_sold_materials PASSED                                                                                                                                                            [ 31%]
tests/test_sql_renderer.py::test_render_all_xml_samples[Sold_Materials.XML] PASSED                                                                                                                                                   [ 37%]
tests/test_sql_renderer.py::test_render_all_xml_samples[SALES_BOM.XML] PASSED                                                                                                                                                        [ 43%]
tests/test_sql_renderer.py::test_render_all_xml_samples[Recently_created_products.XML] PASSED                                                                                                                                        [ 50%]
tests/test_sql_renderer.py::test_render_all_xml_samples[KMDM_Materials.XML] PASSED                                                                                                                                                   [ 56%]
tests/test_sql_renderer.py::test_render_all_xml_samples[CURRENT_MAT_SORT.XML] PASSED                                                                                                                                                 [ 62%]
tests/test_sql_renderer.py::test_render_all_xml_samples[Material Details.XML] PASSED                                                                                                                                                 [ 68%]
tests/test_sql_renderer.py::test_render_all_xml_samples[Sold_Materials_PROD.XML] PASSED                                                                                                                                              [ 75%]
tests/test_sql_renderer.py::test_render_union_node PASSED                                                                                                                                                                            [ 81%]
tests/test_sql_renderer.py::test_render_with_currency_config PASSED                                                                                                                                                                  [ 87%]
tests/test_sql_renderer.py::test_function_translation_if_statement PASSED                                                                                                                                                            [ 93%]
tests/test_sql_renderer.py::test_function_translation_string_concatenation PASSED                                                                                                                                                    [100%]

=========================================================================================================== 16 passed in 0.08s ============================================================================================================

C:\Users\USER\Google Drive\SW_PLATFORM\15. AI\MY_LATEST_FILES\EXODUS\XML to SQL>dir config.yaml
 Volume in drive C is OS
 Volume Serial Number is 4E9D-4825

 Directory of C:\Users\USER\Google Drive\SW_PLATFORM\15. AI\MY_LATEST_FILES\EXODUS\XML to SQL

11/08/2025  01:10 PM             1,118 config.yaml
               1 File(s)          1,118 bytes
               0 Dir(s)  40,387,100,672 bytes free

C:\Users\USER\Google Drive\SW_PLATFORM\15. AI\MY_LATEST_FILES\EXODUS\XML to SQL>venv\Scripts\python -m xml_to_sql.cli list --config config.yaml
Sold_Materials [enabled] -> C:\Users\USER\Google Drive\SW_PLATFORM\15. AI\MY_LATEST_FILES\EXODUS\XML to SQL\Source (XML Files)\Sold_Materials.XML
SALES_BOM [enabled] -> C:\Users\USER\Google Drive\SW_PLATFORM\15. AI\MY_LATEST_FILES\EXODUS\XML to SQL\Source (XML Files)\SALES_BOM.XML
Recently_created_products [enabled] -> C:\Users\USER\Google Drive\SW_PLATFORM\15. AI\MY_LATEST_FILES\EXODUS\XML to SQL\Source (XML Files)\Recently_created_products.XML
Material Details [enabled] -> C:\Users\USER\Google Drive\SW_PLATFORM\15. AI\MY_LATEST_FILES\EXODUS\XML to SQL\Source (XML Files)\Material Details.XML
KMDM_Materials [enabled] -> C:\Users\USER\Google Drive\SW_PLATFORM\15. AI\MY_LATEST_FILES\EXODUS\XML to SQL\Source (XML Files)\KMDM_Materials.XML
CURRENT_MAT_SORT [enabled] -> C:\Users\USER\Google Drive\SW_PLATFORM\15. AI\MY_LATEST_FILES\EXODUS\XML to SQL\Source (XML Files)\CURRENT_MAT_SORT.XML
Sold_Materials_PROD [enabled] -> C:\Users\USER\Google Drive\SW_PLATFORM\15. AI\MY_LATEST_FILES\EXODUS\XML to SQL\Source (XML Files)\Sold_Materials_PROD.XML

C:\Users\USER\Google Drive\SW_PLATFORM\15. AI\MY_LATEST_FILES\EXODUS\XML to SQL>venv\Scripts\python -m xml_to_sql.cli convert --config config.yaml --list-only
[plan] C:\Users\USER\Google Drive\SW_PLATFORM\15. AI\MY_LATEST_FILES\EXODUS\XML to SQL\Source (XML Files)\Sold_Materials.XML -> C:\Users\USER\Google Drive\SW_PLATFORM\15. AI\MY_LATEST_FILES\EXODUS\XML to SQL\Target (SQL Scripts)\V_C_SOLD_MATERIALS.sql
[plan] C:\Users\USER\Google Drive\SW_PLATFORM\15. AI\MY_LATEST_FILES\EXODUS\XML to SQL\Source (XML Files)\SALES_BOM.XML -> C:\Users\USER\Google Drive\SW_PLATFORM\15. AI\MY_LATEST_FILES\EXODUS\XML to SQL\Target (SQL Scripts)\V_C_SALES_BOM.sql
[plan] C:\Users\USER\Google Drive\SW_PLATFORM\15. AI\MY_LATEST_FILES\EXODUS\XML to SQL\Source (XML Files)\Recently_created_products.XML -> C:\Users\USER\Google Drive\SW_PLATFORM\15. AI\MY_LATEST_FILES\EXODUS\XML to SQL\Target (SQL Scripts)\V_C_RECENTLY_CREATED_PRODUCTS.sql
[plan] C:\Users\USER\Google Drive\SW_PLATFORM\15. AI\MY_LATEST_FILES\EXODUS\XML to SQL\Source (XML Files)\Material Details.XML -> C:\Users\USER\Google Drive\SW_PLATFORM\15. AI\MY_LATEST_FILES\EXODUS\XML to SQL\Target (SQL Scripts)\V_C_MATERIAL_DETAILS.sql
[plan] C:\Users\USER\Google Drive\SW_PLATFORM\15. AI\MY_LATEST_FILES\EXODUS\XML to SQL\Source (XML Files)\KMDM_Materials.XML -> C:\Users\USER\Google Drive\SW_PLATFORM\15. AI\MY_LATEST_FILES\EXODUS\XML to SQL\Target (SQL Scripts)\V_C_KMDM_MATERIALS.sql
[plan] C:\Users\USER\Google Drive\SW_PLATFORM\15. AI\MY_LATEST_FILES\EXODUS\XML to SQL\Source (XML Files)\CURRENT_MAT_SORT.XML -> C:\Users\USER\Google Drive\SW_PLATFORM\15. AI\MY_LATEST_FILES\EXODUS\XML to SQL\Target (SQL Scripts)\V_C_CURRENT_MAT_SORT.sql
[plan] C:\Users\USER\Google Drive\SW_PLATFORM\15. AI\MY_LATEST_FILES\EXODUS\XML to SQL\Source (XML Files)\Sold_Materials_PROD.XML -> C:\Users\USER\Google Drive\SW_PLATFORM\15. AI\MY_LATEST_FILES\EXODUS\XML to SQL\Target (SQL Scripts)\V_C_SOLD_MATERIALS_PROD.sql

C:\Users\USER\Google Drive\SW_PLATFORM\15. AI\MY_LATEST_FILES\EXODUS\XML to SQL>venv\Scripts\python -m xml_to_sql.cli convert --config config.yaml --scenario Sold_Materials
[plan] C:\Users\USER\Google Drive\SW_PLATFORM\15. AI\MY_LATEST_FILES\EXODUS\XML to SQL\Source (XML Files)\Sold_Materials.XML -> C:\Users\USER\Google Drive\SW_PLATFORM\15. AI\MY_LATEST_FILES\EXODUS\XML to SQL\Target (SQL Scripts)\V_C_SOLD_MATERIALS.sql
  Scenario ID: Sold_Materials
  Nodes parsed: 2
  Filters detected: 1
  Calculated columns: 0
  Logical model: present
  Planned SQL target: C:\Users\USER\Google Drive\SW_PLATFORM\15. AI\MY_LATEST_FILES\EXODUS\XML to SQL\Target (SQL Scripts)\V_C_SOLD_MATERIALS.sql
  ✓ SQL generated: C:\Users\USER\Google Drive\SW_PLATFORM\15. AI\MY_LATEST_FILES\EXODUS\XML to SQL\Target (SQL Scripts)\V_C_SOLD_MATERIALS.sql

C:\Users\USER\Google Drive\SW_PLATFORM\15. AI\MY_LATEST_FILES\EXODUS\XML to SQL>type "Target (SQL Scripts)\V_C_SOLD_MATERIALS.sql"
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

SELECT * FROM aggregation_1
C:\Users\USER\Google Drive\SW_PLATFORM\15. AI\MY_LATEST_FILES\EXODUS\XML to SQL>venv\Scripts\python -m xml_to_sql.cli convert --config config.yaml --scenario SALES_BOM
[plan] C:\Users\USER\Google Drive\SW_PLATFORM\15. AI\MY_LATEST_FILES\EXODUS\XML to SQL\Source (XML Files)\SALES_BOM.XML -> C:\Users\USER\Google Drive\SW_PLATFORM\15. AI\MY_LATEST_FILES\EXODUS\XML to SQL\Target (SQL Scripts)\V_C_SALES_BOM.sql
  Scenario ID: SALES_BOM
  Nodes parsed: 10
  Filters detected: 5
  Calculated columns: 0
  Logical model: present
  Planned SQL target: C:\Users\USER\Google Drive\SW_PLATFORM\15. AI\MY_LATEST_FILES\EXODUS\XML to SQL\Target (SQL Scripts)\V_C_SALES_BOM.sql
  ✓ SQL generated: C:\Users\USER\Google Drive\SW_PLATFORM\15. AI\MY_LATEST_FILES\EXODUS\XML to SQL\Target (SQL Scripts)\V_C_SALES_BOM.sql

C:\Users\USER\Google Drive\SW_PLATFORM\15. AI\MY_LATEST_FILES\EXODUS\XML to SQL>type "Target (SQL Scripts)\V_C_SALES_BOM.sql"
-- Warnings:
--   Join Join_4 has no join conditions
--   Join Join_3 has no join conditions
--   Join Join_1 has no join conditions
--   Join Join_2 has no join conditions

WITH
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
  fert AS (
    SELECT
        SAPK5D.MARA.MANDT AS MANDT,
        SAPK5D.MARA.MATNR AS MATNR,
        SAPK5D.MARA.MTART AS MTART
    FROM SAPK5D.MARA
    WHERE SAPK5D.MARA.MTART = 'FERT'
  ),
  ynlg AS (
    SELECT
        SAPK5D.MARA.MANDT AS MANDT,
        SAPK5D.MARA.MATNR AS MATNR,
        SAPK5D.MARA.MTART AS MTART
    FROM SAPK5D.MARA
    WHERE SAPK5D.MARA.MTART = 'YNLG'
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
C:\Users\USER\Google Drive\SW_PLATFORM\15. AI\MY_LATEST_FILES\EXODUS\XML to SQL>venv\Scripts\python -m xml_to_sql.cli convert --config config.yaml --scenario KMDM_Materials
[plan] C:\Users\USER\Google Drive\SW_PLATFORM\15. AI\MY_LATEST_FILES\EXODUS\XML to SQL\Source (XML Files)\KMDM_Materials.XML -> C:\Users\USER\Google Drive\SW_PLATFORM\15. AI\MY_LATEST_FILES\EXODUS\XML to SQL\Target (SQL Scripts)\V_C_KMDM_MATERIALS.sql
  Scenario ID: KMDM_Materials
  Nodes parsed: 11
  Filters detected: 1
  Calculated columns: 0
  Logical model: present
  Planned SQL target: C:\Users\USER\Google Drive\SW_PLATFORM\15. AI\MY_LATEST_FILES\EXODUS\XML to SQL\Target (SQL Scripts)\V_C_KMDM_MATERIALS.sql
  ✓ SQL generated: C:\Users\USER\Google Drive\SW_PLATFORM\15. AI\MY_LATEST_FILES\EXODUS\XML to SQL\Target (SQL Scripts)\V_C_KMDM_MATERIALS.sql

C:\Users\USER\Google Drive\SW_PLATFORM\15. AI\MY_LATEST_FILES\EXODUS\XML to SQL>type "Target (SQL Scripts)\V_C_KMDM_MATERIALS.sql" | findstr /i "UNION"
  union_1 AS (
    UNION ALL
    UNION ALL
    UNION ALL
        union_1.MANDT AS MANDT,
        union_1.MATNR AS MATNR,
        union_1.MEINS AS MEINS,
        MAX(union_1.ERDAT) AS ERDAT
    FROM union_1
    GROUP BY union_1.MANDT, union_1.MATNR, union_1.MEINS

C:\Users\USER\Google Drive\SW_PLATFORM\15. AI\MY_LATEST_FILES\EXODUS\XML to SQL>venv\Scripts\python -m xml_to_sql.cli convert --config config.yaml --scenario Recently_created_products
[plan] C:\Users\USER\Google Drive\SW_PLATFORM\15. AI\MY_LATEST_FILES\EXODUS\XML to SQL\Source (XML Files)\Recently_created_products.XML -> C:\Users\USER\Google Drive\SW_PLATFORM\15. AI\MY_LATEST_FILES\EXODUS\XML to SQL\Target (SQL Scripts)\V_C_RECENTLY_CREATED_PRODUCTS.sql
  Scenario ID: Recently_created_products
  Nodes parsed: 10
  Filters detected: 1
  Calculated columns: 0
  Logical model: present
  Planned SQL target: C:\Users\USER\Google Drive\SW_PLATFORM\15. AI\MY_LATEST_FILES\EXODUS\XML to SQL\Target (SQL Scripts)\V_C_RECENTLY_CREATED_PRODUCTS.sql
  ✓ SQL generated: C:\Users\USER\Google Drive\SW_PLATFORM\15. AI\MY_LATEST_FILES\EXODUS\XML to SQL\Target (SQL Scripts)\V_C_RECENTLY_CREATED_PRODUCTS.sql

C:\Users\USER\Google Drive\SW_PLATFORM\15. AI\MY_LATEST_FILES\EXODUS\XML to SQL>type "Target (SQL Scripts)\V_C_RECENTLY_CREATED_PRODUCTS.sql" | findstr /i "UNION"
  union_1 AS (
    UNION ALL
        union_1.MANDT AS MANDT,
        union_1.ENTITY AS ENTITY
    FROM union_1
    GROUP BY union_1.MANDT, union_1.ENTITY
  union_2 AS (
    UNION ALL
        union_2.MANDT AS MANDT,
        union_2.ERSDA AS ERSDA,
        union_2.MATNR AS MATNR
    FROM union_2
    GROUP BY union_2.MANDT, union_2.ERSDA, union_2.MATNR

C:\Users\USER\Google Drive\SW_PLATFORM\15. AI\MY_LATEST_FILES\EXODUS\XML to SQL>venv\Scripts\python -m xml_to_sql.cli convert --config config.yaml --scenario CURRENT_MAT_SORT
[plan] C:\Users\USER\Google Drive\SW_PLATFORM\15. AI\MY_LATEST_FILES\EXODUS\XML to SQL\Source (XML Files)\CURRENT_MAT_SORT.XML -> C:\Users\USER\Google Drive\SW_PLATFORM\15. AI\MY_LATEST_FILES\EXODUS\XML to SQL\Target (SQL Scripts)\V_C_CURRENT_MAT_SORT.sql
  Scenario ID: CURRENT_MAT_SORT
  Nodes parsed: 4
  Filters detected: 2
  Calculated columns: 0
  Logical model: present
  Planned SQL target: C:\Users\USER\Google Drive\SW_PLATFORM\15. AI\MY_LATEST_FILES\EXODUS\XML to SQL\Target (SQL Scripts)\V_C_CURRENT_MAT_SORT.sql
  ✓ SQL generated: C:\Users\USER\Google Drive\SW_PLATFORM\15. AI\MY_LATEST_FILES\EXODUS\XML to SQL\Target (SQL Scripts)\V_C_CURRENT_MAT_SORT.sql

C:\Users\USER\Google Drive\SW_PLATFORM\15. AI\MY_LATEST_FILES\EXODUS\XML to SQL>venv\Scripts\python -m xml_to_sql.cli convert --config config.yaml --scenario "Material Details"
[plan] C:\Users\USER\Google Drive\SW_PLATFORM\15. AI\MY_LATEST_FILES\EXODUS\XML to SQL\Source (XML Files)\Material Details.XML -> C:\Users\USER\Google Drive\SW_PLATFORM\15. AI\MY_LATEST_FILES\EXODUS\XML to SQL\Target (SQL Scripts)\V_C_MATERIAL_DETAILS.sql
  Scenario ID: MATERIAL_DETAILS
  Nodes parsed: 0
  Filters detected: 0
  Calculated columns: 0
  Logical model: present
  Planned SQL target: C:\Users\USER\Google Drive\SW_PLATFORM\15. AI\MY_LATEST_FILES\EXODUS\XML to SQL\Target (SQL Scripts)\V_C_MATERIAL_DETAILS.sql
  ✓ SQL generated: C:\Users\USER\Google Drive\SW_PLATFORM\15. AI\MY_LATEST_FILES\EXODUS\XML to SQL\Target (SQL Scripts)\V_C_MATERIAL_DETAILS.sql

C:\Users\USER\Google Drive\SW_PLATFORM\15. AI\MY_LATEST_FILES\EXODUS\XML to SQL>venv\Scripts\python -m xml_to_sql.cli convert --config config.yaml --scenario Sold_Materials_PROD
[plan] C:\Users\USER\Google Drive\SW_PLATFORM\15. AI\MY_LATEST_FILES\EXODUS\XML to SQL\Source (XML Files)\Sold_Materials_PROD.XML -> C:\Users\USER\Google Drive\SW_PLATFORM\15. AI\MY_LATEST_FILES\EXODUS\XML to SQL\Target (SQL Scripts)\V_C_SOLD_MATERIALS_PROD.sql
  Scenario ID: Sold_Materials_PROD
  Nodes parsed: 6
  Filters detected: 1
  Calculated columns: 0
  Logical model: present
  Planned SQL target: C:\Users\USER\Google Drive\SW_PLATFORM\15. AI\MY_LATEST_FILES\EXODUS\XML to SQL\Target (SQL Scripts)\V_C_SOLD_MATERIALS_PROD.sql
  ✓ SQL generated: C:\Users\USER\Google Drive\SW_PLATFORM\15. AI\MY_LATEST_FILES\EXODUS\XML to SQL\Target (SQL Scripts)\V_C_SOLD_MATERIALS_PROD.sql

C:\Users\USER\Google Drive\SW_PLATFORM\15. AI\MY_LATEST_FILES\EXODUS\XML to SQL>venv\Scripts\python -m xml_to_sql.cli convert --config config.yaml
[plan] C:\Users\USER\Google Drive\SW_PLATFORM\15. AI\MY_LATEST_FILES\EXODUS\XML to SQL\Source (XML Files)\Sold_Materials.XML -> C:\Users\USER\Google Drive\SW_PLATFORM\15. AI\MY_LATEST_FILES\EXODUS\XML to SQL\Target (SQL Scripts)\V_C_SOLD_MATERIALS.sql
  Scenario ID: Sold_Materials
  Nodes parsed: 2
  Filters detected: 1
  Calculated columns: 0
  Logical model: present
  Planned SQL target: C:\Users\USER\Google Drive\SW_PLATFORM\15. AI\MY_LATEST_FILES\EXODUS\XML to SQL\Target (SQL Scripts)\V_C_SOLD_MATERIALS.sql
  ✓ SQL generated: C:\Users\USER\Google Drive\SW_PLATFORM\15. AI\MY_LATEST_FILES\EXODUS\XML to SQL\Target (SQL Scripts)\V_C_SOLD_MATERIALS.sql
[plan] C:\Users\USER\Google Drive\SW_PLATFORM\15. AI\MY_LATEST_FILES\EXODUS\XML to SQL\Source (XML Files)\SALES_BOM.XML -> C:\Users\USER\Google Drive\SW_PLATFORM\15. AI\MY_LATEST_FILES\EXODUS\XML to SQL\Target (SQL Scripts)\V_C_SALES_BOM.sql
  Scenario ID: SALES_BOM
  Nodes parsed: 10
  Filters detected: 5
  Calculated columns: 0
  Logical model: present
  Planned SQL target: C:\Users\USER\Google Drive\SW_PLATFORM\15. AI\MY_LATEST_FILES\EXODUS\XML to SQL\Target (SQL Scripts)\V_C_SALES_BOM.sql
  ✓ SQL generated: C:\Users\USER\Google Drive\SW_PLATFORM\15. AI\MY_LATEST_FILES\EXODUS\XML to SQL\Target (SQL Scripts)\V_C_SALES_BOM.sql
[plan] C:\Users\USER\Google Drive\SW_PLATFORM\15. AI\MY_LATEST_FILES\EXODUS\XML to SQL\Source (XML Files)\Recently_created_products.XML -> C:\Users\USER\Google Drive\SW_PLATFORM\15. AI\MY_LATEST_FILES\EXODUS\XML to SQL\Target (SQL Scripts)\V_C_RECENTLY_CREATED_PRODUCTS.sql
  Scenario ID: Recently_created_products
  Nodes parsed: 10
  Filters detected: 1
  Calculated columns: 0
  Logical model: present
  Planned SQL target: C:\Users\USER\Google Drive\SW_PLATFORM\15. AI\MY_LATEST_FILES\EXODUS\XML to SQL\Target (SQL Scripts)\V_C_RECENTLY_CREATED_PRODUCTS.sql
  ✓ SQL generated: C:\Users\USER\Google Drive\SW_PLATFORM\15. AI\MY_LATEST_FILES\EXODUS\XML to SQL\Target (SQL Scripts)\V_C_RECENTLY_CREATED_PRODUCTS.sql
[plan] C:\Users\USER\Google Drive\SW_PLATFORM\15. AI\MY_LATEST_FILES\EXODUS\XML to SQL\Source (XML Files)\Material Details.XML -> C:\Users\USER\Google Drive\SW_PLATFORM\15. AI\MY_LATEST_FILES\EXODUS\XML to SQL\Target (SQL Scripts)\V_C_MATERIAL_DETAILS.sql
  Scenario ID: MATERIAL_DETAILS
  Nodes parsed: 0
  Filters detected: 0
  Calculated columns: 0
  Logical model: present
  Planned SQL target: C:\Users\USER\Google Drive\SW_PLATFORM\15. AI\MY_LATEST_FILES\EXODUS\XML to SQL\Target (SQL Scripts)\V_C_MATERIAL_DETAILS.sql
  ✓ SQL generated: C:\Users\USER\Google Drive\SW_PLATFORM\15. AI\MY_LATEST_FILES\EXODUS\XML to SQL\Target (SQL Scripts)\V_C_MATERIAL_DETAILS.sql
[plan] C:\Users\USER\Google Drive\SW_PLATFORM\15. AI\MY_LATEST_FILES\EXODUS\XML to SQL\Source (XML Files)\KMDM_Materials.XML -> C:\Users\USER\Google Drive\SW_PLATFORM\15. AI\MY_LATEST_FILES\EXODUS\XML to SQL\Target (SQL Scripts)\V_C_KMDM_MATERIALS.sql
  Scenario ID: KMDM_Materials
  Nodes parsed: 11
  Filters detected: 1
  Calculated columns: 0
  Logical model: present
  Planned SQL target: C:\Users\USER\Google Drive\SW_PLATFORM\15. AI\MY_LATEST_FILES\EXODUS\XML to SQL\Target (SQL Scripts)\V_C_KMDM_MATERIALS.sql
  ✓ SQL generated: C:\Users\USER\Google Drive\SW_PLATFORM\15. AI\MY_LATEST_FILES\EXODUS\XML to SQL\Target (SQL Scripts)\V_C_KMDM_MATERIALS.sql
[plan] C:\Users\USER\Google Drive\SW_PLATFORM\15. AI\MY_LATEST_FILES\EXODUS\XML to SQL\Source (XML Files)\CURRENT_MAT_SORT.XML -> C:\Users\USER\Google Drive\SW_PLATFORM\15. AI\MY_LATEST_FILES\EXODUS\XML to SQL\Target (SQL Scripts)\V_C_CURRENT_MAT_SORT.sql
  Scenario ID: CURRENT_MAT_SORT
  Nodes parsed: 4
  Filters detected: 2
  Calculated columns: 0
  Logical model: present
  Planned SQL target: C:\Users\USER\Google Drive\SW_PLATFORM\15. AI\MY_LATEST_FILES\EXODUS\XML to SQL\Target (SQL Scripts)\V_C_CURRENT_MAT_SORT.sql
  ✓ SQL generated: C:\Users\USER\Google Drive\SW_PLATFORM\15. AI\MY_LATEST_FILES\EXODUS\XML to SQL\Target (SQL Scripts)\V_C_CURRENT_MAT_SORT.sql
[plan] C:\Users\USER\Google Drive\SW_PLATFORM\15. AI\MY_LATEST_FILES\EXODUS\XML to SQL\Source (XML Files)\Sold_Materials_PROD.XML -> C:\Users\USER\Google Drive\SW_PLATFORM\15. AI\MY_LATEST_FILES\EXODUS\XML to SQL\Target (SQL Scripts)\V_C_SOLD_MATERIALS_PROD.sql
  Scenario ID: Sold_Materials_PROD
  Nodes parsed: 6
  Filters detected: 1
  Calculated columns: 0
  Logical model: present
  Planned SQL target: C:\Users\USER\Google Drive\SW_PLATFORM\15. AI\MY_LATEST_FILES\EXODUS\XML to SQL\Target (SQL Scripts)\V_C_SOLD_MATERIALS_PROD.sql
  ✓ SQL generated: C:\Users\USER\Google Drive\SW_PLATFORM\15. AI\MY_LATEST_FILES\EXODUS\XML to SQL\Target (SQL Scripts)\V_C_SOLD_MATERIALS_PROD.sql

C:\Users\USER\Google Drive\SW_PLATFORM\15. AI\MY_LATEST_FILES\EXODUS\XML to SQL>dir "Target (SQL Scripts)\*.sql"
 Volume in drive C is OS
 Volume Serial Number is 4E9D-4825

 Directory of C:\Users\USER\Google Drive\SW_PLATFORM\15. AI\MY_LATEST_FILES\EXODUS\XML to SQL\Target (SQL Scripts)

11/08/2025  01:27 PM             1,978 V_C_CURRENT_MAT_SORT.sql
11/08/2025  01:27 PM             5,211 V_C_KMDM_MATERIALS.sql
11/08/2025  01:27 PM                19 V_C_MATERIAL_DETAILS.sql
11/08/2025  01:27 PM             2,556 V_C_RECENTLY_CREATED_PRODUCTS.sql
11/08/2025  01:27 PM             4,267 V_C_SALES_BOM.sql
11/08/2025  01:27 PM               574 V_C_SOLD_MATERIALS.sql
11/08/2025  01:27 PM             2,218 V_C_SOLD_MATERIALS_PROD.sql
               7 File(s)         16,823 bytes
               0 Dir(s)  40,393,535,488 bytes free

C:\Users\USER\Google Drive\SW_PLATFORM\15. AI\MY_LATEST_FILES\EXODUS\XML to SQL>for %f in ("Target (SQL Scripts)\*.sql") do @echo %f && @type "%f" | findstr /c:"SELECT" >nul && echo [OK] || echo [MISSING SELECT]
Target (SQL Scripts)\V_C_CURRENT_MAT_SORT.sql
[OK]
Target (SQL Scripts)\V_C_KMDM_MATERIALS.sql
[OK]
Target (SQL Scripts)\V_C_MATERIAL_DETAILS.sql
[OK]
Target (SQL Scripts)\V_C_RECENTLY_CREATED_PRODUCTS.sql
[OK]
Target (SQL Scripts)\V_C_SALES_BOM.sql
[OK]
Target (SQL Scripts)\V_C_SOLD_MATERIALS.sql
[OK]
Target (SQL Scripts)\V_C_SOLD_MATERIALS_PROD.sql
[OK]

C:\Users\USER\Google Drive\SW_PLATFORM\15. AI\MY_LATEST_FILES\EXODUS\XML to SQL>type "Target (SQL Scripts)\V_C_SOLD_MATERIALS.sql" | findstr /i "WITH"
WITH

C:\Users\USER\Google Drive\SW_PLATFORM\15. AI\MY_LATEST_FILES\EXODUS\XML to SQL>type "Target (SQL Scripts)\V_C_SOLD_MATERIALS.sql" | findstr /i "AS"
  projection_1 AS (
        SAPK5D.VBAP.MATNR AS MATNR,
        SAPK5D.VBAP.ERDAT AS ERDAT,
        SAPK5D.VBAP.MEINS AS MEINS,
        SAPK5D.VBAP.MANDT AS MANDT
  aggregation_1 AS (
        projection_1.MANDT AS MANDT,
        projection_1.MATNR AS MATNR,
        projection_1.MEINS AS MEINS,
        MAX(projection_1.ERDAT) AS ERDAT

C:\Users\USER\Google Drive\SW_PLATFORM\15. AI\MY_LATEST_FILES\EXODUS\XML to SQL>type "Target (SQL Scripts)\V_C_SOLD_MATERIALS.sql" | findstr /i "WHERE"
    WHERE SAPK5D.VBAP.ERDAT > 20140101

C:\Users\USER\Google Drive\SW_PLATFORM\15. AI\MY_LATEST_FILES\EXODUS\XML to SQL>type "Target (SQL Scripts)\*.sql" | findstr /i "IFF"

Target (SQL Scripts)\V_C_CURRENT_MAT_SORT.sql



Target (SQL Scripts)\V_C_KMDM_MATERIALS.sql



Target (SQL Scripts)\V_C_MATERIAL_DETAILS.sql



Target (SQL Scripts)\V_C_RECENTLY_CREATED_PRODUCTS.sql



Target (SQL Scripts)\V_C_SALES_BOM.sql



Target (SQL Scripts)\V_C_SOLD_MATERIALS.sql



Target (SQL Scripts)\V_C_SOLD_MATERIALS_PROD.sql



C:\Users\USER\Google Drive\SW_PLATFORM\15. AI\MY_LATEST_FILES\EXODUS\XML to SQL>type "Target (SQL Scripts)\*.sql" | findstr /c:"||"

Target (SQL Scripts)\V_C_CURRENT_MAT_SORT.sql



Target (SQL Scripts)\V_C_KMDM_MATERIALS.sql



Target (SQL Scripts)\V_C_MATERIAL_DETAILS.sql



Target (SQL Scripts)\V_C_RECENTLY_CREATED_PRODUCTS.sql



Target (SQL Scripts)\V_C_SALES_BOM.sql



Target (SQL Scripts)\V_C_SOLD_MATERIALS.sql



Target (SQL Scripts)\V_C_SOLD_MATERIALS_PROD.sql



C:\Users\USER\Google Drive\SW_PLATFORM\15. AI\MY_LATEST_FILES\EXODUS\XML to SQL>type "Target (SQL Scripts)\*.sql" | findstr /i /c:"UNION ALL" /c:"UNION"

Target (SQL Scripts)\V_C_CURRENT_MAT_SORT.sql



Target (SQL Scripts)\V_C_KMDM_MATERIALS.sql


  union_1 AS (
    UNION ALL
    UNION ALL
    UNION ALL
        union_1.MANDT AS MANDT,
        union_1.MATNR AS MATNR,
        union_1.MEINS AS MEINS,

Target (SQL Scripts)\V_C_MATERIAL_DETAILS.sql


        MAX(union_1.ERDAT) AS ERDAT
    FROM union_1
    GROUP BY union_1.MANDT, union_1.MATNR, union_1.MEINS

Target (SQL Scripts)\V_C_RECENTLY_CREATED_PRODUCTS.sql


  union_1 AS (
    UNION ALL
        union_1.MANDT AS MANDT,
        union_1.ENTITY AS ENTITY
    FROM union_1
    GROUP BY union_1.MANDT, union_1.ENTITY
  union_2 AS (

Target (SQL Scripts)\V_C_SALES_BOM.sql


    UNION ALL
        union_2.MANDT AS MANDT,
        union_2.ERSDA AS ERSDA,
        union_2.MATNR AS MATNR
    FROM union_2
    GROUP BY union_2.MANDT, union_2.ERSDA, union_2.MATNR

Target (SQL Scripts)\V_C_SOLD_MATERIALS.sql



Target (SQL Scripts)\V_C_SOLD_MATERIALS_PROD.sql


  union_1 AS (
    UNION ALL
        union_1.MANDT AS MANDT,
        union_1.ERDAT AS ERDAT,
        union_1.MATNR AS "JOIN$MATNR$MATNR",
        union_1.LONG_OLD_NUMBER AS LONG_OLD_NUMBER,
        union_1.MEINS AS MEINS,
        union_1.MATNR AS "JOIN$MATNR$MATNR",
        union_1.MANDT AS MANDT
    FROM union_1

C:\Users\USER\Google Drive\SW_PLATFORM\15. AI\MY_LATEST_FILES\EXODUS\XML to SQL>type "Target (SQL Scripts)\*.sql" | findstr /i "GROUP BY"

Target (SQL Scripts)\V_C_CURRENT_MAT_SORT.sql



Target (SQL Scripts)\V_C_KMDM_MATERIALS.sql


    GROUP BY projection_1.MANDT, projection_1.CODAPL, projection_1.LVLGRP, projection_1.ENTITY

Target (SQL Scripts)\V_C_MATERIAL_DETAILS.sql


    GROUP BY union_1.MANDT, union_1.MATNR, union_1.MEINS

Target (SQL Scripts)\V_C_RECENTLY_CREATED_PRODUCTS.sql


    GROUP BY union_1.MANDT, union_1.ENTITY

Target (SQL Scripts)\V_C_SALES_BOM.sql


    GROUP BY union_2.MANDT, union_2.ERSDA, union_2.MATNR
    GROUP BY "/KMDM/CALCULATIONVIEWS/CURRENT_MAT_SORT".CODAPL, "/KMDM/CALCULATIONVIEWS/CURRENT_MAT_SORT".LVLGRP, "/KMDM/CALCULATIONVIEWS/CURRENT_MAT_SORT".ENTITY

Target (SQL Scripts)\V_C_SOLD_MATERIALS.sql


    GROUP BY join_2.MENGE, join_2.MEINS, join_2.PSWRK, join_2.IDNRK, join_2.STLAL, join_2.STLNR, join_2.STLAN, join_2.MATNR, join_2.MANDT, join_2.NUMGRP

Target (SQL Scripts)\V_C_SOLD_MATERIALS_PROD.sql


    GROUP BY projection_1.MANDT, projection_1.MATNR, projection_1.MEINS
    GROUP BY "/KMDM/CALCULATIONVIEWS/SALES_BOM".MANDT, "/KMDM/CALCULATIONVIEWS/SALES_BOM".IDNRK
    GROUP BY join_1.LONG_OLD_NUMBER, join_1.MEINS, join_1.MANDT

C:\Users\USER\Google Drive\SW_PLATFORM\15. AI\MY_LATEST_FILES\EXODUS\XML to SQL>copy config.yaml config.test.yaml
        1 file(s) copied.

C:\Users\USER\Google Drive\SW_PLATFORM\15. AI\MY_LATEST_FILES\EXODUS\XML to SQL>venv\Scripts\python -m xml_to_sql.cli convert --config config.test.yaml --scenario NonExistent
No scenarios matched the requested filters.

C:\Users\USER\Google Drive\SW_PLATFORM\15. AI\MY_LATEST_FILES\EXODUS\XML to SQL>echo invalid: yaml: [ > config.invalid.yaml

C:\Users\USER\Google Drive\SW_PLATFORM\15. AI\MY_LATEST_FILES\EXODUS\XML to SQL>venv\Scripts\python -m xml_to_sql.cli list --config config.invalid.yaml
╭───────────────────────────────────────────────────────────────────────────────── Traceback (most recent call last) ─────────────────────────────────────────────────────────────────────────────────╮
│ C:\Users\USER\Google Drive\SW_PLATFORM\15. AI\MY_LATEST_FILES\EXODUS\XML to SQL\src\xml_to_sql\cli\app.py:88 in list_scenarios                                                                      │
│                                                                                                                                                                                                     │
│    85 ) -> None:                                                                               ╭────────────────── locals ───────────────────╮                                                      │
│    86 │   """Display scenarios defined in the configuration file."""                           │ config = WindowsPath('config.invalid.yaml') │                                                      │
│    87 │                                                                                        ╰─────────────────────────────────────────────╯                                                      │
│ ❱  88 │   config_obj = load_config(config)                                                                                                                                                          │
│    89 │   if not config_obj.scenarios:                                                                                                                                                              │
│    90 │   │   typer.echo("No scenarios defined.")                                                                                                                                                   │
│    91 │   │   raise typer.Exit()                                                                                                                                                                    │
│                                                                                                                                                                                                     │
│ C:\Users\USER\Google Drive\SW_PLATFORM\15. AI\MY_LATEST_FILES\EXODUS\XML to SQL\src\xml_to_sql\config\loader.py:22 in load_config                                                                   │
│                                                                                                                                                                                                     │
│    19 │                                                                                                                                                                                             │
│    20 │   config_path = Path(path).expanduser().resolve()                                                                                                                                           │
│    21 │   with config_path.open("r", encoding="utf-8") as handle:                                                                                                                                   │
│ ❱  22 │   │   raw_data = yaml.safe_load(handle) or {}                                                                                                                                               │
│    23 │                                                                                                                                                                                             │
│    24 │   if not isinstance(raw_data, dict):                                                                                                                                                        │
│    25 │   │   raise ValueError("Configuration root must be a mapping.")                                                                                                                             │
│                                                                                                                                                                                                     │
│ ╭──────────────────────────────────────────────────────────────────────────────────── locals ─────────────────────────────────────────────────────────────────────────────────────╮                 │
│ │ config_path = WindowsPath('C:/Users/USER/Google Drive/SW_PLATFORM/15. AI/MY_LATEST_FILES/EXODUS/XML to SQL/config.invalid.yaml')                                                │                 │
│ │      handle = <_io.TextIOWrapper name='C:\\Users\\USER\\Google Drive\\SW_PLATFORM\\15. AI\\MY_LATEST_FILES\\EXODUS\\XML to SQL\\config.invalid.yaml' mode='r' encoding='utf-8'> │                 │
│ │        path = WindowsPath('config.invalid.yaml')                                                                                                                                │                 │
│ ╰─────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────╯                 │
│                                                                                                                                                                                                     │
│ C:\Users\USER\Google Drive\SW_PLATFORM\15. AI\MY_LATEST_FILES\EXODUS\XML to SQL\venv\Lib\site-packages\yaml\__init__.py:125 in safe_load                                                            │
│                                                                                                                                                                                                     │
│   122 │   Resolve only basic YAML tags. This is known                                                                                                                                               │
│   123 │   to be safe for untrusted input.                                                                                                                                                           │
│   124 │   """                                                                                                                                                                                       │
│ ❱ 125 │   return load(stream, SafeLoader)                                                                                                                                                           │
│   126                                                                                                                                                                                               │
│   127 def safe_load_all(stream):                                                                                                                                                                    │
│   128 │   """                                                                                                                                                                                       │
│                                                                                                                                                                                                     │
│ ╭────────────────────────────────────────────────────────────────────────────────── locals ──────────────────────────────────────────────────────────────────────────────────╮                      │
│ │ stream = <_io.TextIOWrapper name='C:\\Users\\USER\\Google Drive\\SW_PLATFORM\\15. AI\\MY_LATEST_FILES\\EXODUS\\XML to SQL\\config.invalid.yaml' mode='r' encoding='utf-8'> │                      │
│ ╰────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────╯                      │
│                                                                                                                                                                                                     │
│ C:\Users\USER\Google Drive\SW_PLATFORM\15. AI\MY_LATEST_FILES\EXODUS\XML to SQL\venv\Lib\site-packages\yaml\__init__.py:81 in load                                                                  │
│                                                                                                                                                                                                     │
│    78 │   """                                                                                                                                                                                       │
│    79 │   loader = Loader(stream)                                                                                                                                                                   │
│    80 │   try:                                                                                                                                                                                      │
│ ❱  81 │   │   return loader.get_single_data()                                                                                                                                                       │
│    82 │   finally:                                                                                                                                                                                  │
│    83 │   │   loader.dispose()                                                                                                                                                                      │
│    84                                                                                                                                                                                               │
│                                                                                                                                                                                                     │
│ ╭────────────────────────────────────────────────────────────────────────────────── locals ──────────────────────────────────────────────────────────────────────────────────╮                      │
│ │ loader = <yaml.loader.SafeLoader object at 0x0000026587C72510>                                                                                                             │                      │
│ │ stream = <_io.TextIOWrapper name='C:\\Users\\USER\\Google Drive\\SW_PLATFORM\\15. AI\\MY_LATEST_FILES\\EXODUS\\XML to SQL\\config.invalid.yaml' mode='r' encoding='utf-8'> │                      │
│ ╰────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────╯                      │
│                                                                                                                                                                                                     │
│ C:\Users\USER\Google Drive\SW_PLATFORM\15. AI\MY_LATEST_FILES\EXODUS\XML to SQL\venv\Lib\site-packages\yaml\constructor.py:49 in get_single_data                                                    │
│                                                                                                                                                                                                     │
│    46 │                                                                                        ╭─────────────────────────── locals ───────────────────────────╮                                     │
│    47 │   def get_single_data(self):                                                           │ self = <yaml.loader.SafeLoader object at 0x0000026587C72510> │                                     │
│    48 │   │   # Ensure that the stream contains a single document and construct it.            ╰──────────────────────────────────────────────────────────────╯                                     │
│ ❱  49 │   │   node = self.get_single_node()                                                                                                                                                         │
│    50 │   │   if node is not None:                                                                                                                                                                  │
│    51 │   │   │   return self.construct_document(node)                                                                                                                                              │
│    52 │   │   return None                                                                                                                                                                           │
│                                                                                                                                                                                                     │
│ C:\Users\USER\Google Drive\SW_PLATFORM\15. AI\MY_LATEST_FILES\EXODUS\XML to SQL\venv\Lib\site-packages\yaml\composer.py:36 in get_single_node                                                       │
│                                                                                                                                                                                                     │
│    33 │   │   # Compose a document if the stream is not empty.                                 ╭───────────────────────────── locals ─────────────────────────────╮                                 │
│    34 │   │   document = None                                                                  │ document = None                                                  │                                 │
│    35 │   │   if not self.check_event(StreamEndEvent):                                         │     self = <yaml.loader.SafeLoader object at 0x0000026587C72510> │                                 │
│ ❱  36 │   │   │   document = self.compose_document()                                           ╰──────────────────────────────────────────────────────────────────╯                                 │
│    37 │   │                                                                                                                                                                                         │
│    38 │   │   # Ensure that the stream contains no more documents.                                                                                                                                  │
│    39 │   │   if not self.check_event(StreamEndEvent):                                                                                                                                              │
│                                                                                                                                                                                                     │
│ C:\Users\USER\Google Drive\SW_PLATFORM\15. AI\MY_LATEST_FILES\EXODUS\XML to SQL\venv\Lib\site-packages\yaml\composer.py:55 in compose_document                                                      │
│                                                                                                                                                                                                     │
│    52 │   │   self.get_event()                                                                 ╭─────────────────────────── locals ───────────────────────────╮                                     │
│    53 │   │                                                                                    │ self = <yaml.loader.SafeLoader object at 0x0000026587C72510> │                                     │
│    54 │   │   # Compose the root node.                                                         ╰──────────────────────────────────────────────────────────────╯                                     │
│ ❱  55 │   │   node = self.compose_node(None, None)                                                                                                                                                  │
│    56 │   │                                                                                                                                                                                         │
│    57 │   │   # Drop the DOCUMENT-END event.                                                                                                                                                        │
│    58 │   │   self.get_event()                                                                                                                                                                      │
│                                                                                                                                                                                                     │
│ C:\Users\USER\Google Drive\SW_PLATFORM\15. AI\MY_LATEST_FILES\EXODUS\XML to SQL\venv\Lib\site-packages\yaml\composer.py:84 in compose_node                                                          │
│                                                                                                                                                                                                     │
│    81 │   │   elif self.check_event(SequenceStartEvent):                                       ╭───────────────────────────── locals ─────────────────────────────╮                                 │
│    82 │   │   │   node = self.compose_sequence_node(anchor)                                    │ anchor = None                                                    │                                 │
│    83 │   │   elif self.check_event(MappingStartEvent):                                        │  event = MappingStartEvent(anchor=None, tag=None, implicit=True) │                                 │
│ ❱  84 │   │   │   node = self.compose_mapping_node(anchor)                                     │  index = None                                                    │                                 │
│    85 │   │   self.ascend_resolver()                                                           │ parent = None                                                    │                                 │
│    86 │   │   return node                                                                      │   self = <yaml.loader.SafeLoader object at 0x0000026587C72510>   │                                 │
│    87                                                                                          ╰──────────────────────────────────────────────────────────────────╯                                 │
│                                                                                                                                                                                                     │
│ C:\Users\USER\Google Drive\SW_PLATFORM\15. AI\MY_LATEST_FILES\EXODUS\XML to SQL\venv\Lib\site-packages\yaml\composer.py:127 in compose_mapping_node                                                 │
│                                                                                                                                                                                                     │
│   124 │   │   │   │   flow_style=start_event.flow_style)                                                                                                                                            │
│   125 │   │   if anchor is not None:                                                                                                                                                                │
│   126 │   │   │   self.anchors[anchor] = node                                                                                                                                                       │
│ ❱ 127 │   │   while not self.check_event(MappingEndEvent):                                                                                                                                          │
│   128 │   │   │   #key_event = self.peek_event()                                                                                                                                                    │
│   129 │   │   │   item_key = self.compose_node(node, None)                                                                                                                                          │
│   130 │   │   │   #if item_key in node.value:                                                                                                                                                       │
│                                                                                                                                                                                                     │
│ ╭───────────────────────────────────────────────────────────────────────────────────── locals ──────────────────────────────────────────────────────────────────────────────────────╮               │
│ │      anchor = None                                                                                                                                                                │               │
│ │    item_key = ScalarNode(tag='tag:yaml.org,2002:str', value='invalid')                                                                                                            │               │
│ │  item_value = ScalarNode(tag='tag:yaml.org,2002:str', value='yaml')                                                                                                               │               │
│ │        node = MappingNode(tag='tag:yaml.org,2002:map', value=[(ScalarNode(tag='tag:yaml.org,2002:str', value='invalid'), ScalarNode(tag='tag:yaml.org,2002:str', value='yaml'))]) │               │
│ │        self = <yaml.loader.SafeLoader object at 0x0000026587C72510>                                                                                                               │               │
│ │ start_event = MappingStartEvent(anchor=None, tag=None, implicit=True)                                                                                                             │               │
│ │         tag = 'tag:yaml.org,2002:map'                                                                                                                                             │               │
│ ╰───────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────╯               │
│                                                                                                                                                                                                     │
│ C:\Users\USER\Google Drive\SW_PLATFORM\15. AI\MY_LATEST_FILES\EXODUS\XML to SQL\venv\Lib\site-packages\yaml\parser.py:98 in check_event                                                             │
│                                                                                                                                                                                                     │
│    95 │   │   # Check the type of the next event.                                              ╭──────────────────────────── locals ─────────────────────────────╮                                  │
│    96 │   │   if self.current_event is None:                                                   │ choices = (<class 'yaml.events.MappingEndEvent'>,)              │                                  │
│    97 │   │   │   if self.state:                                                               │    self = <yaml.loader.SafeLoader object at 0x0000026587C72510> │                                  │
│ ❱  98 │   │   │   │   self.current_event = self.state()                                        ╰─────────────────────────────────────────────────────────────────╯                                  │
│    99 │   │   if self.current_event is not None:                                                                                                                                                    │
│   100 │   │   │   if not choices:                                                                                                                                                                   │
│   101 │   │   │   │   return True                                                                                                                                                                   │
│                                                                                                                                                                                                     │
│ C:\Users\USER\Google Drive\SW_PLATFORM\15. AI\MY_LATEST_FILES\EXODUS\XML to SQL\venv\Lib\site-packages\yaml\parser.py:428 in parse_block_mapping_key                                                │
│                                                                                                                                                                                                     │
│   425 │   │   return self.parse_block_mapping_key()                                            ╭─────────────────────────── locals ───────────────────────────╮                                     │
│   426 │                                                                                        │ self = <yaml.loader.SafeLoader object at 0x0000026587C72510> │                                     │
│   427 │   def parse_block_mapping_key(self):                                                   ╰──────────────────────────────────────────────────────────────╯                                     │
│ ❱ 428 │   │   if self.check_token(KeyToken):                                                                                                                                                        │
│   429 │   │   │   token = self.get_token()                                                                                                                                                          │
│   430 │   │   │   if not self.check_token(KeyToken, ValueToken, BlockEndToken):                                                                                                                     │
│   431 │   │   │   │   self.states.append(self.parse_block_mapping_value)                                                                                                                            │
│                                                                                                                                                                                                     │
│ C:\Users\USER\Google Drive\SW_PLATFORM\15. AI\MY_LATEST_FILES\EXODUS\XML to SQL\venv\Lib\site-packages\yaml\scanner.py:116 in check_token                                                           │
│                                                                                                                                                                                                     │
│    113 │   def check_token(self, *choices):                                                     ╭──────────────────────────── locals ─────────────────────────────╮                                 │
│    114 │   │   # Check if the next token is one of the given types.                             │ choices = (<class 'yaml.tokens.KeyToken'>,)                     │                                 │
│    115 │   │   while self.need_more_tokens():                                                   │    self = <yaml.loader.SafeLoader object at 0x0000026587C72510> │                                 │
│ ❱  116 │   │   │   self.fetch_more_tokens()                                                     ╰─────────────────────────────────────────────────────────────────╯                                 │
│    117 │   │   if self.tokens:                                                                                                                                                                      │
│    118 │   │   │   if not choices:                                                                                                                                                                  │
│    119 │   │   │   │   return True                                                                                                                                                                  │
│                                                                                                                                                                                                     │
│ C:\Users\USER\Google Drive\SW_PLATFORM\15. AI\MY_LATEST_FILES\EXODUS\XML to SQL\venv\Lib\site-packages\yaml\scanner.py:223 in fetch_more_tokens                                                     │
│                                                                                                                                                                                                     │
│    220 │   │                                                                                    ╭─────────────────────────── locals ───────────────────────────╮                                    │
│    221 │   │   # Is it the value indicator?                                                     │   ch = ':'                                                   │                                    │
│    222 │   │   if ch == ':' and self.check_value():                                             │ self = <yaml.loader.SafeLoader object at 0x0000026587C72510> │                                    │
│ ❱  223 │   │   │   return self.fetch_value()                                                    ╰──────────────────────────────────────────────────────────────╯                                    │
│    224 │   │                                                                                                                                                                                        │
│    225 │   │   # Is it an alias?                                                                                                                                                                    │
│    226 │   │   if ch == '*':                                                                                                                                                                        │
│                                                                                                                                                                                                     │
│ C:\Users\USER\Google Drive\SW_PLATFORM\15. AI\MY_LATEST_FILES\EXODUS\XML to SQL\venv\Lib\site-packages\yaml\scanner.py:577 in fetch_value                                                           │
│                                                                                                                                                                                                     │
│    574 │   │   │   │   # We are allowed to start a complex value if and only if                 ╭─────────────────────────── locals ───────────────────────────╮                                    │
│    575 │   │   │   │   # we can start a simple key.                                             │ self = <yaml.loader.SafeLoader object at 0x0000026587C72510> │                                    │
│    576 │   │   │   │   if not self.allow_simple_key:                                            ╰──────────────────────────────────────────────────────────────╯                                    │
│ ❱  577 │   │   │   │   │   raise ScannerError(None, None,                                                                                                                                           │
│    578 │   │   │   │   │   │   │   "mapping values are not allowed here",                                                                                                                           │
│    579 │   │   │   │   │   │   │   self.get_mark())                                                                                                                                                 │
│    580                                                                                                                                                                                              │
╰─────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────╯
ScannerError: mapping values are not allowed here
  in "C:\Users\USER\Google Drive\SW_PLATFORM\15. AI\MY_LATEST_FILES\EXODUS\XML to SQL\config.invalid.yaml", line 1, column 14

C:\Users\USER\Google Drive\SW_PLATFORM\15. AI\MY_LATEST_FILES\EXODUS\XML to SQL>venv\Scripts\python -m xml_to_sql.cli convert --config config.yaml --scenario Sold_Materials
[plan] C:\Users\USER\Google Drive\SW_PLATFORM\15. AI\MY_LATEST_FILES\EXODUS\XML to SQL\Source (XML Files)\Sold_Materials.XML -> C:\Users\USER\Google Drive\SW_PLATFORM\15. AI\MY_LATEST_FILES\EXODUS\XML to SQL\Target (SQL Scripts)\V_C_SOLD_MATERIALS.sql
  Scenario ID: Sold_Materials
  Nodes parsed: 2
  Filters detected: 1
  Calculated columns: 0
  Logical model: present
  Planned SQL target: C:\Users\USER\Google Drive\SW_PLATFORM\15. AI\MY_LATEST_FILES\EXODUS\XML to SQL\Target (SQL Scripts)\V_C_SOLD_MATERIALS.sql
  ✓ SQL generated: C:\Users\USER\Google Drive\SW_PLATFORM\15. AI\MY_LATEST_FILES\EXODUS\XML to SQL\Target (SQL Scripts)\V_C_SOLD_MATERIALS.sql

C:\Users\USER\Google Drive\SW_PLATFORM\15. AI\MY_LATEST_FILES\EXODUS\XML to SQL>venv\Scripts\python -m pytest tests/test_sql_renderer.py::test_render_all_xml_samples -v
======================================================================================== test session starts =========================================================================================
platform win32 -- Python 3.11.9, pytest-8.4.2, pluggy-1.6.0 -- C:\Users\USER\Google Drive\SW_PLATFORM\15. AI\MY_LATEST_FILES\EXODUS\XML to SQL\venv\Scripts\python.exe
cachedir: .pytest_cache
rootdir: C:\Users\USER\Google Drive\SW_PLATFORM\15. AI\MY_LATEST_FILES\EXODUS\XML to SQL
configfile: pyproject.toml
collected 7 items

tests/test_sql_renderer.py::test_render_all_xml_samples[Sold_Materials.XML] PASSED                                                                                                              [ 14%]
tests/test_sql_renderer.py::test_render_all_xml_samples[SALES_BOM.XML] PASSED                                                                                                                   [ 28%]
tests/test_sql_renderer.py::test_render_all_xml_samples[Recently_created_products.XML] PASSED                                                                                                   [ 42%]
tests/test_sql_renderer.py::test_render_all_xml_samples[KMDM_Materials.XML] PASSED                                                                                                              [ 57%]
tests/test_sql_renderer.py::test_render_all_xml_samples[CURRENT_MAT_SORT.XML] PASSED                                                                                                            [ 71%]
tests/test_sql_renderer.py::test_render_all_xml_samples[Material Details.XML] PASSED                                                                                                            [ 85%]
tests/test_sql_renderer.py::test_render_all_xml_samples[Sold_Materials_PROD.XML] PASSED                                                                                                         [100%]

========================================================================================= 7 passed in 0.06s ==========================================================================================

C:\Users\USER\Google Drive\SW_PLATFORM\15. AI\MY_LATEST_FILES\EXODUS\XML to SQL>type "Target (SQL Scripts)\*.sql" | findstr /i "WARNING\|TODO\|FIXME"

Target (SQL Scripts)\V_C_CURRENT_MAT_SORT.sql



Target (SQL Scripts)\V_C_KMDM_MATERIALS.sql



Target (SQL Scripts)\V_C_MATERIAL_DETAILS.sql



Target (SQL Scripts)\V_C_RECENTLY_CREATED_PRODUCTS.sql



Target (SQL Scripts)\V_C_SALES_BOM.sql



Target (SQL Scripts)\V_C_SOLD_MATERIALS.sql



Target (SQL Scripts)\V_C_SOLD_MATERIALS_PROD.sql



C:\Users\USER\Google Drive\SW_PLATFORM\15. AI\MY_LATEST_FILES\EXODUS\XML to SQL>dir "Target (SQL Scripts)\*.sql"
 Volume in drive C is OS
 Volume Serial Number is 4E9D-4825

 Directory of C:\Users\USER\Google Drive\SW_PLATFORM\15. AI\MY_LATEST_FILES\EXODUS\XML to SQL\Target (SQL Scripts)

11/08/2025  01:27 PM             1,978 V_C_CURRENT_MAT_SORT.sql
11/08/2025  01:27 PM             5,211 V_C_KMDM_MATERIALS.sql
11/08/2025  01:27 PM                19 V_C_MATERIAL_DETAILS.sql
11/08/2025  01:27 PM             2,556 V_C_RECENTLY_CREATED_PRODUCTS.sql
11/08/2025  01:27 PM             4,267 V_C_SALES_BOM.sql
11/08/2025  01:35 PM               574 V_C_SOLD_MATERIALS.sql
11/08/2025  01:27 PM             2,218 V_C_SOLD_MATERIALS_PROD.sql
               7 File(s)         16,823 bytes
               0 Dir(s)  40,388,984,832 bytes free

C:\Users\USER\Google Drive\SW_PLATFORM\15. AI\MY_LATEST_FILES\EXODUS\XML to SQL>powershell -Command "Measure-Command { venv\Scripts\python -m xml_to_sql.cli convert --config config.yaml }"


Days              : 0
Hours             : 0
Minutes           : 0
Seconds           : 0
Milliseconds      : 262
Ticks             : 2629959
TotalDays         : 3.04393402777778E-06
TotalHours        : 7.30544166666667E-05
TotalMinutes      : 0.004383265
TotalSeconds      : 0.2629959
TotalMilliseconds : 262.9959




C:\Users\USER\Google Drive\SW_PLATFORM\15. AI\MY_LATEST_FILES\EXODUS\XML to SQL>dir "Target (SQL Scripts)\*.sql" | find /c ".sql"
7

C:\Users\USER\Google Drive\SW_PLATFORM\15. AI\MY_LATEST_FILES\EXODUS\XML to SQL>venv\Scripts\python -m xml_to_sql.cli convert --config config.yaml --list-only
[plan] C:\Users\USER\Google Drive\SW_PLATFORM\15. AI\MY_LATEST_FILES\EXODUS\XML to SQL\Source (XML Files)\Sold_Materials.XML -> C:\Users\USER\Google Drive\SW_PLATFORM\15. AI\MY_LATEST_FILES\EXODUS\XML to SQL\Target (SQL Scripts)\V_C_SOLD_MATERIALS.sql
[plan] C:\Users\USER\Google Drive\SW_PLATFORM\15. AI\MY_LATEST_FILES\EXODUS\XML to SQL\Source (XML Files)\SALES_BOM.XML -> C:\Users\USER\Google Drive\SW_PLATFORM\15. AI\MY_LATEST_FILES\EXODUS\XML to SQL\Target (SQL Scripts)\V_C_SALES_BOM.sql
[plan] C:\Users\USER\Google Drive\SW_PLATFORM\15. AI\MY_LATEST_FILES\EXODUS\XML to SQL\Source (XML Files)\Recently_created_products.XML -> C:\Users\USER\Google Drive\SW_PLATFORM\15. AI\MY_LATEST_FILES\EXODUS\XML to SQL\Target (SQL Scripts)\V_C_RECENTLY_CREATED_PRODUCTS.sql
[plan] C:\Users\USER\Google Drive\SW_PLATFORM\15. AI\MY_LATEST_FILES\EXODUS\XML to SQL\Source (XML Files)\Material Details.XML -> C:\Users\USER\Google Drive\SW_PLATFORM\15. AI\MY_LATEST_FILES\EXODUS\XML to SQL\Target (SQL Scripts)\V_C_MATERIAL_DETAILS.sql
[plan] C:\Users\USER\Google Drive\SW_PLATFORM\15. AI\MY_LATEST_FILES\EXODUS\XML to SQL\Source (XML Files)\KMDM_Materials.XML -> C:\Users\USER\Google Drive\SW_PLATFORM\15. AI\MY_LATEST_FILES\EXODUS\XML to SQL\Target (SQL Scripts)\V_C_KMDM_MATERIALS.sql
[plan] C:\Users\USER\Google Drive\SW_PLATFORM\15. AI\MY_LATEST_FILES\EXODUS\XML to SQL\Source (XML Files)\CURRENT_MAT_SORT.XML -> C:\Users\USER\Google Drive\SW_PLATFORM\15. AI\MY_LATEST_FILES\EXODUS\XML to SQL\Target (SQL Scripts)\V_C_CURRENT_MAT_SORT.sql
[plan] C:\Users\USER\Google Drive\SW_PLATFORM\15. AI\MY_LATEST_FILES\EXODUS\XML to SQL\Source (XML Files)\Sold_Materials_PROD.XML -> C:\Users\USER\Google Drive\SW_PLATFORM\15. AI\MY_LATEST_FILES\EXODUS\XML to SQL\Target (SQL Scripts)\V_C_SOLD_MATERIALS_PROD.sql

C:\Users\USER\Google Drive\SW_PLATFORM\15. AI\MY_LATEST_FILES\EXODUS\XML to SQL>del "Target (SQL Scripts)\*.sql"

C:\Users\USER\Google Drive\SW_PLATFORM\15. AI\MY_LATEST_FILES\EXODUS\XML to SQL>venv\Scripts\python -m xml_to_sql.cli convert --config config.yaml
[plan] C:\Users\USER\Google Drive\SW_PLATFORM\15. AI\MY_LATEST_FILES\EXODUS\XML to SQL\Source (XML Files)\Sold_Materials.XML -> C:\Users\USER\Google Drive\SW_PLATFORM\15. AI\MY_LATEST_FILES\EXODUS\XML to SQL\Target (SQL Scripts)\V_C_SOLD_MATERIALS.sql
  Scenario ID: Sold_Materials
  Nodes parsed: 2
  Filters detected: 1
  Calculated columns: 0
  Logical model: present
  Planned SQL target: C:\Users\USER\Google Drive\SW_PLATFORM\15. AI\MY_LATEST_FILES\EXODUS\XML to SQL\Target (SQL Scripts)\V_C_SOLD_MATERIALS.sql
  ✓ SQL generated: C:\Users\USER\Google Drive\SW_PLATFORM\15. AI\MY_LATEST_FILES\EXODUS\XML to SQL\Target (SQL Scripts)\V_C_SOLD_MATERIALS.sql
[plan] C:\Users\USER\Google Drive\SW_PLATFORM\15. AI\MY_LATEST_FILES\EXODUS\XML to SQL\Source (XML Files)\SALES_BOM.XML -> C:\Users\USER\Google Drive\SW_PLATFORM\15. AI\MY_LATEST_FILES\EXODUS\XML to SQL\Target (SQL Scripts)\V_C_SALES_BOM.sql
  Scenario ID: SALES_BOM
  Nodes parsed: 10
  Filters detected: 5
  Calculated columns: 0
  Logical model: present
  Planned SQL target: C:\Users\USER\Google Drive\SW_PLATFORM\15. AI\MY_LATEST_FILES\EXODUS\XML to SQL\Target (SQL Scripts)\V_C_SALES_BOM.sql
  ✓ SQL generated: C:\Users\USER\Google Drive\SW_PLATFORM\15. AI\MY_LATEST_FILES\EXODUS\XML to SQL\Target (SQL Scripts)\V_C_SALES_BOM.sql
[plan] C:\Users\USER\Google Drive\SW_PLATFORM\15. AI\MY_LATEST_FILES\EXODUS\XML to SQL\Source (XML Files)\Recently_created_products.XML -> C:\Users\USER\Google Drive\SW_PLATFORM\15. AI\MY_LATEST_FILES\EXODUS\XML to SQL\Target (SQL Scripts)\V_C_RECENTLY_CREATED_PRODUCTS.sql
  Scenario ID: Recently_created_products
  Nodes parsed: 10
  Filters detected: 1
  Calculated columns: 0
  Logical model: present
  Planned SQL target: C:\Users\USER\Google Drive\SW_PLATFORM\15. AI\MY_LATEST_FILES\EXODUS\XML to SQL\Target (SQL Scripts)\V_C_RECENTLY_CREATED_PRODUCTS.sql
  ✓ SQL generated: C:\Users\USER\Google Drive\SW_PLATFORM\15. AI\MY_LATEST_FILES\EXODUS\XML to SQL\Target (SQL Scripts)\V_C_RECENTLY_CREATED_PRODUCTS.sql
[plan] C:\Users\USER\Google Drive\SW_PLATFORM\15. AI\MY_LATEST_FILES\EXODUS\XML to SQL\Source (XML Files)\Material Details.XML -> C:\Users\USER\Google Drive\SW_PLATFORM\15. AI\MY_LATEST_FILES\EXODUS\XML to SQL\Target (SQL Scripts)\V_C_MATERIAL_DETAILS.sql
  Scenario ID: MATERIAL_DETAILS
  Nodes parsed: 0
  Filters detected: 0
  Calculated columns: 0
  Logical model: present
  Planned SQL target: C:\Users\USER\Google Drive\SW_PLATFORM\15. AI\MY_LATEST_FILES\EXODUS\XML to SQL\Target (SQL Scripts)\V_C_MATERIAL_DETAILS.sql
  ✓ SQL generated: C:\Users\USER\Google Drive\SW_PLATFORM\15. AI\MY_LATEST_FILES\EXODUS\XML to SQL\Target (SQL Scripts)\V_C_MATERIAL_DETAILS.sql
[plan] C:\Users\USER\Google Drive\SW_PLATFORM\15. AI\MY_LATEST_FILES\EXODUS\XML to SQL\Source (XML Files)\KMDM_Materials.XML -> C:\Users\USER\Google Drive\SW_PLATFORM\15. AI\MY_LATEST_FILES\EXODUS\XML to SQL\Target (SQL Scripts)\V_C_KMDM_MATERIALS.sql
  Scenario ID: KMDM_Materials
  Nodes parsed: 11
  Filters detected: 1
  Calculated columns: 0
  Logical model: present
  Planned SQL target: C:\Users\USER\Google Drive\SW_PLATFORM\15. AI\MY_LATEST_FILES\EXODUS\XML to SQL\Target (SQL Scripts)\V_C_KMDM_MATERIALS.sql
  ✓ SQL generated: C:\Users\USER\Google Drive\SW_PLATFORM\15. AI\MY_LATEST_FILES\EXODUS\XML to SQL\Target (SQL Scripts)\V_C_KMDM_MATERIALS.sql
[plan] C:\Users\USER\Google Drive\SW_PLATFORM\15. AI\MY_LATEST_FILES\EXODUS\XML to SQL\Source (XML Files)\CURRENT_MAT_SORT.XML -> C:\Users\USER\Google Drive\SW_PLATFORM\15. AI\MY_LATEST_FILES\EXODUS\XML to SQL\Target (SQL Scripts)\V_C_CURRENT_MAT_SORT.sql
  Scenario ID: CURRENT_MAT_SORT
  Nodes parsed: 4
  Filters detected: 2
  Calculated columns: 0
  Logical model: present
  Planned SQL target: C:\Users\USER\Google Drive\SW_PLATFORM\15. AI\MY_LATEST_FILES\EXODUS\XML to SQL\Target (SQL Scripts)\V_C_CURRENT_MAT_SORT.sql
  ✓ SQL generated: C:\Users\USER\Google Drive\SW_PLATFORM\15. AI\MY_LATEST_FILES\EXODUS\XML to SQL\Target (SQL Scripts)\V_C_CURRENT_MAT_SORT.sql
[plan] C:\Users\USER\Google Drive\SW_PLATFORM\15. AI\MY_LATEST_FILES\EXODUS\XML to SQL\Source (XML Files)\Sold_Materials_PROD.XML -> C:\Users\USER\Google Drive\SW_PLATFORM\15. AI\MY_LATEST_FILES\EXODUS\XML to SQL\Target (SQL Scripts)\V_C_SOLD_MATERIALS_PROD.sql
  Scenario ID: Sold_Materials_PROD
  Nodes parsed: 6
  Filters detected: 1
  Calculated columns: 0
  Logical model: present
  Planned SQL target: C:\Users\USER\Google Drive\SW_PLATFORM\15. AI\MY_LATEST_FILES\EXODUS\XML to SQL\Target (SQL Scripts)\V_C_SOLD_MATERIALS_PROD.sql
  ✓ SQL generated: C:\Users\USER\Google Drive\SW_PLATFORM\15. AI\MY_LATEST_FILES\EXODUS\XML to SQL\Target (SQL Scripts)\V_C_SOLD_MATERIALS_PROD.sql

C:\Users\USER\Google Drive\SW_PLATFORM\15. AI\MY_LATEST_FILES\EXODUS\XML to SQL>^A^A