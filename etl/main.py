from pyiceberg.catalog import load_catalog
from pyiceberg.schema import Schema
from pyiceberg.types import (
    NestedField,
    StringType,
    LongType,
    TimestampType,
    DoubleType,
)
import pyarrow as pa


def get_catalog():
    """Create a catalog connection to Nessie with MinIO as storage backend."""
    return load_catalog(
        "nessie",
        **{
            "type": "rest",
            "uri": "http://localhost:19120/iceberg",
            "warehouse": "s3://warehouse",
            "s3.endpoint": "http://localhost:9000",
            "s3.access-key-id": "minioadmin",
            "s3.secret-access-key": "minioadmin",
            "s3.region": "us-east-1",
            "s3.path-style-access": "true",
        },
    )


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
    """Register a new Iceberg table in the Nessie catalog."""
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
            location=f"s3://warehouse/{namespace}/{table_name}",
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


def main():
    print("Connecting to Nessie catalog...")
    catalog = get_catalog()

    print(f"Catalog: {catalog.name} with props {catalog.properties}")

    # Create example schema
    schema = create_example_schema()
    #
    # # Register a table
    namespace = "default"
    table_name = "example_table"
    #
    table = register_table(catalog, namespace, table_name, schema)

    # # List tables
    list_tables(catalog, namespace)

    print("\nTable schema:")
    print(table.schema())


if __name__ == "__main__":
    main()
