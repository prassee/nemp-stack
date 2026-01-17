from pyiceberg.catalog import Catalog
import polars as pl
from pyiceberg.catalog import load_catalog

# Read parquet from S3
df = pl.read_parquet(
    "s3://stage/backfill/users/users_2025_01.parquet",
    storage_options={
        "endpoint_url": "http://localhost:9000",
        "aws_access_key_id": "minioadmin",
        "aws_secret_access_key": "minioadmin",
    },
)

# Connect to Polaris REST catalog
catalog: Catalog = load_catalog(
    "polaris",
    type="rest",
    uri="http://localhost:8181/iceberg",
    warehouse="default",
    credential="root:s3cr3t",
    **{
        "s3.endpoint": "http://localhost:9000",
        "s3.access-key-id": "minioadmin",
        "s3.secret-access-key": "minioadmin",
        "s3.path-style-access": "true",
        "s3.region": "us-east-1",
    },
)

# Create namespace if it doesn't exist
# namespace = "default"
# if namespace not in [ns[0] for ns in catalog.list_namespaces()]:
#     catalog.create_namespace(namespace)
#
# # Convert Polars to PyArrow and create Iceberg table
# arrow_table = df.to_arrow()
# table_name = f"{namespace}.users"
#
# # Create or replace the table
# if table_name in [f"{t[0]}.{t[1]}" for t in catalog.list_tables(namespace)]:
#     table = catalog.load_table(table_name)
#     table.overwrite(arrow_table)
# else:
#     table = catalog.create_table(table_name, schema=arrow_table.schema)
#     table.append(arrow_table)
#
# print(f"Registered Iceberg table: {table_name}")
# print(f"Table location: {table.location()}")
#
if __name__ == "__main__":
    # print(df)
    catalog_tables = catalog.list_tables("default")
    print(
        f"Tables in 'default' namespace: {[f'{t[0]}.{t[1]}' for t in catalog_tables]}"
    )
