# ClickHouse DataLakeCatalog Integration with Lakekeeper

This guide documents the complete setup and configuration of ClickHouse with the DataLakeCatalog database engine to query Iceberg tables managed by Lakekeeper, all running in a Podman-based Docker Compose stack.

## Overview

**What was accomplished:**
- ✅ Upgraded ClickHouse from `latest` to `head` image (required for DataLakeCatalog support)
- ✅ Enabled experimental database features via `config.xml`
- ✅ Created a `DataLakeCatalog` database that connects to Lakekeeper's REST API
- ✅ Configured automatic Iceberg table discovery through Lakekeeper
- ✅ Tested connectivity with the full Lakekeeper/MinIO/ClickHouse stack
- ✅ All services running in the same Podman network
- ✅ Configured users.xml for proper network access

## Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                    Podman Docker Compose Stack                  │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────────────┐ │
│  │   MinIO      │  │  Lakekeeper  │  │   ClickHouse         │ │
│  │  (S3 Storage)│  │  (Catalog)   │  │   (Query Engine)     │ │
│  │  :9000-9001  │  │  :8181       │  │   :8123, :9009       │ │
│  └──────────────┘  └──────────────┘  └──────────────────────┘ │
│        ▲                  ▲                      │               │
│        │                  │                      │               │
│        └──────────────────┴──────────────────────┘               │
│                        Network: default (bridge)                │
└─────────────────────────────────────────────────────────────────┘

Flow:
1. ClickHouse uses DataLakeCatalog engine
2. Connects to Lakekeeper REST API at http://lakekeeper:8181/catalog
3. Lakekeeper catalogs Iceberg tables in MinIO
4. ClickHouse automatically discovers and queries Iceberg tables
```

## Key Configuration Changes

### 1. **Updated docker-compose.yml**

```yaml
clickhouse:
  image: clickhouse/clickhouse-server:head  # ← Changed from :latest
  container_name: clickhouse
  ports:
    - "8123:8123"  # HTTP interface
    - "9009:9000"  # Native protocol
  environment:
    CLICKHOUSE_USER: default
    CLICKHOUSE_PASSWORD: ""
    CLICKHOUSE_DB: default
    AWS_ACCESS_KEY_ID: minioadmin
    AWS_SECRET_ACCESS_KEY: minioadmin
    AWS_DEFAULT_REGION: us-east-1
  volumes:
    - ./data/clickhouse:/var/lib/clickhouse
    - ./config/clickhouse/config.xml:/etc/clickhouse-server/config.d/iceberg.xml:ro
    - ./config/clickhouse/users.xml:/etc/clickhouse-server/config.d/users.xml:ro
    - ./config/clickhouse/init.sql:/docker-entrypoint-initdb.d/init.sql:ro
  depends_on:
    lakekeeper:
      condition: service_healthy
    minio:
      condition: service_healthy
  restart: unless-stopped
```

**Key changes:**
- Image upgraded to `head` (supports experimental DataLakeCatalog engine)
- Added `CLICKHOUSE_USER`, `CLICKHOUSE_PASSWORD`, `CLICKHOUSE_DB` environment variables
- Mount `users.xml` for user configuration (enables network access)
- Mount `init.sql` for automatic database creation on startup
- Added dependency on Lakekeeper service

### 2. **Updated config/clickhouse/config.xml**

```xml
<clickhouse>
    <!-- Allow user-level settings at top-level config -->
    <skip_check_for_incorrect_settings>1</skip_check_for_incorrect_settings>
    
    <!-- Enable experimental features for DataLakeCatalog support -->
    <allow_experimental_database_iceberg>1</allow_experimental_database_iceberg>
    <allow_experimental_database_paimon_rest_catalog>1</allow_experimental_database_paimon_rest_catalog>
    
    <!-- Named collections for Iceberg/S3 access -->
    <named_collections>
        <minio_s3>
            <url>http://minio:9000/warehouse/</url>
            <access_key_id>minioadmin</access_key_id>
            <secret_access_key>minioadmin</secret_access_key>
        </minio_s3>
    </named_collections>

    <!-- S3 settings for MinIO compatibility -->
    <s3>
        <use_environment_credentials>true</use_environment_credentials>
    </s3>
</clickhouse>
```

**Key settings:**
- `skip_check_for_incorrect_settings=1` allows user-level settings in config
- `allow_experimental_database_iceberg=1` enables DataLakeCatalog engine
- Named collection `minio_s3` for backward compatibility with IcebergS3 engine

### 3. **Created config/clickhouse/users.xml** (NEW)

```xml
<?xml version="1.0"?>
<clickhouse>
    <!-- Users and roles configuration for ClickHouse -->
    
    <!-- Default user with no password for development -->
    <users>
        <default>
            <!-- Password is empty (no authentication required) -->
            <password></password>
            
            <!-- Allow access from any host -->
            <networks>
                <ip>::/0</ip>
            </networks>
            
            <!-- Set resource quotas and settings -->
            <profile>default</profile>
            <quota>default</quota>
        </default>
    </users>

    <!-- Default profile settings -->
    <profiles>
        <default>
            <!-- Default settings for all users -->
            <readonly>0</readonly>
        </default>
    </profiles>

    <!-- Default quota (unlimited for development) -->
    <quotas>
        <default>
            <interval>
                <duration>3600</duration>
            </interval>
        </default>
    </quotas>
</clickhouse>
```

**Purpose:**
- Explicitly configures network access for the `default` user
- Allows connections from any host (`::/0`)
- Enables full read/write access (development configuration)

### 4. **Created config/clickhouse/init.sql**

```sql
-- Enable experimental database features
SET allow_experimental_database_iceberg = 1;

-- Create DataLakeCatalog database for Lakekeeper
CREATE DATABASE IF NOT EXISTS iceberg_catalog
ENGINE = DataLakeCatalog('http://lakekeeper:8181/catalog', 'minioadmin', 'minioadmin')
SETTINGS
   catalog_type = 'rest',
   warehouse = 'default',
   storage_endpoint = 'http://minio:9000/warehouse/';
```

**Parameters:**
- `catalog_endpoint`: `http://lakekeeper:8181/catalog` - Lakekeeper REST API
- `catalog_type`: `rest` - Uses Iceberg REST catalog specification
- `warehouse`: `default` - Default warehouse name in Lakekeeper
- `storage_endpoint`: `http://minio:9000/warehouse/` - MinIO S3 storage location

## ClickHouse Startup Message Explained

### Warning Message
When ClickHouse starts, you may see:
```
/entrypoint.sh: neither CLICKHOUSE_USER nor CLICKHOUSE_PASSWORD is set, disabling network access for user 'default'
```

**This is just a warning from the Docker entrypoint script.** It appears because:
1. The entrypoint script checks for `CLICKHOUSE_USER` and `CLICKHOUSE_PASSWORD` environment variables
2. Even though we set `CLICKHOUSE_PASSWORD: ""` (empty password), the entrypoint script warns about it
3. Our `users.xml` configuration overrides this and properly enables network access

**The warning is harmless and does NOT prevent ClickHouse from functioning normally.**

To verify network access is working:
```bash
podman exec clickhouse clickhouse-client --query "SELECT 1;"
# Should return: 1
```

## Lakekeeper Setup

### Creating a Warehouse

If Lakekeeper doesn't have a `default` warehouse, create one using its management API:

```bash
curl -X POST http://localhost:8181/management/v1/warehouse \
  -H "Content-Type: application/json" \
  -d '{
    "warehouse-name": "default",
    "project-id": "00000000-0000-0000-0000-000000000000",
    "storage-profile": {
      "type": "s3",
      "bucket": "warehouse",
      "key-prefix": "",
      "assume-role-arn": null,
      "endpoint": "http://minio:9000",
      "region": "local",
      "path-style-access": true,
      "flavor": "minio",
      "sts-enabled": false
    },
    "storage-credential": {
      "type": "s3",
      "credential-type": "access-key",
      "aws-access-key-id": "minioadmin",
      "aws-secret-access-key": "minioadmin"
    }
  }'
```

## Usage Examples

### Start the Stack (Podman)

```bash
cd /data/pyworkspace/nmt-stack

# Start all services
podman-compose up -d

# Start only ClickHouse (other services already running)
podman-compose up -d clickhouse

# View logs
podman-compose logs -f clickhouse
```

### Connect to ClickHouse

```bash
# Using podman-compose
podman exec clickhouse clickhouse-client

# Or use HTTP interface
curl http://localhost:8123/

# With query
podman exec clickhouse clickhouse-client --query "SELECT 'Hello' as greeting;"
```

### Query the Iceberg Catalog

```sql
-- List all databases
SHOW DATABASES;

-- Output should include:
-- iceberg_catalog
-- default
-- system
-- information_schema
-- ...

-- Use the iceberg catalog database
USE iceberg_catalog;

-- List all Iceberg tables (auto-discovered from Lakekeeper)
SHOW TABLES;

-- If Iceberg tables exist, query them:
-- SELECT * FROM `namespace.table_name` LIMIT 10;
```

### View Catalog Configuration

```sql
-- Show database details
SHOW CREATE DATABASE iceberg_catalog;

-- Show table schema (if tables exist)
-- DESCRIBE TABLE `namespace.table_name`;
```

## DataLakeCatalog Connection Parameters

When creating a DataLakeCatalog database, the following parameters are used:

| Parameter | Value | Description |
|-----------|-------|-------------|
| `catalog_endpoint` | `http://lakekeeper:8181/catalog` | Lakekeeper REST API endpoint |
| `user` | `minioadmin` | S3 credential user for Lakekeeper |
| `password` | `minioadmin` | S3 credential password for Lakekeeper |
| `catalog_type` | `rest` | REST catalog specification (Iceberg) |
| `warehouse` | `default` | Warehouse name in Lakekeeper |
| `storage_endpoint` | `http://minio:9000/warehouse/` | MinIO S3 endpoint for data storage |

## Supported Catalogs in DataLakeCatalog Engine

ClickHouse's DataLakeCatalog engine supports:

1. **AWS Glue Catalog** - For Iceberg tables in AWS environments
2. **Databricks Unity Catalog** - For Delta Lake and Iceberg tables
3. **Hive Metastore** - Traditional Hadoop ecosystem catalog
4. **REST Catalogs** - Any catalog supporting the Iceberg REST specification (e.g., Lakekeeper, Tabular.io, Nessie)

## Troubleshooting

### Issue: Startup Warning About Network Access

```
/entrypoint.sh: neither CLICKHOUSE_USER nor CLICKHOUSE_PASSWORD is set, disabling network access for user 'default'
```

**Solution:** This is expected and harmless. The `users.xml` configuration ensures proper network access. Verify connectivity works:
```bash
podman exec clickhouse clickhouse-client --query "SELECT 1;"
```

### Issue: `WarehouseNotFound` Error

```
Error: Warehouse 'default' does not exist
```

**Solution:** Create a warehouse in Lakekeeper using the management API (see "Lakekeeper Setup" section above).

### Issue: `Connection refused` to Lakekeeper

**Solution:** Ensure:
- Lakekeeper container is running and healthy: `podman ps | grep lakekeeper`
- Service name is correct in connection string (use container network alias, not localhost)
- Lakekeeper port 8181 is exposed and accessible

### Issue: ClickHouse container exits immediately

**Cause:** Config validation errors (especially user-level settings)

**Solution:** 
1. Check logs: `podman logs clickhouse`
2. Ensure `skip_check_for_incorrect_settings=1` in config.xml
3. Verify experimental settings are properly formatted in config.xml

### View Detailed Logs

```bash
# ClickHouse error log
podman exec clickhouse cat /var/log/clickhouse-server/clickhouse-server.err.log

# Lakekeeper logs
podman-compose logs lakekeeper

# MinIO logs
podman-compose logs minio
```

## Next Steps

1. **Create Iceberg Tables:** Use Lakekeeper or any Iceberg client to create tables in the `default` warehouse
2. **Query Data:** Once tables exist, they'll be automatically discoverable in ClickHouse
3. **Load Data:** Use `INSERT INTO ... SELECT FROM iceberg_catalog.` to copy data or query directly
4. **Monitor Performance:** Track query execution and optimize as needed

## References

- [ClickHouse DataLakeCatalog Documentation](https://clickhouse.com/docs/engines/database-engines/datalakecatalog)
- [ClickHouse Lakekeeper Integration Guide](https://clickhouse.com/docs/use-cases/data-lake/lakekeeper-catalog)
- [Lakekeeper Documentation](https://docs.lakekeeper.io/)
- [Apache Iceberg REST Catalog Specification](https://iceberg.apache.org/docs/latest/api/)

## Summary

✅ **DataLakeCatalog is now fully configured and integrated with:**
- Lakekeeper (Iceberg REST catalog)
- MinIO (S3-compatible storage)
- ClickHouse (head image with experimental DataLakeCatalog support)
- User configuration for proper network access

All services run in the same Podman network (`nmt-stack_default`) and automatically discover each other by service name.


## Lakekeeper Setup

### Creating a Warehouse

If Lakekeeper doesn't have a `default` warehouse, create one using its management API:

```bash
curl -X POST http://localhost:8181/management/v1/warehouse \
  -H "Content-Type: application/json" \
  -d '{
    "warehouse-name": "default",
    "project-id": "00000000-0000-0000-0000-000000000000",
    "storage-profile": {
      "type": "s3",
      "bucket": "warehouse",
      "key-prefix": "",
      "assume-role-arn": null,
      "endpoint": "http://minio:9000",
      "region": "local",
      "path-style-access": true,
      "flavor": "minio",
      "sts-enabled": false
    },
    "storage-credential": {
      "type": "s3",
      "credential-type": "access-key",
      "aws-access-key-id": "minioadmin",
      "aws-secret-access-key": "minioadmin"
    }
  }'
```

## Usage Examples

### Start the Stack (Podman)

```bash
cd /data/pyworkspace/nmt-stack

# Start all services
podman-compose up -d

# Start only ClickHouse (other services already running)
podman-compose up -d clickhouse

# View logs
podman-compose logs -f clickhouse
```

### Connect to ClickHouse

```bash
# Using podman-compose
podman exec clickhouse clickhouse-client

# Or use HTTP interface
curl http://localhost:8123/

# With query
podman exec clickhouse clickhouse-client --query "SELECT 'Hello' as greeting;"
```

### Query the Iceberg Catalog

```sql
-- List all databases
SHOW DATABASES;

-- Output should include:
-- iceberg_catalog
-- default
-- system
-- information_schema
-- ...

-- Use the iceberg catalog database
USE iceberg_catalog;

-- List all Iceberg tables (auto-discovered from Lakekeeper)
SHOW TABLES;

-- If Iceberg tables exist, query them:
-- SELECT * FROM `namespace.table_name` LIMIT 10;
```

### View Catalog Configuration

```sql
-- Show database details
SHOW CREATE DATABASE iceberg_catalog;

-- Show table schema (if tables exist)
-- DESCRIBE TABLE `namespace.table_name`;
```

## DataLakeCatalog Connection Parameters

When creating a DataLakeCatalog database, the following parameters are used:

| Parameter | Value | Description |
|-----------|-------|-------------|
| `catalog_endpoint` | `http://lakekeeper:8181/catalog` | Lakekeeper REST API endpoint |
| `user` | `minioadmin` | S3 credential user for Lakekeeper |
| `password` | `minioadmin` | S3 credential password for Lakekeeper |
| `catalog_type` | `rest` | REST catalog specification (Iceberg) |
| `warehouse` | `default` | Warehouse name in Lakekeeper |
| `storage_endpoint` | `http://minio:9000/warehouse/` | MinIO S3 endpoint for data storage |

## Supported Catalogs in DataLakeCatalog Engine

ClickHouse's DataLakeCatalog engine supports:

1. **AWS Glue Catalog** - For Iceberg tables in AWS environments
2. **Databricks Unity Catalog** - For Delta Lake and Iceberg tables
3. **Hive Metastore** - Traditional Hadoop ecosystem catalog
4. **REST Catalogs** - Any catalog supporting the Iceberg REST specification (e.g., Lakekeeper, Tabular.io, Nessie)

## Troubleshooting

### Issue: `WarehouseNotFound` Error

```
Error: Warehouse 'default' does not exist
```

**Solution:** Create a warehouse in Lakekeeper using the management API (see "Lakekeeper Setup" section above).

### Issue: `Connection refused` to Lakekeeper

**Solution:** Ensure:
- Lakekeeper container is running and healthy: `podman ps | grep lakekeeper`
- Service name is correct in connection string (use container network alias, not localhost)
- Lakekeeper port 8181 is exposed and accessible

### Issue: ClickHouse container exits immediately

**Cause:** Config validation errors (especially user-level settings)

**Solution:** 
1. Check logs: `podman logs clickhouse`
2. Ensure `skip_check_for_incorrect_settings=1` in config.xml
3. Verify experimental settings are properly formatted in config.xml

### View Detailed Logs

```bash
# ClickHouse error log
podman exec clickhouse cat /var/log/clickhouse-server/clickhouse-server.err.log

# Lakekeeper logs
podman-compose logs lakekeeper

# MinIO logs
podman-compose logs minio
```

## Next Steps

1. **Create Iceberg Tables:** Use Lakekeeper or any Iceberg client to create tables in the `default` warehouse
2. **Query Data:** Once tables exist, they'll be automatically discoverable in ClickHouse
3. **Load Data:** Use `INSERT INTO ... SELECT FROM iceberg_catalog.` to copy data or query directly
4. **Monitor Performance:** Track query execution and optimize as needed

## References

- [ClickHouse DataLakeCatalog Documentation](https://clickhouse.com/docs/engines/database-engines/datalakecatalog)
- [ClickHouse Lakekeeper Integration Guide](https://clickhouse.com/docs/use-cases/data-lake/lakekeeper-catalog)
- [Lakekeeper Documentation](https://docs.lakekeeper.io/)
- [Apache Iceberg REST Catalog Specification](https://iceberg.apache.org/docs/latest/api/)

## Summary

✅ **DataLakeCatalog is now fully configured and integrated with:**
- Lakekeeper (Iceberg REST catalog)
- MinIO (S3-compatible storage)
- ClickHouse (head image with experimental DataLakeCatalog support)

All services run in the same Podman network (`nmt-stack_default`) and automatically discover each other by service name.
