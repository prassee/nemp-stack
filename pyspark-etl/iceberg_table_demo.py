"""
PySpark job to create and register an Iceberg table in Lakekeeper catalog with MinIO storage.

This script demonstrates:
1. Connecting to Lakekeeper REST catalog
2. Creating a namespace (database)
3. Creating an Iceberg table
4. Inserting sample data
5. Querying the table

Usage:
    spark-submit --master spark://spark-master:7077 \
        --packages org.apache.iceberg:iceberg-spark-runtime-3.5_2.12:1.7.1,org.apache.iceberg:iceberg-aws-bundle:1.7.1 \
        /opt/spark-jobs/iceberg_table_demo.py
"""

from pyspark.sql import SparkSession


def create_spark_session() -> SparkSession:
    """Create SparkSession with Iceberg and Lakekeeper configuration."""
    return (
        SparkSession.builder.appName("Iceberg Table Demo - Lakekeeper")
        .config(
            "spark.sql.extensions",
            "org.apache.iceberg.spark.extensions.IcebergSparkSessionExtensions",
        )
        .config("spark.sql.catalog.lakekeeper", "org.apache.iceberg.spark.SparkCatalog")
        .config("spark.sql.catalog.lakekeeper.type", "rest")
        .config("spark.sql.catalog.lakekeeper.uri", "http://lakekeeper:8181/catalog")
        .config("spark.sql.catalog.lakekeeper.warehouse", "warehouse")
        .config(
            "spark.sql.catalog.lakekeeper.io-impl", "org.apache.iceberg.aws.s3.S3FileIO"
        )
        .config("spark.sql.catalog.lakekeeper.s3.endpoint", "http://minio:9000")
        .config("spark.sql.catalog.lakekeeper.s3.access-key-id", "minioadmin")
        .config("spark.sql.catalog.lakekeeper.s3.secret-access-key", "minioadmin")
        .config("spark.sql.catalog.lakekeeper.s3.path-style-access", "true")
        .config("spark.sql.defaultCatalog", "lakekeeper")
        .getOrCreate()
    )


def create_namespace(spark: SparkSession, namespace: str) -> None:
    """Create a namespace (database) if it doesn't exist."""
    print(f"Creating namespace: {namespace}")
    spark.sql(f"CREATE NAMESPACE IF NOT EXISTS lakekeeper.{namespace}")
    print(f"Namespace '{namespace}' created successfully")


def list_catalog_info(spark: SparkSession) -> None:
    """List namespaces and tables in the catalog."""
    print(f"\n{'=' * 60}")
    print("Lakekeeper Catalog Information")
    print(f"{'=' * 60}")

    print("\nNamespaces:")
    spark.sql("SHOW NAMESPACES IN lakekeeper").show()

    print("\nTables in 'demo' namespace:")
    spark.sql("SHOW TABLES IN lakekeeper.demo").show()


def main():
    """Main entry point for the Iceberg demo job."""
    print("Starting Iceberg Table Demo with Lakekeeper Catalog")
    print("=" * 60)

    # Create Spark session
    spark = create_spark_session()
    spark.sparkContext.setLogLevel("WARN")

    try:
        # Create namespace
        create_namespace(spark, namespace)

        # List catalog info
        list_catalog_info(spark)

     except Exception as e:
        print(f"Error: {e}")
        raise
    finally:
        spark.stop()


if __name__ == "__main__":
    main()
