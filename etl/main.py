#!/usr/bin/env python3
"""
ETL Pipeline CLI

Unified command-line interface for:
- Setting up Polaris catalog
- Backfilling MySQL data to Iceberg

Usage:
    python main.py setup              # Setup Polaris catalog
    python main.py backfill           # Export all tables (users, events)
    python main.py backfill users     # Export only users
    python main.py backfill events    # Export only events
    python main.py --help             # Show help
"""

import logging
from typing import Optional

import typer

from backfill import (
    DEFAULT_NAMESPACE,
    MINIO_BUCKET,
    MINIO_ENDPOINT,
    MYSQL_URI,
    POLARIS_URI,
    backfill_events,
    backfill_users,
    ensure_namespace,
    get_iceberg_catalog,
)
from logger import get_logger, setup_logging
from setup_polaris import (
    create_catalog,
    delete_catalog,
    get_bearer_token,
    grant_catalog_role,
    list_catalogs,
)

# Initialize logger for this module
logger = logging.getLogger(__name__)

app = typer.Typer(
    name="etl",
    help="ETL Pipeline: MySQL -> Iceberg via Polaris",
    add_completion=False,
)


# =============================================================================
# Setup Commands
# =============================================================================


@app.command()
def setup(
    catalog_name: str = typer.Option(
        "warehouse", "--catalog", "-c", help="Catalog name to create"
    ),
    force: bool = typer.Option(
        False, "--force", "-f", help="Delete existing catalog before creating"
    ),
):
    """
    Setup Polaris catalog with proper permissions.

    Creates a new catalog in Polaris with S3/MinIO storage backend
    and grants necessary permissions for table operations.
    """
    logger.info("Starting Polaris catalog setup...")
    typer.echo("Setting up Polaris...")

    try:
        logger.info("Step 1: Getting OAuth2 token...")
        typer.echo("1. Getting OAuth2 token...")
        token = get_bearer_token()
        typer.echo(f"   Got token: {token[:20]}...")

        logger.info("Step 2: Listing existing catalogs...")
        typer.echo("\n2. Listing existing catalogs...")
        list_catalogs(token)

        if force:
            logger.info(f"Step 3: Force flag enabled, deleting existing '{catalog_name}' catalog...")
            typer.echo(f"\n3. Deleting existing '{catalog_name}' catalog...")
            delete_catalog(token, catalog_name)
        else:
            logger.debug("Force flag not set, skipping catalog deletion")
            typer.echo("\n3. Skipping delete (use --force to delete existing catalog)")

        logger.info(f"Step 4: Creating '{catalog_name}' catalog...")
        typer.echo(f"\n4. Creating '{catalog_name}' catalog...")
        create_catalog(token, catalog_name)

        logger.info(f"Step 5: Granting permissions to '{catalog_name}'...")
        typer.echo("\n5. Granting permissions to catalog...")
        grant_catalog_role(token, catalog_name)

        logger.info("Step 6: Verifying catalog creation...")
        typer.echo("\n6. Verifying catalog was created...")
        list_catalogs(token)

        logger.info("Polaris catalog setup completed successfully")
        typer.echo(typer.style("\nSetup complete!", fg=typer.colors.GREEN, bold=True))

    except Exception as e:
        logger.exception(f"Error during Polaris setup: {e}")
        typer.echo(typer.style(f"Error: {e}", fg=typer.colors.RED), err=True)
        raise typer.Exit(code=1)


# =============================================================================
# Backfill Commands
# =============================================================================


@app.command()
def backfill(
    table: Optional[str] = typer.Argument(
        None,
        help="Table to export: 'users', 'events', or omit for all",
    ),
    namespace: str = typer.Option(
        DEFAULT_NAMESPACE,
        "--namespace",
        "-n",
        help="Iceberg namespace to export to",
    ),
):
    """
    Export MySQL tables to Iceberg.

    Reads data from MySQL using Polars and writes to Iceberg tables
    stored on MinIO via the Polaris catalog.

    Examples:
        python main.py backfill              # Export all tables
        python main.py backfill users        # Export only users
        python main.py backfill events       # Export only events
        python main.py backfill -n myns      # Export to custom namespace
    """
    logger.info(f"Starting backfill command (table={table}, namespace={namespace})")
    typer.echo("=" * 60)
    typer.echo("MySQL -> Iceberg Backfill")
    typer.echo("=" * 60)
    typer.echo(f"\nConfiguration:")
    typer.echo(f"  MySQL:     {MYSQL_URI}")
    typer.echo(f"  Polaris:   {POLARIS_URI}")
    typer.echo(f"  MinIO:     {MINIO_ENDPOINT}")
    typer.echo(f"  Bucket:    {MINIO_BUCKET}")
    typer.echo(f"  Namespace: {namespace}")

    try:
        # Connect to catalog
        logger.info("Connecting to Polaris catalog...")
        typer.echo("\nConnecting to Polaris catalog...")
        catalog = get_iceberg_catalog()
        
        # Ensure namespace exists
        logger.info(f"Ensuring namespace '{namespace}' exists...")
        typer.echo(f"Ensuring namespace '{namespace}' exists...")
        ensure_namespace(catalog, namespace)

        # Determine which tables to export
        if table is None:
            # Export all tables
            logger.info("Exporting all tables (users and events)...")
            users_count = backfill_users(catalog, namespace)
            events_count = backfill_events(catalog, namespace)

            typer.echo("\n" + "=" * 60)
            typer.echo(
                typer.style("Backfill Complete", fg=typer.colors.GREEN, bold=True)
            )
            typer.echo("=" * 60)
            typer.echo(f"\nExported to namespace: {namespace}")
            typer.echo(f"  - users:  {users_count:,} rows")
            typer.echo(f"  - events: {events_count:,} rows")
            typer.echo(f"\nLocation: s3://{MINIO_BUCKET}/{namespace}/")
            logger.info(f"Backfill complete - users: {users_count:,}, events: {events_count:,}")

        elif table.lower() == "users":
            logger.info("Exporting users table...")
            count = backfill_users(catalog, namespace)
            typer.echo(
                typer.style(f"\nExported {count:,} users", fg=typer.colors.GREEN)
            )
            logger.info(f"Users export complete - {count:,} rows")

        elif table.lower() == "events":
            logger.info("Exporting events table...")
            count = backfill_events(catalog, namespace)
            typer.echo(
                typer.style(f"\nExported {count:,} events", fg=typer.colors.GREEN)
            )
            logger.info(f"Events export complete - {count:,} rows")

        else:
            logger.error(f"Unknown table: {table}")
            typer.echo(
                typer.style(f"Unknown table: {table}", fg=typer.colors.RED), err=True
            )
            typer.echo("Available tables: users, events")
            raise typer.Exit(code=1)

    except Exception as e:
        logger.exception(f"Error during backfill: {e}")
        typer.echo(typer.style(f"Error: {e}", fg=typer.colors.RED), err=True)
        raise typer.Exit(code=1)


# =============================================================================
# Info Command
# =============================================================================


@app.command()
def info():
    """
    Show current configuration.
    """
    logger.info("Displaying configuration information...")
    typer.echo("ETL Pipeline Configuration")
    typer.echo("=" * 40)
    typer.echo(f"\nMySQL:")
    typer.echo(f"  URI: {MYSQL_URI}")
    typer.echo(f"\nPolaris:")
    typer.echo(f"  URI: {POLARIS_URI}")
    typer.echo(f"\nMinIO/S3:")
    typer.echo(f"  Endpoint: {MINIO_ENDPOINT}")
    typer.echo(f"  Bucket:   {MINIO_BUCKET}")
    typer.echo(f"\nDefaults:")
    typer.echo(f"  Namespace: {DEFAULT_NAMESPACE}")


if __name__ == "__main__":
    # Initialize logging before running the app
    setup_logging()
    logger.info("ETL Pipeline started")
    app()
