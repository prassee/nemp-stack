-- ClickHouse initialization script for local connections
-- This script configures ClickHouse to connect to the DataLakeCatalog using localhost.
-- Run this from your local SQL client (like DBeaver) after the Docker stack is running.

-- Enable experimental database features for DataLakeCatalog support
SET allow_experimental_database_iceberg = 1;

-- Create DataLakeCatalog database for connections from local clients
-- This uses 'localhost' because your client is running on the same machine as the Docker host.
CREATE DATABASE IF NOT EXISTS iceberg_catalog_local
ENGINE = DataLakeCatalog('http://localhost:8181/catalog')
SETTINGS
    catalog_type = 'rest',
    warehouse = 'warehouse',
    storage_endpoint = 'http://localhost:9000/warehouse/',
    aws_access_key_id = 'minioadmin',
    aws_secret_access_key = 'minioadmin';

-- Display status
SHOW DATABASES;
