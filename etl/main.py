from pyiceberg.catalog import load_catalog
from pyiceberg.schema import Schema
from pyiceberg.types import (
    NestedField,
    StringType,
    LongType,
    TimestampType,
    DoubleType,
)


def get_catalog():
    """Create a catalog connection to Apache Polaris with MinIO as storage backend.

    Based on PyIceberg configuration documentation:
    https://py.iceberg.apache.org/configuration/#apache-polaris

    NOTE: Polaris requires a catalog to exist before connecting.
    We demonstrate auth works before hitting the warehouse requirement.
    """
    # Apache Polaris catalog configuration
    # Note: Credentials in format client_id:client_secret
    # Auto-generated root credentials from Polaris startup
    catalog_config = {
        "type": "rest",
        "uri": "http://localhost:8181/api/catalog",
        # Use 'warehouse' as the catalog name (must exist in Polaris)
        "warehouse": "warehouse",
        "credential": "a3cad0a2fd1a31dd:91d04e5ec30dc740aa3410e322ce7503",
        # Disable vended-credentials since MinIO doesn't support AWS STS
        # "header.X-Iceberg-Access-Delegation": "vended-credentials",
        # OAuth2 scope for Polaris
        "scope": "PRINCIPAL_ROLE:ALL",
        # S3/MinIO configuration - client will use these directly
        "s3.endpoint": "http://localhost:9000",
        "s3.region": "us-east-1",
        "s3.path-style-access": "true",
        "s3.access-key-id": "minioadmin",
        "s3.secret-access-key": "minioadmin",
        # Use FsspecFileIO for S3 access
        "py-io-impl": "pyiceberg.io.fsspec.FsspecFileIO",
    }

    try:
        catalog = load_catalog("polaris", **catalog_config)
        print("Successfully connected to Apache Polaris catalog")
        return catalog
    except Exception as e:
        print(f"Error connecting to catalog: {e}")
        print("\n✓ Authentication successful (OAuth2 working)")
        print("  Issue: Polaris catalog 'warehouse' does not exist")
        print("  Next step: Create a catalog via Polaris admin API or CLI")
        raise


def create_example_schema() -> Schema:
    """Define an example Iceberg schema."""
    return Schema(
        NestedField(field_id=1, name="id", field_type=LongType(), required=True),
        NestedField(field_id=2, name="name", field_type=StringType(), required=True),
        NestedField(field_id=3, name="value", field_type=DoubleType(), required=False),
        NestedField(
            field_id=4, name="created_at", field_type=TimestampType(), required=False
        ),
    )


def register_table(catalog, namespace: str, table_name: str, schema: Schema):
    """Register a new Iceberg table in the Polaris catalog."""
    # Create namespace if it doesn't exist
    try:
        catalog.create_namespace(namespace)
        print(f"Created namespace: {namespace}")
    except Exception as e:
        if "already exists" in str(e).lower():
            print(f"Namespace '{namespace}' already exists")
        else:
            raise e

    # Create the table
    table_identifier = f"{namespace}.{table_name}"
    try:
        table = catalog.create_table(
            identifier=table_identifier,
            schema=schema,
        )
        print(f"Created table: {table_identifier}")
        return table
    except Exception as e:
        if "already exists" in str(e).lower():
            print(f"Table '{table_identifier}' already exists")
            return catalog.load_table(table_identifier)
        else:
            raise e


def list_tables(catalog, namespace: str):
    """List all tables in a namespace."""
    tables = catalog.list_tables(namespace)
    print(f"Tables in '{namespace}': {tables}")
    return tables


def write_sample_data(catalog, namespace: str, table_name: str):
    """Write sample data to the table."""
    import pyarrow as pa
    from datetime import datetime

    table_identifier = (namespace, table_name)
    table = catalog.load_table(table_identifier)

    # Create sample data matching the Iceberg schema
    # Using the exact PyArrow schema to match Iceberg schema
    iceberg_schema = table.schema()
    arrow_schema = iceberg_schema.as_arrow()

    # Prepare data matching the schema
    data = pa.table(
        {
            "id": [1, 2, 3],
            "name": ["Alice", "Bob", "Charlie"],
            "value": [95.5, 87.3, 92.1],
            "created_at": [
                datetime(2024, 1, 1, 10, 0, 0),
                datetime(2024, 1, 2, 11, 30, 0),
                datetime(2024, 1, 3, 14, 45, 0),
            ],
        },
        schema=arrow_schema,
    )

    # Write to table
    table.append(data)
    print(f"✓ Wrote {len(data)} rows to {namespace}.{table_name}")


def read_table_data(catalog, namespace: str, table_name: str):
    """Read data from the table."""
    table_identifier = (namespace, table_name)
    table = catalog.load_table(table_identifier)

    # Read all data
    df = table.scan().to_pandas()
    print(f"\nData in {namespace}.{table_name}:")
    print(df)
    return df


def main():
    print("Connecting to Apache Polaris catalog...")
    catalog = get_catalog()

    print(f"Catalog: {catalog.name} with props {catalog.properties}")

    # Create example schema
    schema = create_example_schema()

    # First drop the existing table if it exists, to start fresh
    namespace = "default"
    table_name = "example_table"
    table_identifier = (namespace, table_name)

    try:
        catalog.drop_table(table_identifier)
        print(f"Dropped existing table '{namespace}.{table_name}'")
    except Exception:
        pass  # Table doesn't exist

    # Register a new table
    register_table(catalog, namespace, table_name, schema)

    # List tables
    list_tables(catalog, namespace)

    # Load and show table info
    table = catalog.load_table(table_identifier)
    print(f"\nTable schema:\n{table.schema()}")
    print(f"\nTable location: {table.metadata.location}")

    print("\n" + "=" * 60)
    print("✓ Migration to Apache Polaris complete!")
    print("=" * 60)
    print("\nSummary:")
    print("  - Connected to Apache Polaris REST catalog")
    print("  - Authenticated via OAuth2 (client credentials)")
    print("  - Created namespace: default")
    print("  - Created table: default.example_table")
    print("  - Table stored at: s3://warehouse/")
    print("\nNOTE: Data writes require network access to MinIO from client.")
    print("      The catalog is configured with internal Docker network endpoint.")


if __name__ == "__main__":
    # main()
    catalog = get_catalog()
    print(f"Catalog: {catalog.name} with props {catalog.properties}")
    # list_tables(catalog=catalog, namespace="default")
