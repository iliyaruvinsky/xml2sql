# Deployment Quick Reference

> **One-page summary for experienced users**

## Quick Steps

1. **Open SQL file** from `Target (SQL Scripts)/` or `DEPLOYMENT_SCRIPTS/`
2. **Wrap in CREATE VIEW:**
   ```sql
   CREATE OR REPLACE VIEW YOUR_SCHEMA.V_C_<NAME> AS
   <PASTE_SQL_CONTENT>
   ```
3. **Execute in Snowflake**
4. **Verify:** `SHOW VIEWS LIKE 'V_C_<NAME>' IN SCHEMA YOUR_SCHEMA;`

## View Names

| SQL File | View Name |
|----------|-----------|
| V_C_SOLD_MATERIALS.sql | V_C_SOLD_MATERIALS |
| V_C_SALES_BOM.sql | V_C_SALES_BOM |
| V_C_RECENTLY_CREATED_PRODUCTS.sql | V_C_RECENTLY_CREATED_PRODUCTS |
| V_C_KMDM_MATERIALS.sql | V_C_KMDM_MATERIALS |
| V_C_CURRENT_MAT_SORT.sql | V_C_CURRENT_MAT_SORT |
| V_C_MATERIAL_DETAILS.sql | V_C_MATERIAL_DETAILS |
| V_C_SOLD_MATERIALS_PROD.sql | V_C_SOLD_MATERIALS_PROD |

## Common Commands

**Check if view exists:**
```sql
SHOW VIEWS LIKE 'V_C_SOLD_MATERIALS' IN SCHEMA YOUR_SCHEMA;
```

**Test view:**
```sql
SELECT * FROM YOUR_SCHEMA.V_C_SOLD_MATERIALS LIMIT 10;
```

**View definition:**
```sql
SELECT GET_DDL('VIEW', 'YOUR_SCHEMA.V_C_SOLD_MATERIALS');
```

## Troubleshooting

- **"Object does not exist"** → Check source tables exist
- **"Insufficient privileges"** → Need CREATE VIEW permission
- **"SQL compilation error"** → Check schema/table names (case-sensitive!)

## Full Guide

For detailed instructions, see [CLIENT_DEPLOYMENT_GUIDE.md](CLIENT_DEPLOYMENT_GUIDE.md)

