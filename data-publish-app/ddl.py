import os
from pathlib import Path

import mysql.connector


def get_connection(database: str | None = None):
    """Create MySQL connection using docker-compose defaults (root user for DDL)."""
    config = {
        "host": os.getenv("MYSQL_HOST", "localhost"),
        "port": int(os.getenv("MYSQL_PORT", "3306")),
        "user": os.getenv("MYSQL_USER", "root"),
        "password": os.getenv("MYSQL_PASSWORD", "mysql"),
    }
    if database:
        config["database"] = database
    return mysql.connector.connect(**config)


def create_database(db_name: str) -> None:
    """Create database if it doesn't exist."""
    connection = None
    cursor = None
    try:
        connection = get_connection()
        cursor = connection.cursor()
        cursor.execute(f"CREATE DATABASE IF NOT EXISTS {db_name}")
        connection.commit()
        print(f"Database '{db_name}' created or already exists")
    except mysql.connector.Error as e:
        print(f"Error creating database: {e}")
        raise
    finally:
        if cursor:
            cursor.close()
        if connection and connection.is_connected():
            connection.close()


def grant_privileges(db_name: str, user: str = "mysql") -> None:
    """Grant INSERT, UPDATE, SELECT privileges to a user on all tables in database."""
    connection = None
    cursor = None
    try:
        connection = get_connection()
        cursor = connection.cursor()
        cursor.execute(f"GRANT SELECT, INSERT, UPDATE ON {db_name}.* TO '{user}'@'%'")
        cursor.execute("FLUSH PRIVILEGES")
        connection.commit()
        print(f"Granted SELECT, INSERT, UPDATE on {db_name}.* to '{user}'")
    except mysql.connector.Error as e:
        print(f"Error granting privileges: {e}")
        raise
    finally:
        if cursor:
            cursor.close()
        if connection and connection.is_connected():
            connection.close()


def execute_ddl(sql_file: str, database: str) -> None:
    """Execute DDL statements from a SQL file."""
    sql_path = Path(__file__).parent / sql_file

    if not sql_path.exists():
        raise FileNotFoundError(f"SQL file not found: {sql_path}")

    sql_content = sql_path.read_text()

    # Split by semicolon, filter empty statements and comments-only blocks
    statements = []
    for stmt in sql_content.split(";"):
        stmt = stmt.strip()
        # Skip empty or comment-only statements
        if stmt and not all(
            line.strip().startswith("--") or not line.strip()
            for line in stmt.split("\n")
        ):
            statements.append(stmt)

    connection = None
    cursor = None
    try:
        connection = get_connection(database)
        cursor = connection.cursor()

        for stmt in statements:
            # Extract first meaningful line for logging
            first_line = next(
                (
                    line.strip()
                    for line in stmt.split("\n")
                    if line.strip() and not line.strip().startswith("--")
                ),
                "Unknown",
            )
            print(f"Executing: {first_line[:60]}...")
            cursor.execute(stmt)

        connection.commit()
        print(f"\nSuccessfully executed {len(statements)} statements from {sql_file}")

    except mysql.connector.Error as e:
        print(f"Error executing DDL: {e}")
        raise
    finally:
        if cursor:
            cursor.close()
        if connection and connection.is_connected():
            connection.close()
