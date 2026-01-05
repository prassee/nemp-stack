"""
Backfill module for exporting MySQL tables to Iceberg on MinIO.

Uses Polars for fast MySQL reads and PyIceberg for writing.

This module provides functions for backfilling data. CLI is in main.py.
"""

import logging
import os

import polars as pl
from pyiceberg.catalog import Catalog, load_catalog
from pyiceberg.table import Table

# Initialize logger for this module
logger = logging.getLogger(__name__)

# =============================================================================
# Configuration (from docker-compose.yml and setup_polaris.py)
# =============================================================================

# MySQL configuration
MYSQL_URI = os.getenv("MYSQL_URI", "mysql://root:mysql@localhost:3306/mixpanel")

# MinIO/S3 configuration
MINIO_ENDPOINT = os.getenv("MINIO_ENDPOINT", "http://localhost:9000")
MINIO_ACCESS_KEY = os.getenv("MINIO_ACCESS_KEY", "minioadmin")
MINIO_SECRET_KEY = os.getenv("MINIO_SECRET_KEY", "minioadmin")
MINIO_BUCKET = os.getenv("MINIO_BUCKET", "warehouse")

# Polaris catalog configuration
# Credentials from setup_polaris.py (client_id:client_secret format)
POLARIS_URI = os.getenv("POLARIS_URI", "http://localhost:8181/api/catalog")
POLARIS_CREDENTIAL = os.getenv(
    "POLARIS_CREDENTIAL", "c208b265597a57cc:b0d74647fdc58fa84c6ac099cd34260f"
)

# Default namespace for all tables
DEFAULT_NAMESPACE = "analytics"


def get_iceberg_catalog() -> Catalog:
    """Create PyIceberg catalog connected to Polaris."""
    logger.info("Connecting to Iceberg catalog via Polaris...")
    try:
        catalog: Catalog = load_catalog(
            "polaris",
            **{
                "type": "rest",
                "uri": POLARIS_URI,
                "credential": POLARIS_CREDENTIAL,
                "warehouse": "warehouse",
                "scope": "PRINCIPAL_ROLE:ALL",
                # S3/MinIO configuration
                "s3.endpoint": MINIO_ENDPOINT,
                "s3.access-key-id": MINIO_ACCESS_KEY,
                "s3.secret-access-key": MINIO_SECRET_KEY,
                "s3.path-style-access": "true",
                "s3.region": "us-east-1",
                # Use FsspecFileIO for S3 access
                "py-io-impl": "pyiceberg.io.fsspec.FsspecFileIO",
            },
        )
        logger.info("Successfully connected to Iceberg catalog")
        return catalog
    except Exception as e:
        logger.error(f"Failed to connect to Iceberg catalog: {e}")
        raise


def ensure_namespace(catalog: Catalog, namespace: str) -> None:
    """Create namespace if it doesn't exist."""
    logger.debug(f"Checking if namespace '{namespace}' exists...")
    try:
        namespaces = [ns[0] for ns in catalog.list_namespaces()]
        if namespace not in namespaces:
            catalog.create_namespace(namespace)
            logger.info(f"Created namespace: {namespace}")
        else:
            logger.debug(f"Namespace '{namespace}' already exists")
    except Exception as e:
        logger.error(f"Error ensuring namespace '{namespace}': {e}")
        raise


def create_or_load_table(
    catalog: Catalog, namespace: str, table_name: str, arrow_table
):
    """Create a new table or load existing one."""
    table_id = f"{namespace}.{table_name}"

    try:
        iceberg_table: Table = catalog.load_table(table_id)
        logger.info(f"Loaded existing table: {table_id}")
    except Exception as e:
        logger.debug(f"Table {table_id} does not exist, creating new table...")
        try:
            iceberg_table = catalog.create_table(
                identifier=table_id,
                schema=arrow_table.schema,
                location=f"s3://{MINIO_BUCKET}/{namespace}/{table_name}",
            )
            logger.info(f"Created new table: {table_id}")
        except Exception as create_error:
            logger.error(f"Failed to create table {table_id}: {create_error}")
            raise

    return iceberg_table


# =============================================================================
# Users Export
# =============================================================================


def fetch_users() -> pl.DataFrame:
    """Fetch users from MySQL using Polars (via connectorx)."""
    query = """
        SELECT 
            id, user_id, email, phone, full_name, first_name, last_name,
            avatar_url, city, region, country_code, timezone,
            os_name, browser_name, app_version, device_model,
            CAST(properties AS CHAR) as properties,
            created_at, updated_at, last_seen_at
        FROM users
    """
    try:
        logger.debug(f"Fetching users from MySQL: {MYSQL_URI}")
        df = pl.read_database_uri(query, MYSQL_URI)
        logger.info(f"Fetched {len(df):,} users from MySQL")
        return df
    except Exception as e:
        logger.error(f"Failed to fetch users from MySQL: {e}")
        raise


def backfill_users(catalog: Catalog, namespace: str = DEFAULT_NAMESPACE) -> int:
    """Export users from MySQL to Iceberg table."""
    logger.info("=" * 60)
    logger.info("Backfill: users")
    logger.info("=" * 60)

    # 1. Fetch from MySQL
    logger.info("1. Fetching users from MySQL...")
    try:
        df = fetch_users()
    except Exception as e:
        logger.error(f"Failed to fetch users: {e}")
        raise

    if df.is_empty():
        logger.info("No users found. Skipping.")
        return 0

    # 2. Create or load table
    logger.info("2. Creating/loading Iceberg table...")
    try:
        arrow_table = df.to_arrow()
        logger.debug(
            f"Converted Polars DataFrame to Arrow table with {arrow_table.num_rows} rows"
        )
        iceberg_table = create_or_load_table(catalog, namespace, "users", arrow_table)
    except Exception as e:
        logger.error(f"Failed to create/load Iceberg table: {e}")
        raise

    # 3. Write data (overwrite mode)
    logger.info(f"3. Writing {len(df):,} rows to Iceberg...")
    try:
        iceberg_table.append(arrow_table)
        logger.info(f"Successfully exported {len(df):,} users to {namespace}.users")
    except Exception as e:
        logger.error(f"Failed to write data to Iceberg: {e}")
        raise

    return len(df)


# =============================================================================
# Events Export
# =============================================================================


def fetch_events() -> pl.DataFrame:
    """Fetch events from MySQL using Polars (via connectorx)."""
    query = """
        SELECT 
            id, insert_id, event_name, user_id, event_time,
            session_id, device_id, os_name, os_version, device_model,
            browser_name, browser_version, app_version,
            ip_address, country_code, city,
            page_url, page_title, screen_name, referrer,
            experiment_id, variant_id,
            revenue, currency_code,
            CAST(properties AS CHAR) as properties,
            created_at
        FROM events
    """
    try:
        logger.debug(f"Fetching events from MySQL: {MYSQL_URI}")
        df = pl.read_database_uri(query, MYSQL_URI)
        logger.info(f"Fetched {len(df):,} events from MySQL")
        return df
    except Exception as e:
        logger.error(f"Failed to fetch events from MySQL: {e}")
        raise


def backfill_events(catalog: Catalog, namespace: str = DEFAULT_NAMESPACE) -> int:
    """Export events from MySQL to Iceberg table."""
    logger.info("=" * 60)
    logger.info("Backfill: events")
    logger.info("=" * 60)
    # 1. Fetch from MySQL
    logger.info("1. Fetching events from MySQL...")
    try:
        df = fetch_events()
    except Exception as e:
        logger.error(f"Failed to fetch events: {e}")
        raise

    if df.is_empty():
        logger.info("No events found. Skipping.")
        return 0

    # 2. Create or load table
    logger.info("2. Creating/loading Iceberg table...")
    try:
        arrow_table = df.to_arrow()
        logger.debug(
            f"Converted Polars DataFrame to Arrow table with {arrow_table.num_rows} rows"
        )
        iceberg_table = create_or_load_table(catalog, namespace, "events", arrow_table)
    except Exception as e:
        logger.error(f"Failed to create/load Iceberg table: {e}")
        raise

    # 3. Write data (overwrite mode)
    logger.info(f"3. Writing {len(df):,} rows to Iceberg...")
    try:
        iceberg_table.append(arrow_table)
        logger.info(f"Successfully exported {len(df):,} events to {namespace}.events")
    except Exception as e:
        logger.error(f"Failed to write data to Iceberg: {e}")
        raise

    return len(df)
