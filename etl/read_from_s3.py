from typing import Any, Tuple
import socket
import polars as pl
import s3fs
from pyiceberg.catalog import Catalog
from pyiceberg.catalog.rest import RestCatalog
from pyiceberg.table import Table

# S3/MinIO configuration
MINIO_ENDPOINT = "http://localhost:9000"
MINIO_ACCESS_KEY = "minioadmin"
MINIO_SECRET_KEY = "minioadmin"

# LakeKeeper Iceberg REST catalog configuration
# Note: LakeKeeper uses /catalog path and warehouse name (not s3:// path)
LAKEKEEPER_URI = "http://localhost:8181/catalog"
LAKEKEEPER_WAREHOUSE = "warehouse"  # Warehouse name created in LakeKeeper

# DNS override: Map 'minio' hostname to localhost
# This is needed because LakeKeeper returns Docker-internal 'minio:9000' endpoint
# but PyIceberg runs on the host where 'minio' doesn't resolve.
_original_getaddrinfo = socket.getaddrinfo


def _patched_getaddrinfo(host, port, *args, **kwargs):
    if host == "minio":
        host = "127.0.0.1"
    return _original_getaddrinfo(host, port, *args, **kwargs)


socket.getaddrinfo = _patched_getaddrinfo


def get_iceberg_catalog() -> Catalog:
    """Create PyIceberg catalog connected to LakeKeeper service.

    Note: We explicitly provide S3 configuration here to override the endpoint
    returned by LakeKeeper (which uses Docker-internal 'minio:9000' hostname).
    This allows PyIceberg running on the host to connect to MinIO via localhost.
    """
    return RestCatalog(
        name="lakekeeper",
        uri=LAKEKEEPER_URI,
        warehouse=LAKEKEEPER_WAREHOUSE,
        **{
            "s3.endpoint": MINIO_ENDPOINT,
            "s3.access-key-id": MINIO_ACCESS_KEY,
            "s3.secret-access-key": MINIO_SECRET_KEY,
            "s3.region": "us-east-1",
        },
    )


def list_iceberg_catalogs() -> list[dict[str, Any]]:
    """
    List available catalogs from the Iceberg REST catalog service.

    Uses PyIceberg to connect to the iceberg-rest service and retrieve
    catalog information including namespaces and tables.

    Returns:
        List of catalog information dictionaries with 'name', 'namespaces', and 'tables' keys.
    """
    try:
        catalog: Catalog = get_iceberg_catalog()

        # Get all namespaces
        namespaces = catalog.list_namespaces()

        # Get tables for each namespace
        tables_by_namespace: dict[str, list[str]] = {}
        for ns in namespaces:
            ns_name = ".".join(ns)
            tables = catalog.list_tables(ns)
            tables_by_namespace[ns_name] = [".".join(t) for t in tables]

        return [
            {
                "name": catalog.name,
                "uri": LAKEKEEPER_URI,
                "namespaces": [".".join(ns) for ns in namespaces],
                "tables": tables_by_namespace,
            }
        ]

    except Exception as e:
        print(f"Error connecting to Iceberg REST catalog: {e}")
        return []


def load_df_from_s3() -> Tuple[pl.DataFrame, pl.DataFrame]:
    """Load users and events dataframes from S3 parquet files."""
    users_file = "s3://stage/backfill/users/users_2025_01.parquet"
    events_file = "s3://stage/backfill/events/events_2025_01_01.parquet"
    # Read parquet from S3
    users_df: pl.DataFrame = pl.read_parquet(
        users_file,
        storage_options={
            "endpoint_url": MINIO_ENDPOINT,
            "aws_access_key_id": MINIO_ACCESS_KEY,
            "aws_secret_access_key": MINIO_SECRET_KEY,
        },
    )
    events_df: pl.DataFrame = pl.read_parquet(
        events_file,
        storage_options={
            "endpoint_url": MINIO_ENDPOINT,
            "aws_access_key_id": MINIO_ACCESS_KEY,
            "aws_secret_access_key": MINIO_SECRET_KEY,
        },
    )
    return users_df, events_df


def ensure_namespace(catalog: Catalog, namespace: str) -> None:
    """Create namespace if it doesn't exist."""
    namespaces: list[str] = [ns[0] for ns in catalog.list_namespaces()]
    if namespace not in namespaces:
        catalog.create_namespace(namespace)
        print(f"Created namespace: {namespace}")


def get_s3_filesystem() -> s3fs.S3FileSystem:
    """Create S3FileSystem for MinIO access."""
    return s3fs.S3FileSystem(
        endpoint_url=MINIO_ENDPOINT,
        key=MINIO_ACCESS_KEY,
        secret=MINIO_SECRET_KEY,
    )


def drop_iceberg_table(
    catalog: Catalog,
    namespace: str,
    table_name: str,
    purge: bool = True,
) -> None:
    """
    Drop an Iceberg table from the catalog.

    With LakeKeeper, file cleanup is handled automatically by the catalog:
    - Metadata files are cleaned up based on `write.metadata.delete-after-commit.enabled`
    - Snapshots are expired based on warehouse/table configuration
    - Data files are deleted when snapshots expire

    Args:
        catalog: PyIceberg catalog instance
        namespace: Iceberg namespace (e.g., 'analytics')
        table_name: Name of the table to drop
        purge: If True, request catalog to purge data files (LakeKeeper handles this).
               If False, only remove table from catalog metadata.
    """
    table_id: str = f"{namespace}.{table_name}"

    try:
        if purge:
            # LakeKeeper handles file deletion automatically when purge=True
            # This uses catalog.purge_table() which tells LakeKeeper to delete files
            catalog.purge_table(table_id)
            print(f"Purged table (data deleted by LakeKeeper): {table_id}")
        else:
            catalog.drop_table(table_id)
            print(f"Dropped table (data retained): {table_id}")
    except Exception as e:
        print(f"Error dropping table {table_id}: {e}")


def drop_iceberg_namespace(catalog: Catalog, namespace: str) -> None:
    """
    Drop an Iceberg namespace from the catalog.

    Args:
        catalog: PyIceberg catalog instance
        namespace: Iceberg namespace to drop
    """
    try:
        catalog.drop_namespace(namespace)
        print(f"Dropped namespace: {namespace}")
    except Exception as e:
        print(f"Error dropping namespace {namespace}: {e}")


def register_iceberg_table(
    catalog: Catalog,
    namespace: str,
    table_name: str,
    df: pl.DataFrame,
    overwrite: bool = True,
    location: str | None = None,
) -> Table:
    """
    Register a Polars DataFrame as an Iceberg table.

    Args:
        catalog: PyIceberg catalog instance
        namespace: Iceberg namespace (e.g., 'analytics')
        table_name: Name of the table to create
        df: Polars DataFrame to register
        overwrite: If True, overwrite existing data; if False, append
        location: Optional custom location for external table. If None,
                  creates a managed table using catalog's default warehouse.

    Returns:
        The Iceberg table instance
    """
    table_id: str = f"{namespace}.{table_name}"
    arrow_table = df.to_arrow()

    try:
        # Try to load existing table
        iceberg_table = catalog.load_table(table_id)
        print(f"Loaded existing table: {table_id}")
    except Exception:
        # Create new managed table (catalog determines location)
        create_kwargs: dict[str, Any] = {
            "identifier": table_id,
            "schema": arrow_table.schema,
        }
        if location:
            create_kwargs["location"] = location

        iceberg_table = catalog.create_table(**create_kwargs)

        if location:
            print(f"Created new external table: {table_id} at {location}")
        else:
            print(f"Created new managed table: {table_id}")

    # Write data to table
    if overwrite:
        iceberg_table.overwrite(arrow_table)
        print(f"Overwrote {len(df):,} rows to {table_id}")
    else:
        iceberg_table.append(arrow_table)
        print(f"Appended {len(df):,} rows to {table_id}")

    return iceberg_table


def load_and_register_tables(namespace: str) -> Tuple[pl.DataFrame, pl.DataFrame]:
    """
    Load users and events from S3 and register them as Iceberg tables.

    Args:
        namespace: Iceberg namespace to register tables in

    Returns:
        Tuple of (users_df, events_df) DataFrames
    """
    # Load dataframes from S3
    print("Loading dataframes from S3...")
    users_df, events_df = load_df_from_s3()
    print(f"  Users: {len(users_df):,} rows")
    print(f"  Events: {len(events_df):,} rows")

    # Connect to catalog
    print("\nConnecting to Iceberg catalog...")
    catalog: Catalog = get_iceberg_catalog()

    # Ensure namespace exists
    ensure_namespace(catalog, namespace)

    # Register tables
    print(f"\nRegistering tables in namespace '{namespace}'...")
    register_iceberg_table(catalog, namespace, "users", users_df)
    register_iceberg_table(catalog, namespace, "events", events_df)

    print("\nDone!")
    return users_df, events_df


def drop_all_namespace():
    """Drop all example namespaces and their tables."""
    # Uncomment to drop tables:
    # drop_iceberg_table(get_iceberg_catalog(), "unnest", "users")
    # drop_iceberg_table(get_iceberg_catalog(), "unnest", "events")
    iceberg_catalog = get_iceberg_catalog()
    drop_iceberg_table(iceberg_catalog, "mysql_mixpanel", "users")
    drop_iceberg_table(iceberg_catalog, "mysql_mixpanel", "events")
    drop_iceberg_table(iceberg_catalog, "test_olake", "test_olake")

    catalog: Catalog = get_iceberg_catalog()
    namespaces = ["test_olake", "mysql_mixpanel", "unnest"]
    for ns in namespaces:
        drop_iceberg_namespace(catalog, ns)


if __name__ == "__main__":

    def list_tables():
        print("=" * 60)
        print("Iceberg Catalog Status")
        print("=" * 60)
        catalogs = list_iceberg_catalogs()
        for catalog in catalogs:
            print(f"  Catalog: {catalog['name']}")
            print(f"  URI: {catalog['uri']}")
            print(f"  Namespaces: {catalog['namespaces']}")
            print(f"  Tables:")
            for ns, tables in catalog["tables"].items():
                for table in tables:
                    print(f"    - {table}")
        if not catalogs:
            print("  No catalogs available or connection error")

    list_tables()
    # Uncomment to load and register tables:
    # users_df, events_df = load_and_register_tables("unnest")

    drop_all_namespace()
    list_tables()
