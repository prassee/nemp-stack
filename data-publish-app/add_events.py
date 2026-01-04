import json
import random
import uuid
from datetime import datetime, timedelta

import mysql.connector

from ddl import get_connection

# Event names for a typical mobile app
EVENT_NAMES = [
    "app_open",
    "app_close",
    "screen_view",
    "button_click",
    "search",
    "view_item",
    "add_to_cart",
    "remove_from_cart",
    "begin_checkout",
    "purchase",
    "sign_up",
    "login",
    "logout",
    "share",
    "rate_app",
    "notification_received",
    "notification_opened",
    "profile_update",
    "settings_change",
    "error",
]

# Event weights (some events happen more frequently)
EVENT_WEIGHTS = [
    15,  # app_open
    12,  # app_close
    20,  # screen_view
    15,  # button_click
    8,  # search
    10,  # view_item
    5,  # add_to_cart
    2,  # remove_from_cart
    2,  # begin_checkout
    1,  # purchase
    1,  # sign_up
    3,  # login
    2,  # logout
    1,  # share
    0.5,  # rate_app
    1,  # notification_received
    0.5,  # notification_opened
    0.5,  # profile_update
    0.3,  # settings_change
    0.2,  # error
]

# Screen names
SCREEN_NAMES = [
    "HomeScreen",
    "ProductListScreen",
    "ProductDetailScreen",
    "CartScreen",
    "CheckoutScreen",
    "ProfileScreen",
    "SettingsScreen",
    "SearchScreen",
    "OrderHistoryScreen",
    "WishlistScreen",
    "NotificationsScreen",
    "HelpScreen",
    "AboutScreen",
]

# OS versions
ANDROID_VERSIONS = ["12", "13", "14"]
IOS_VERSIONS = ["16.0", "16.5", "17.0", "17.1", "17.2"]


def generate_ip_address() -> str:
    """Generate a random Indian IP address."""
    # Common Indian IP ranges
    prefixes = ["103.", "106.", "117.", "122.", "182.", "183.", "202.", "203."]
    prefix = random.choice(prefixes)
    return f"{prefix}{random.randint(0, 255)}.{random.randint(0, 255)}.{random.randint(0, 255)}"


def generate_event(user: dict, event_time: datetime) -> dict:
    """Generate a single event record based on user data."""
    event_name = random.choices(EVENT_NAMES, weights=EVENT_WEIGHTS, k=1)[0]

    os_name = user["os_name"]
    os_version = random.choice(IOS_VERSIONS if os_name == "iOS" else ANDROID_VERSIONS)

    # Generate session_id (users typically have multiple sessions per day)
    session_id = str(uuid.uuid4())

    # Generate device_id (consistent per user in real scenarios, but random here)
    device_id = str(uuid.uuid4())

    # Build event properties based on event type
    properties = {}
    revenue = None
    currency_code = None

    if event_name == "screen_view":
        properties["screen_name"] = random.choice(SCREEN_NAMES)
    elif event_name == "search":
        properties["search_term"] = random.choice(
            ["shoes", "phone", "laptop", "watch", "shirt", "bag"]
        )
    elif event_name == "view_item":
        properties["item_id"] = f"PROD_{random.randint(1000, 9999)}"
        properties["item_name"] = random.choice(
            ["Running Shoes", "Smartphone", "Laptop", "Smart Watch", "T-Shirt"]
        )
        properties["item_category"] = random.choice(
            ["Electronics", "Fashion", "Sports", "Home"]
        )
    elif event_name in ["add_to_cart", "remove_from_cart"]:
        properties["item_id"] = f"PROD_{random.randint(1000, 9999)}"
        properties["quantity"] = random.randint(1, 3)
    elif event_name == "purchase":
        revenue = round(random.uniform(100, 10000), 2)
        currency_code = "INR"
        properties["order_id"] = f"ORD_{random.randint(100000, 999999)}"
        properties["items_count"] = random.randint(1, 5)
    elif event_name == "error":
        properties["error_code"] = random.choice(
            ["E001", "E002", "E003", "E404", "E500"]
        )
        properties["error_message"] = random.choice(
            ["Network error", "Timeout", "Invalid input", "Server error"]
        )

    return {
        "insert_id": str(uuid.uuid4()),
        "event_name": event_name,
        "user_id": user["user_id"],
        "event_time": int(event_time.timestamp() * 1000),  # Unix timestamp in ms
        "session_id": session_id,
        "device_id": device_id,
        "os_name": os_name,
        "os_version": os_version,
        "device_model": user["device_model"],
        "app_version": user["app_version"],
        "ip_address": generate_ip_address(),
        "country_code": user["country_code"],
        "city": user["city"],
        "screen_name": properties.get("screen_name") or random.choice(SCREEN_NAMES),
        "revenue": revenue,
        "currency_code": currency_code,
        "properties": json.dumps(properties) if properties else None,
    }


def fetch_users(database: str) -> list[dict]:
    """Fetch all users from the database."""
    connection = None
    cursor = None

    try:
        connection = get_connection(database)
        cursor = connection.cursor(dictionary=True)

        cursor.execute("""
            SELECT user_id, os_name, device_model, app_version, 
                   country_code, city
            FROM users
        """)

        users = cursor.fetchall()
        print(f"Fetched {len(users)} users from database")
        return users

    except mysql.connector.Error as e:
        print(f"Error fetching users: {e}")
        raise
    finally:
        if cursor:
            cursor.close()
        if connection and connection.is_connected():
            connection.close()


def insert_events(database: str, events_per_day: int = 1000000) -> None:
    """Insert events for each day from Jan 1 to Jan 10, 2025."""
    start_date = datetime(2025, 1, 1)
    end_date = datetime(2025, 1, 10)

    # Fetch users first
    users = fetch_users(database)
    if not users:
        print("No users found in database. Run add_users.py first.")
        return

    connection = None
    cursor = None

    insert_sql = """
        INSERT INTO events (
            insert_id, event_name, user_id, event_time,
            session_id, device_id, os_name, os_version, device_model,
            app_version, ip_address, country_code, city,
            screen_name, revenue, currency_code, properties
        ) VALUES (
            %(insert_id)s, %(event_name)s, %(user_id)s, %(event_time)s,
            %(session_id)s, %(device_id)s, %(os_name)s, %(os_version)s, %(device_model)s,
            %(app_version)s, %(ip_address)s, %(country_code)s, %(city)s,
            %(screen_name)s, %(revenue)s, %(currency_code)s, %(properties)s
        )
    """

    try:
        connection = get_connection(database)
        cursor = connection.cursor()

        current_date = start_date
        total_events = 0
        batch_size = 10000

        while current_date <= end_date:
            day_events = 0

            # Process in batches
            for batch_start in range(0, events_per_day, batch_size):
                batch_count = min(batch_size, events_per_day - batch_start)
                events = []

                for _ in range(batch_count):
                    # Pick a random user
                    user = random.choice(users)

                    # Generate random time during the day
                    event_time = current_date + timedelta(
                        hours=random.randint(0, 23),
                        minutes=random.randint(0, 59),
                        seconds=random.randint(0, 59),
                        milliseconds=random.randint(0, 999),
                    )

                    events.append(generate_event(user, event_time))

                cursor.executemany(insert_sql, events)
                connection.commit()

                day_events += batch_count
                total_events += batch_count

                print(
                    f"  {current_date.strftime('%Y-%m-%d')}: Inserted {day_events}/{events_per_day} events..."
                )

            print(
                f"Completed {current_date.strftime('%Y-%m-%d')}: {day_events} events (Total: {total_events})"
            )
            current_date += timedelta(days=1)

        print(f"\nCompleted! Total events inserted: {total_events}")

    except mysql.connector.Error as e:
        print(f"Error inserting events: {e}")
        raise
    finally:
        if cursor:
            cursor.close()
        if connection and connection.is_connected():
            connection.close()


if __name__ == "__main__":
    insert_events("mixpanel")
