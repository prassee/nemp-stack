import polars as pl
import requests

# S3/MinIO configuration
MINIO_ENDPOINT = "http://localhost:9000"
MINIO_ACCESS_KEY = "minioadmin"
MINIO_SECRET_KEY = "minioadmin"

# Iceberg REST catalog configuration
ICEBERG_REST_URI = "http://localhost:8181"


def list_iceberg_catalogs() -> list[dict]:
    """
    List available catalogs from the Iceberg REST catalog service.

    Uses the Iceberg REST API config endpoint to retrieve catalog information.
    The iceberg-rest service (tabulario/iceberg-rest) exposes catalog config
    at the /v1/config endpoint.

    Returns:
        List of catalog information dictionaries with 'name' and 'properties' keys.
    """
    config_url = f"{ICEBERG_REST_URI}/v1/config"

    try:
        response = requests.get(config_url, timeout=10)
        response.raise_for_status()
        config = response.json()

        catalogs = []
        # The config endpoint returns catalog defaults and overrides
        if "defaults" in config or "overrides" in config:
            # Extract warehouse info which represents the catalog
            catalog_info = {
                "name": config.get("defaults", {}).get("warehouse", "default"),
                "properties": config,
            }
            catalogs.append(catalog_info)

        return catalogs

    except requests.exceptions.RequestException as e:
        print(f"Error connecting to Iceberg REST catalog at {config_url}: {e}")
        return []


def load_df_from_s3() -> pl.DataFrame:
    s3_file = "s3://stage/backfill/users/users_2025_01.parquet"
    s3_file = "s3://stage/backfill/events/events_2025_01_01.parquet"
    # Read parquet from S3
    df: pl.DataFrame = pl.read_parquet(
        s3_file,
        storage_options={
            "endpoint_url": MINIO_ENDPOINT,
            "aws_access_key_id": MINIO_ACCESS_KEY,
            "aws_secret_access_key": MINIO_SECRET_KEY,
        },
    )
    return df


if __name__ == "__main__":
    print("Iceberg Catalogs:")
    print("=" * 40)
    catalogs = list_iceberg_catalogs()
    for catalog in catalogs:
        print(f"  - {catalog['name']}")
        if "properties" in catalog:
            props = catalog["properties"]
            if "defaults" in props:
                print(f"    defaults: {props['defaults']}")

    print("DataFrame Info:")
    print("=" * 40)
    df = load_df_from_s3()
    print(df.describe())
    print(df.head(10))
