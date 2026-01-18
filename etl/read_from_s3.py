from typing import Any, Tuple
import polars as pl
from pyiceberg.catalog import Catalog, load_catalog
from pyiceberg.table import Table

# S3/MinIO configuration
MINIO_ENDPOINT = "http://localhost:9000"
MINIO_ACCESS_KEY = "minioadmin"
MINIO_SECRET_KEY = "minioadmin"

# Iceberg REST catalog configuration
ICEBERG_REST_URI = "http://localhost:8181"
ICEBERG_WAREHOUSE = "s3://warehouse/"


def get_iceberg_catalog() -> Catalog:
    """Create PyIceberg catalog connected to iceberg-rest service."""
    return load_catalog(
        "iceberg_rest",
        **{
            "type": "rest",
            "uri": ICEBERG_REST_URI,
            "warehouse": ICEBERG_WAREHOUSE,
            "s3.endpoint": MINIO_ENDPOINT,
            "s3.access-key-id": MINIO_ACCESS_KEY,
            "s3.secret-access-key": MINIO_SECRET_KEY,
            "s3.path-style-access": "true",
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
                "uri": ICEBERG_REST_URI,
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
        iceberg_table: Table = catalog.load_table(table_id)
        print(f"Loaded existing table: {table_id}")
    except Exception:
        # Create new managed table (catalog determines location)
        # Only pass location if explicitly provided (for external tables)
        if location:
            iceberg_table = catalog.create_table(
                identifier=table_id,
                schema=arrow_table.schema,
                location=location,
            )
            print(f"Created new external table: {table_id} at {location}")
        else:
            iceberg_table = catalog.create_table(
                identifier=table_id,
                schema=arrow_table.schema,
            )
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


if __name__ == "__main__":
    print("=" * 60)
    print("Iceberg Catalogs (Before)")
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

    # print("=" * 60)
    # print("Loading and Registering Tables")
    # print("=" * 60)
    # users_df, events_df = load_and_register_tables("unnest")
    # print()
    #
    # print("=" * 60)
    # print("Iceberg Catalogs (After)")
    # print("=" * 60)
    # catalogs = list_iceberg_catalogs()
    # for catalog in catalogs:
    #     print(f"  Catalog: {catalog['name']}")
    #     print(f"  URI: {catalog['uri']}")
    #     print(f"  Namespaces: {catalog['namespaces']}")
    #     print(f"  Tables:")
    #     for ns, tables in catalog["tables"].items():
    #         for table in tables:
    #             print(f"    - {table}")
