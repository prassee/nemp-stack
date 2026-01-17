import polars as pl


# read data from a CSV file in to a Polars DataFrame and export it to a Parquet file
def export_csv_to_parquet(
    csv_file_path: str,
    parquet_file_path: str,
) -> None:
    """Export data from CSV to Parquet using Polars."""
    print("=" * 60)
    print("Exporting data from CSV to Parquet")
    print("=" * 60)

    try:
        # Read data from CSV file
        print(f"\n1. Reading data from CSV file: {csv_file_path}...")
        df = pl.read_csv(csv_file_path, has_header=True, try_parse_dates=True)
        print(f"Read {df.height} rows and {df.width} columns from CSV")

        if df.height == 0:
            print("No data found in CSV file. Nothing to export.")
            return

        # Write data to Parquet file
        print(f"\n2. Writing data to Parquet file: {parquet_file_path}...")
        df.write_parquet(parquet_file_path)
        print(f"Successfully exported data to Parquet file: {parquet_file_path}")

    except Exception as e:
        print(f"Error exporting data: {e}")
        raise


# read the parquet file and print the first 5 rows
def read_parquet(file_path: str) -> None:
    """Read and display data from Parquet file."""
    df: pl.DataFrame = pl.read_parquet(file_path)
    print(f"Read {df.height} rows and {df.width} columns from Parquet")
    print("\nFirst 5 rows:")
    print(df.head(5))


if __name__ == "__main__":
    # export_csv_to_parquet(
    #     csv_file_path="/data/datasets/users_2025_03.csv",
    #     parquet_file_path="/data/datasets/users_2025_03.parquet",
    # )
    read_parquet("/data/datasets/users_2025_01.parquet")
    read_parquet("/data/datasets/users_2025_02.parquet")
    read_parquet("/data/datasets/users_2025_03.parquet")
