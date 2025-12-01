"""
ABAP Generator Module

Converts generated HANA SQL to ABAP Report programs for data extraction.
The generated ABAP program:
- Creates a temporary view using the SQL
- Fetches data using native SQL cursor
- Exports to CSV (GUI download or Application Server)
"""

from .generator import generate_abap_report, extract_columns_from_sql

__all__ = ["generate_abap_report", "extract_columns_from_sql"]
