# Client Deployment Guide: HANA to Snowflake Views

> **For HANA Experts:** This guide will help you deploy your HANA calculation views as Snowflake views, even if you're new to Snowflake.

---

## Table of Contents

1. [Introduction](#introduction)
2. [Snowflake Basics for HANA Experts](#snowflake-basics-for-hana-experts)
3. [Pre-Deployment Checklist](#pre-deployment-checklist)
4. [Step-by-Step View Creation](#step-by-step-view-creation)
5. [Verification Steps](#verification-steps)
6. [Troubleshooting](#troubleshooting)
7. [Appendix](#appendix)

---

## Introduction

### Purpose

This guide helps you deploy the generated SQL scripts from your HANA calculation views into Snowflake as views. The SQL files have already been generated and are ready to use.

### Prerequisites

Before you begin, ensure you have:

- ✅ Access to your Snowflake account
- ✅ Permissions to create views in your target schema
- ✅ The generated SQL files (located in `Target (SQL Scripts)/` folder)
- ✅ Basic SQL knowledge (you're a HANA expert, so this should be easy!)

### What This Guide Covers

- Understanding Snowflake basics (if you're new to it)
- Creating views from the generated SQL scripts
- Verifying that the views work correctly
- Troubleshooting common issues

### Estimated Time

- **First-time deployment:** 30-45 minutes
- **Subsequent deployments:** 10-15 minutes per view

---

## Snowflake Basics for HANA Experts

### Key Differences: HANA vs Snowflake

If you're familiar with HANA, here's how Snowflake concepts map:

| HANA Concept | Snowflake Equivalent | Notes |
|--------------|---------------------|-------|
| Schema | Schema | Same concept |
| Calculation View | View | Similar, but Snowflake views are simpler |
| Analytic View | View | Snowflake uses views for most analytics |
| SQL | SQL | Very similar SQL syntax |
| Client | Not applicable | Snowflake doesn't use client separation like HANA |

### Snowflake Concepts You Need to Know

#### 1. Database → Schema → Object Hierarchy

```
Database
  └── Schema
      └── Views/Tables
```

**Example:**
```
SAP_PROD (Database)
  └── SAPK5D (Schema)
      └── V_C_SOLD_MATERIALS (View)
```

#### 2. Warehouse

- **What it is:** A compute resource that runs your queries
- **When you need it:** Snowflake automatically uses a warehouse when you run queries
- **You don't need to:** Manually start/stop warehouses for view creation

#### 3. Role and Permissions

- You need the `CREATE VIEW` permission in your target schema
- Your role determines what you can do
- If you can run queries, you likely have view creation permissions

### Access Methods

#### Option 1: Snowflake Web UI (Recommended for Beginners)

1. Log in to your Snowflake account
2. You'll see a web-based SQL editor
3. This is the easiest way to create views

#### Option 2: SQL Client (For Advanced Users)

- Use any SQL client that supports Snowflake (DBeaver, DataGrip, etc.)
- Connect using your Snowflake account credentials
- Run SQL commands directly

### Basic Navigation in Snowflake Web UI

When you log in to Snowflake Web UI:

1. **Left Panel:** Shows databases, schemas, and objects
2. **Top Panel:** SQL worksheet (where you write SQL)
3. **Bottom Panel:** Results area (shows query results)

**To create a view:**
1. Click on "Worksheets" (top menu)
2. Select or create a worksheet
3. Write your CREATE VIEW statement
4. Click "Run" (or press Ctrl+Enter)

---

## Pre-Deployment Checklist

Before you start creating views, verify the following:

### ✅ Checklist

- [ ] **Generated SQL files exist** - Check the `Target (SQL Scripts)/` folder
- [ ] **Snowflake access confirmed** - You can log in to Snowflake
- [ ] **Target schema identified** - Know where you want to create the views
- [ ] **Source tables verified** - The source tables/schemas (e.g., SAPK5D) exist in Snowflake
- [ ] **Permissions confirmed** - You have CREATE VIEW permission in target schema

### Generated SQL Files

You should have 7 SQL files ready:

1. `V_C_SOLD_MATERIALS.sql`
2. `V_C_SALES_BOM.sql`
3. `V_C_RECENTLY_CREATED_PRODUCTS.sql`
4. `V_C_KMDM_MATERIALS.sql`
5. `V_C_CURRENT_MAT_SORT.sql`
6. `V_C_MATERIAL_DETAILS.sql`
7. `V_C_SOLD_MATERIALS_PROD.sql`

**Location:** `Target (SQL Scripts)/` folder in this repository

### Verify Source Tables Exist

Before creating views, verify that your source tables exist in Snowflake. The SQL scripts reference schemas and tables like:

- `SAPK5D.MARA`
- `SAPK5D.VBAP`
- `SAPK5D.MAST`
- etc.

**To check:**
```sql
-- Run this in Snowflake to verify tables exist
SHOW TABLES IN SCHEMA SAPK5D;
```

If tables don't exist, you'll need to load them into Snowflake first (outside the scope of this guide).

---

## Step-by-Step View Creation

This section walks you through creating each view. Follow these steps for each SQL file.

### General Process

For each SQL file, you will:

1. Open the SQL file
2. Copy its contents
3. Wrap it in a CREATE VIEW statement
4. Execute it in Snowflake
5. Verify it was created

### View Naming Convention

The views follow this naming pattern: `V_C_<NAME>`

- **V_C** = View, Calculation (corporate naming standard)
- **NAME** = Descriptive name (e.g., SOLD_MATERIALS)

**Example:** `V_C_SOLD_MATERIALS` means "View, Calculation - Sold Materials"

### Step-by-Step Instructions

#### Step 1: Open the SQL File

**Option A: Use Ready-Made Scripts (Recommended - Faster!)**

1. Navigate to the `DEPLOYMENT_SCRIPTS/` folder
2. Open the numbered script (e.g., `01_V_C_SOLD_MATERIALS.sql`)
3. The script already has the CREATE VIEW wrapper - just replace `<YOUR_SCHEMA>` with your schema name
4. Copy the entire script (Ctrl+A, then Ctrl+C)
5. Skip to Step 3 (Execute in Snowflake)

**Option B: Use Raw SQL Files**

1. Navigate to the `Target (SQL Scripts)/` folder
2. Open the SQL file you want to deploy (e.g., `V_C_SOLD_MATERIALS.sql`)
3. Copy the entire contents (Ctrl+A, then Ctrl+C)
4. Continue to Step 2 to wrap it in CREATE VIEW

#### Step 2: Prepare the CREATE VIEW Statement

**If using DEPLOYMENT_SCRIPTS:** The scripts already have the CREATE VIEW wrapper - just replace `<YOUR_SCHEMA>` and you're ready!

**If using raw SQL files:** The SQL files contain SELECT statements. You need to wrap them in a CREATE VIEW statement.

**Template:**
```sql
CREATE OR REPLACE VIEW <SCHEMA>.<VIEW_NAME> AS
<PASTE_SQL_CONTENT_HERE>
```

**Example for V_C_SOLD_MATERIALS:**
```sql
CREATE OR REPLACE VIEW YOUR_SCHEMA.V_C_SOLD_MATERIALS AS
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
```

**Important Notes:**
- Replace `YOUR_SCHEMA` with your actual schema name
- The view name should match the file name (without .sql extension)
- Make sure there's a semicolon (;) at the end

#### Step 3: Execute in Snowflake

**Using Snowflake Web UI:**

1. Log in to Snowflake
2. Click "Worksheets" in the top menu
3. Select or create a new worksheet
4. Paste your CREATE VIEW statement
5. **Select the correct database and schema** using the dropdowns at the top
6. Click "Run" (or press Ctrl+Enter)

**What to Expect:**
- If successful: You'll see "View V_C_SOLD_MATERIALS successfully created" or similar
- If there's an error: You'll see an error message (see Troubleshooting section)

#### Step 4: Verify View Creation

**Check that the view exists:**
```sql
SHOW VIEWS LIKE 'V_C_SOLD_MATERIALS' IN SCHEMA YOUR_SCHEMA;
```

**Or check all views in your schema:**
```sql
SHOW VIEWS IN SCHEMA YOUR_SCHEMA;
```

You should see your view in the list.

### Creating All 7 Views

Repeat the above steps for each SQL file:

1. ✅ V_C_SOLD_MATERIALS.sql → CREATE VIEW V_C_SOLD_MATERIALS
2. ✅ V_C_SALES_BOM.sql → CREATE VIEW V_C_SALES_BOM
3. ✅ V_C_RECENTLY_CREATED_PRODUCTS.sql → CREATE VIEW V_C_RECENTLY_CREATED_PRODUCTS
4. ✅ V_C_KMDM_MATERIALS.sql → CREATE VIEW V_C_KMDM_MATERIALS
5. ✅ V_C_CURRENT_MAT_SORT.sql → CREATE VIEW V_C_CURRENT_MAT_SORT
6. ✅ V_C_MATERIAL_DETAILS.sql → CREATE VIEW V_C_MATERIAL_DETAILS
7. ✅ V_C_SOLD_MATERIALS_PROD.sql → CREATE VIEW V_C_SOLD_MATERIALS_PROD

**Tip:** Create them one at a time and verify each one before moving to the next.

---

## Verification Steps

After creating each view, verify that it works correctly.

### Step 1: Test the View with a Simple Query

Run this query for each view:

```sql
SELECT * FROM YOUR_SCHEMA.V_C_SOLD_MATERIALS LIMIT 10;
```

**What to Check:**
- ✅ Query executes without errors
- ✅ Returns data (or returns empty result if source is empty)
- ✅ Column names are correct
- ✅ Data types look correct

### Step 2: Check Row Counts (Optional)

If you have access to the HANA source, compare row counts:

**In Snowflake:**
```sql
SELECT COUNT(*) FROM YOUR_SCHEMA.V_C_SOLD_MATERIALS;
```

**In HANA:**
Run the equivalent query on your HANA calculation view.

**Note:** Row counts may differ due to:
- Different data refresh times
- Different filter criteria
- Data transformations

### Step 3: Validate Column Names

Check that the view has the expected columns:

```sql
DESCRIBE VIEW YOUR_SCHEMA.V_C_SOLD_MATERIALS;
```

Compare the column list with your HANA calculation view definition.

### Step 4: Check for Warnings

Some SQL files may contain warnings in comments. Check the SQL file for lines starting with `-- Warnings:`. These are informational and don't prevent the view from working, but you should be aware of them.

**Example warning:**
```sql
-- Warnings:
--   Join Join_1 has no join conditions
```

This means the join uses `ON 1=1` (cartesian product), which is intentional based on the HANA definition.

### Verification Checklist

For each view, verify:

- [ ] View created successfully
- [ ] SELECT query works
- [ ] Returns expected columns
- [ ] No unexpected errors
- [ ] Row count is reasonable (or matches HANA if comparing)

---

## Troubleshooting

### Common Errors and Solutions

#### Error: "Object does not exist or not authorized"

**Problem:** The source table or schema doesn't exist in Snowflake.

**Solution:**
1. Verify the source tables exist: `SHOW TABLES IN SCHEMA SAPK5D;`
2. Check schema name spelling (case-sensitive in Snowflake)
3. Verify you have SELECT permissions on source tables

#### Error: "Insufficient privileges to operate on schema"

**Problem:** You don't have CREATE VIEW permission.

**Solution:**
1. Contact your Snowflake administrator
2. Request CREATE VIEW permission on the target schema
3. Or use a different schema where you have permissions

#### Error: "SQL compilation error"

**Problem:** SQL syntax issue or object reference problem.

**Solution:**
1. Check that all referenced tables/schemas exist
2. Verify schema names are correct (case-sensitive!)
3. Check for typos in the SQL
4. Make sure the CREATE VIEW statement is properly formatted

#### Error: "Invalid identifier"

**Problem:** Column or object name issue.

**Solution:**
1. Check that column names match exactly (case-sensitive)
2. Verify table aliases are correct
3. Check for reserved word conflicts (unlikely but possible)

### Permission Issues

If you encounter permission errors:

1. **Check your role:**
   ```sql
   SHOW GRANTS TO ROLE YOUR_ROLE;
   ```

2. **Verify schema permissions:**
   ```sql
   SHOW GRANTS ON SCHEMA YOUR_SCHEMA;
   ```

3. **Contact administrator** if you need additional permissions

### Schema/Table Not Found Errors

**Verify tables exist:**
```sql
-- Check if schema exists
SHOW SCHEMAS LIKE 'SAPK5D';

-- Check if tables exist in schema
SHOW TABLES IN SCHEMA SAPK5D;

-- Check specific table
DESCRIBE TABLE SAPK5D.MARA;
```

**If tables don't exist:**
- You need to load the data into Snowflake first
- This is outside the scope of this guide
- Contact your data engineering team

### SQL Syntax Issues

**Common issues:**
- Missing semicolon at the end
- Incorrect CREATE VIEW syntax
- Mismatched parentheses or quotes

**Solution:**
- Copy the SQL exactly as provided
- Make sure the CREATE VIEW wrapper is correct
- Check for any accidental edits to the SQL

### Getting More Help

If you're still stuck:

1. **Check the error message carefully** - It usually tells you what's wrong
2. **Verify each step** - Go back and check the pre-deployment checklist
3. **Contact support** with:
   - The exact error message
   - Which SQL file you were working with
   - Your Snowflake database and schema names
   - Screenshot of the error (if possible)

---

## Appendix

### Quick Reference: SQL File to View Name Mapping

| SQL File | View Name | Description |
|----------|-----------|-------------|
| V_C_SOLD_MATERIALS.sql | V_C_SOLD_MATERIALS | Sold materials view |
| V_C_SALES_BOM.sql | V_C_SALES_BOM | Sales bill of materials |
| V_C_RECENTLY_CREATED_PRODUCTS.sql | V_C_RECENTLY_CREATED_PRODUCTS | Recently created products |
| V_C_KMDM_MATERIALS.sql | V_C_KMDM_MATERIALS | KMDM materials view |
| V_C_CURRENT_MAT_SORT.sql | V_C_CURRENT_MAT_SORT | Current material sort |
| V_C_MATERIAL_DETAILS.sql | V_C_MATERIAL_DETAILS | Material details |
| V_C_SOLD_MATERIALS_PROD.sql | V_C_SOLD_MATERIALS_PROD | Sold materials production |

### Naming Convention Explanation

**V_C_ Prefix:**
- **V** = View
- **C** = Calculation (indicating it's derived from a calculation view)
- **_** = Separator
- **NAME** = Descriptive name

This follows corporate naming standards for views derived from calculation views.

### CREATE VIEW Template

Use this template for each SQL file:

```sql
CREATE OR REPLACE VIEW <YOUR_SCHEMA>.<VIEW_NAME> AS
-- Paste SQL file contents here
;
```

**Example:**
```sql
CREATE OR REPLACE VIEW PROD_SCHEMA.V_C_SOLD_MATERIALS AS
WITH
  projection_1 AS (
    -- ... SQL content ...
  )
SELECT * FROM projection_1;
```

### Useful Snowflake Commands

**Check if view exists:**
```sql
SHOW VIEWS LIKE 'V_C_SOLD_MATERIALS' IN SCHEMA YOUR_SCHEMA;
```

**View view definition:**
```sql
SELECT GET_DDL('VIEW', 'YOUR_SCHEMA.V_C_SOLD_MATERIALS');
```

**Drop a view (if needed):**
```sql
DROP VIEW YOUR_SCHEMA.V_C_SOLD_MATERIALS;
```

**List all views in schema:**
```sql
SHOW VIEWS IN SCHEMA YOUR_SCHEMA;
```

### Contact Information for Support

If you need help:

1. **Check this guide first** - Most issues are covered here
2. **Review the troubleshooting section** - Common errors are documented
3. **Contact your project team** with:
   - Which document you were following
   - The step number
   - Exact error message
   - Your environment details

---

## Summary

You've learned how to:

1. ✅ Understand Snowflake basics
2. ✅ Create views from generated SQL scripts
3. ✅ Verify that views work correctly
4. ✅ Troubleshoot common issues

**Next Steps:**
- Create your first view using the step-by-step instructions
- Verify it works with a test query
- Repeat for all 7 views
- Compare results with HANA (if applicable)

**Good luck with your deployment! 🚀**

