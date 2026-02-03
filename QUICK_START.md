# ClickHouse DataLakeCatalog - Quick Start Guide

## After Running `ch` (ClickHouse Shell)

When you enter the ClickHouse shell with the `ch` command, you'll have access to the DataLakeCatalog. Here's what you should see and do:

### 1. Check Available Databases

```sql
:) SHOW DATABASES;

┌─name───────────────┐
│ INFORMATION_SCHEMA │
│ default            │
│ iceberg_catalog    │  ← This is the NEW DataLakeCatalog database
│ information_schema │
│ system             │
└────────────────────┘

5 rows in set. Elapsed: 0.005 sec.
```

### 2. Switch to the Iceberg Catalog

```sql
:) USE iceberg_catalog;

Ok.

0 rows in set. Elapsed: 0.000 sec.
```

### 3. Show Tables (Currently Empty - No Data Created Yet)

```sql
:) SHOW TABLES;

┌─name─┐
│      │  (empty - waiting for Iceberg tables to be created)
└──────┘

0 rows in set. Elapsed: 0.003 sec.
```

### 4. Query Table Information

```sql
:) SELECT * FROM system.tables WHERE database = 'iceberg_catalog';

(will show metadata about tables once they're created)
```

## How to Create Iceberg Tables

Once you create Iceberg tables using Spark, Flink, DuckDB, or PyIceberg, they will automatically appear in the `iceberg_catalog` database.

### Example: Create a Table Using Spark

```python
# In Spark with Iceberg support
spark.sql("""
    CREATE TABLE iceberg_catalog.my_namespace.my_table
    USING iceberg
    AS SELECT * FROM source_data
""")
```

### Then Query It in ClickHouse

```sql
:) USE iceberg_catalog;
:) SHOW TABLES;

(my_table should appear here)

:) SELECT * FROM `my_namespace.my_table` LIMIT 10;
```

## Important Notes

### Table Names Require Backticks

When querying tables with namespace prefixes, use backticks:

```sql
-- ✓ CORRECT
SELECT * FROM `namespace.table_name`;

-- ✗ WRONG
SELECT * FROM namespace.table_name;  -- This won't work!
```

### Where Data Is Stored

All Iceberg table data is stored in MinIO S3 storage:
- **MinIO Console**: http://localhost:9001 (user: minio / password: minioadmin)
- **Lakekeeper UI**: http://localhost:8181 (for browsing catalogs)

### Architecture Flow

```
ClickHouse (iceberg_catalog) 
    ↓ (REST API Query)
Lakekeeper (Iceberg Catalog)
    ↓ (Table Location)
MinIO S3 Storage (Iceberg Data Files)
```

## Common Commands

### List all namespaces and tables
```sql
SELECT database, name FROM system.tables 
WHERE database = 'iceberg_catalog';
```

### Get table schema
```sql
DESCRIBE TABLE `namespace.table_name`;
```

### Query with WHERE clause
```sql
SELECT * FROM `namespace.table_name` 
WHERE condition = true 
LIMIT 100;
```

### Join Iceberg tables
```sql
SELECT a.*, b.* 
FROM `namespace.table1` a
JOIN `namespace.table2` b ON a.id = b.id
LIMIT 10;
```

### Export to local ClickHouse table
```sql
CREATE TABLE local_table AS
SELECT * FROM `namespace.iceberg_table`;
```

## Troubleshooting in ClickHouse Shell

### Tables not appearing?

1. Check if Lakekeeper has tables:
```sql
:) SELECT * FROM system.tables WHERE database = 'iceberg_catalog';
```

2. Verify Lakekeeper connection:
```bash
# From outside ClickHouse:
curl http://localhost:8181/catalog/v1/config?warehouse=default
```

3. Check MinIO has data:
```bash
# Access MinIO console at http://localhost:9001
# User: minio / Password: minioadmin
```

### Getting "Cannot parse ..." error?

Make sure you're using backticks around table names with namespaces:
```sql
-- This will fail:
:) SELECT * FROM default.my_table;

-- Use this instead:
:) SELECT * FROM `default.my_table`;
```

## Exit ClickHouse Shell

```sql
:) EXIT
root@container:/#
```

Or use Ctrl+C

## Next Steps

1. ✓ You have iceberg_catalog database ready
2. → Create Iceberg tables using your preferred tool
3. → They'll auto-appear in iceberg_catalog
4. → Query them directly in ClickHouse!

---

**For more details, see**: DATALAKECATALOG_SETUP.md
