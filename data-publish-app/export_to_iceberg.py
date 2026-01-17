# import os
#
# import pyarrow as pa
# from pyiceberg.catalog import load_catalog
# from pyiceberg.schema import Schema
# from pyiceberg.types import (
#     LongType,
#     NestedField,
#     StringType,
#     TimestampType,
# )
#
# from ddl import get_connection
#
# # MinIO/S3 configuration from docker-compose.yml
# MINIO_ENDPOINT = os.getenv("MINIO_ENDPOINT", "http://localhost:9000")
# MINIO_ACCESS_KEY = os.getenv("MINIO_ACCESS_KEY", "minioadmin")
# MINIO_SECRET_KEY = os.getenv("MINIO_SECRET_KEY", "minioadmin")
# MINIO_BUCKET = os.getenv("MINIO_BUCKET", "warehouse")
#
# # Polaris catalog configuration
# POLARIS_URI = os.getenv("POLARIS_URI", "http://localhost:8181/api/catalog")
# POLARIS_CREDENTIAL = os.getenv("POLARIS_CREDENTIAL", "root:s3cr3t")
#
# # Iceberg schema for users table
# USERS_ICEBERG_SCHEMA = Schema(
#     NestedField(field_id=1, name="id", field_type=LongType(), required=True),
#     NestedField(field_id=2, name="user_id", field_type=StringType(), required=True),
#     NestedField(field_id=3, name="email", field_type=StringType(), required=False),
#     NestedField(field_id=4, name="phone", field_type=StringType(), required=False),
#     NestedField(field_id=5, name="full_name", field_type=StringType(), required=False),
#     NestedField(field_id=6, name="first_name", field_type=StringType(), required=False),
#     NestedField(field_id=7, name="last_name", field_type=StringType(), required=False),
#     NestedField(field_id=8, name="avatar_url", field_type=StringType(), required=False),
#     NestedField(field_id=9, name="city", field_type=StringType(), required=False),
#     NestedField(field_id=10, name="region", field_type=StringType(), required=False),
#     NestedField(
#         field_id=11, name="country_code", field_type=StringType(), required=False
#     ),
#     NestedField(field_id=12, name="timezone", field_type=StringType(), required=False),
#     NestedField(field_id=13, name="os_name", field_type=StringType(), required=False),
#     NestedField(
#         field_id=14, name="browser_name", field_type=StringType(), required=False
#     ),
#     NestedField(
#         field_id=15, name="app_version", field_type=StringType(), required=False
#     ),
#     NestedField(
#         field_id=16, name="device_model", field_type=StringType(), required=False
#     ),
#     NestedField(
#         field_id=17, name="properties", field_type=StringType(), required=False
#     ),
#     NestedField(
#         field_id=18, name="created_at", field_type=TimestampType(), required=True
#     ),
#     NestedField(
#         field_id=19, name="updated_at", field_type=TimestampType(), required=True
#     ),
#     NestedField(
#         field_id=20, name="last_seen_at", field_type=TimestampType(), required=False
#     ),
# )
#
#
# def get_iceberg_catalog():
#     """Create and return PyIceberg catalog connected to Polaris."""
#     catalog = load_catalog(
#         "polaris",
#         **{
#             "type": "rest",
#             "uri": POLARIS_URI,
#             "credential": POLARIS_CREDENTIAL,
#             "warehouse": "default",
#             "scope": "PRINCIPAL_ROLE:ALL",
#             "s3.endpoint": MINIO_ENDPOINT,
#             "s3.access-key-id": MINIO_ACCESS_KEY,
#             "s3.secret-access-key": MINIO_SECRET_KEY,
#             "s3.path-style-access": "true",
#             "s3.region": "us-east-1",
#         },
#     )
#     return catalog
#
#
# def fetch_users_as_arrow(database: str, batch_size: int = 100000) -> pa.Table:
#     """Fetch users from MySQL and return as PyArrow Table."""
#     connection = None
#     cursor = None
#
#     try:
#         connection = get_connection(database)
#         cursor = connection.cursor(dictionary=True)
#
#         cursor.execute("""
#             SELECT
#                 id, user_id, email, phone, full_name, first_name, last_name,
#                 avatar_url, city, region, country_code, timezone,
#                 os_name, browser_name, app_version, device_model,
#                 CAST(properties AS CHAR) as properties,
#                 created_at, updated_at, last_seen_at
#             FROM users
#         """)
#
#         # Fetch all rows
#         rows = cursor.fetchall()
#         print(f"Fetched {len(rows)} users from MySQL")
#
#         if not rows:
#             return None
#
#         # Convert to PyArrow Table
#         arrays = {
#             "id": pa.array([r["id"] for r in rows], type=pa.int64()),
#             "user_id": pa.array([r["user_id"] for r in rows], type=pa.string()),
#             "email": pa.array([r["email"] for r in rows], type=pa.string()),
#             "phone": pa.array([r["phone"] for r in rows], type=pa.string()),
#             "full_name": pa.array([r["full_name"] for r in rows], type=pa.string()),
#             "first_name": pa.array([r["first_name"] for r in rows], type=pa.string()),
#             "last_name": pa.array([r["last_name"] for r in rows], type=pa.string()),
#             "avatar_url": pa.array([r["avatar_url"] for r in rows], type=pa.string()),
#             "city": pa.array([r["city"] for r in rows], type=pa.string()),
#             "region": pa.array([r["region"] for r in rows], type=pa.string()),
#             "country_code": pa.array(
#                 [r["country_code"] for r in rows], type=pa.string()
#             ),
#             "timezone": pa.array([r["timezone"] for r in rows], type=pa.string()),
#             "os_name": pa.array([r["os_name"] for r in rows], type=pa.string()),
#             "browser_name": pa.array(
#                 [r["browser_name"] for r in rows], type=pa.string()
#             ),
#             "app_version": pa.array([r["app_version"] for r in rows], type=pa.string()),
#             "device_model": pa.array(
#                 [r["device_model"] for r in rows], type=pa.string()
#             ),
#             "properties": pa.array([r["properties"] for r in rows], type=pa.string()),
#             "created_at": pa.array(
#                 [r["created_at"] for r in rows], type=pa.timestamp("us")
#             ),
#             "updated_at": pa.array(
#                 [r["updated_at"] for r in rows], type=pa.timestamp("us")
#             ),
#             "last_seen_at": pa.array(
#                 [r["last_seen_at"] for r in rows], type=pa.timestamp("us")
#             ),
#         }
#
#         table = pa.table(arrays)
#         print(f"Created PyArrow table with {table.num_rows} rows")
#         return table
#
#     except Exception as e:
#         print(f"Error fetching users: {e}")
#         raise
#     finally:
#         if cursor:
#             cursor.close()
#         if connection and connection.is_connected():
#             connection.close()
#
#
# def create_namespace_if_not_exists(catalog, namespace: str) -> None:
#     """Create namespace if it doesn't exist."""
#     try:
#         namespaces = [ns[0] for ns in catalog.list_namespaces()]
#         if namespace not in namespaces:
#             catalog.create_namespace(namespace)
#             print(f"Created namespace: {namespace}")
#         else:
#             print(f"Namespace '{namespace}' already exists")
#     except Exception as e:
#         print(f"Error creating namespace: {e}")
#         raise
#
#
# def export_users_to_iceberg(
#     database: str = "mixpanel",
#     namespace: str = "analytics",
#     table_name: str = "users",
# ) -> None:
#     """Export users from MySQL to Iceberg table on MinIO."""
#     print("=" * 60)
#     print("Exporting users to Iceberg table")
#     print("=" * 60)
#
#     # Fetch data from MySQL
#     print("\n1. Fetching users from MySQL...")
#     arrow_table = fetch_users_as_arrow(database)
#
#     if arrow_table is None or arrow_table.num_rows == 0:
#         print("No users found in database. Nothing to export.")
#         return
#
#     # Connect to Iceberg catalog
#     print("\n2. Connecting to Polaris catalog...")
#     catalog = get_iceberg_catalog()
#
#     # Create namespace
#     print(f"\n3. Creating namespace '{namespace}'...")
#     create_namespace_if_not_exists(catalog, namespace)
#
#     # Create or get table
#     table_identifier = f"{namespace}.{table_name}"
#     print(f"\n4. Creating/loading table '{table_identifier}'...")
#
#     try:
#         # Try to load existing table
#         iceberg_table = catalog.load_table(table_identifier)
#         print(f"Loaded existing table: {table_identifier}")
#     except Exception:
#         # Create new table
#         iceberg_table = catalog.create_table(
#             identifier=table_identifier,
#             schema=USERS_ICEBERG_SCHEMA,
#             location=f"s3://{MINIO_BUCKET}/{namespace}/{table_name}",
#         )
#         print(f"Created new table: {table_identifier}")
#
#     # Write data to Iceberg
#     print(f"\n5. Writing {arrow_table.num_rows} rows to Iceberg...")
#     iceberg_table.overwrite(arrow_table)
#
#     print(f"\n{'=' * 60}")
#     print(f"Successfully exported {arrow_table.num_rows} users to:")
#     print(f"  Catalog: polaris")
#     print(f"  Table: {table_identifier}")
#     print(f"  Location: s3://{MINIO_BUCKET}/{namespace}/{table_name}")
#     print("=" * 60)
#
#
# if __name__ == "__main__":
#     export_users_to_iceberg()
