# Deployment Scripts

This directory contains ready-to-use SQL scripts for creating Snowflake views from the generated SQL files.

## What's in This Directory

Each script is a complete `CREATE VIEW` statement that you can execute directly in Snowflake. The scripts are numbered in the recommended deployment order.

## Files

1. **01_V_C_SOLD_MATERIALS.sql** - Sold materials view
2. **02_V_C_SALES_BOM.sql** - Sales bill of materials view
3. **03_V_C_RECENTLY_CREATED_PRODUCTS.sql** - Recently created products view
4. **04_V_C_KMDM_MATERIALS.sql** - KMDM materials view
5. **05_V_C_CURRENT_MAT_SORT.sql** - Current material sort view
6. **06_V_C_MATERIAL_DETAILS.sql** - Material details view
7. **07_V_C_SOLD_MATERIALS_PROD.sql** - Sold materials production view

## How to Use

### Step 1: Replace Schema Name

Before executing, replace `<YOUR_SCHEMA>` with your actual Snowflake schema name in each script.

**Example:**
```sql
-- Change this:
CREATE OR REPLACE VIEW <YOUR_SCHEMA>.V_C_SOLD_MATERIALS AS

-- To this (if your schema is PROD_SCHEMA):
CREATE OR REPLACE VIEW PROD_SCHEMA.V_C_SOLD_MATERIALS AS
```

### Step 2: Execute in Snowflake

1. Open Snowflake Web UI or your SQL client
2. Select the correct database and schema
3. Copy the entire script
4. Paste into the SQL editor
5. Execute (Run button or Ctrl+Enter)

### Step 3: Verify

After executing each script, verify the view was created:

```sql
SHOW VIEWS LIKE 'V_C_SOLD_MATERIALS' IN SCHEMA YOUR_SCHEMA;
```

## Alternative: Use the Deployment Guide

For detailed step-by-step instructions, see the [CLIENT_DEPLOYMENT_GUIDE.md](../CLIENT_DEPLOYMENT_GUIDE.md) in the repository root.

## Notes

- Scripts are numbered in recommended deployment order
- Some scripts contain warnings about joins without conditions - this is intentional
- All scripts use `CREATE OR REPLACE VIEW` so you can re-run them safely
- Make sure source tables exist in Snowflake before creating views

## Troubleshooting

If you encounter errors:

1. Verify source tables exist: `SHOW TABLES IN SCHEMA SAPK5D;`
2. Check schema name spelling (case-sensitive in Snowflake)
3. Verify you have CREATE VIEW permissions
4. See [CLIENT_DEPLOYMENT_GUIDE.md](../CLIENT_DEPLOYMENT_GUIDE.md) troubleshooting section

