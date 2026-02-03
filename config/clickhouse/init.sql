-- ClickHouse initialization script for DataLakeCatalog setup
-- This script configures ClickHouse to connect to Lakekeeper catalog

-- Enable experimental database features for DataLakeCatalog support
SET allow_experimental_database_iceberg = 1;

-- Create DataLakeCatalog database for Lakekeeper
-- The catalog_endpoint should be the Lakekeeper REST API endpoint
-- warehouse = the default warehouse name in Lakekeeper
-- storage_endpoint = the MinIO S3 endpoint where data is stored
CREATE DATABASE IF NOT EXISTS iceberg_catalog_lk ENGINE = DataLakeCatalog('http://lakekeeper:8181/catalog') SETTINGS catalog_type = 'rest', warehouse = 'warehouse', storage_endpoint = 'http://minio:9000/warehouse/', aws_access_key_id = 'minioadmin',   aws_secret_access_key = 'minioadmin';

-- Display status
SHOW DATABASES;

-- Example query (if tables exist in Lakekeeper):
-- USE iceberg_catalog;
-- SHOW TABLES;
