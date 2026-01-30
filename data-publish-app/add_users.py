import random
import uuid
from datetime import datetime, timedelta
from typing import Any, cast

import mysql.connector
from faker import Faker

from ddl import get_connection

# Initialize Faker with Indian locale
fake = Faker("en_IN")
Faker.seed(42)
random.seed(42)

# Android device models (50)
ANDROID_DEVICES = [
    "Samsung Galaxy S24 Ultra",
    "Samsung Galaxy S24+",
    "Samsung Galaxy S24",
    "Samsung Galaxy S23 Ultra",
    "Samsung Galaxy S23",
    "Samsung Galaxy A54",
    "Samsung Galaxy A34",
    "Samsung Galaxy A14",
    "Samsung Galaxy M54",
    "Samsung Galaxy F54",
    "OnePlus 12",
    "OnePlus 12R",
    "OnePlus 11",
    "OnePlus Nord 3",
    "OnePlus Nord CE 3",
    "Xiaomi 14 Pro",
    "Xiaomi 14",
    "Xiaomi 13 Pro",
    "Xiaomi 13",
    "Redmi Note 13 Pro+",
    "Redmi Note 13 Pro",
    "Redmi Note 13",
    "Redmi 13C",
    "Poco X6 Pro",
    "Poco X6",
    "Poco M6 Pro",
    "Poco F5",
    "Realme GT 5 Pro",
    "Realme GT Neo 5",
    "Realme 12 Pro+",
    "Realme 12 Pro",
    "Realme Narzo 60",
    "Realme C55",
    "Vivo X100 Pro",
    "Vivo X100",
    "Vivo V30 Pro",
    "Vivo V30",
    "Vivo T2 Pro",
    "Vivo Y100",
    "Oppo Find X7 Ultra",
    "Oppo Find X7",
    "Oppo Reno 11 Pro",
    "Oppo Reno 11",
    "Oppo A79",
    "Oppo A58",
    "Motorola Edge 40 Pro",
    "Motorola Edge 40",
    "Motorola G84",
    "Google Pixel 8 Pro",
    "Google Pixel 8",
]

# iOS device models (15)
IOS_DEVICES = [
    "iPhone 15 Pro Max",
    "iPhone 15 Pro",
    "iPhone 15 Plus",
    "iPhone 15",
    "iPhone 14 Pro Max",
    "iPhone 14 Pro",
    "iPhone 14 Plus",
    "iPhone 14",
    "iPhone 13 Pro Max",
    "iPhone 13 Pro",
    "iPhone 13",
    "iPhone 13 mini",
    "iPhone SE (3rd generation)",
    "iPhone 12",
    "iPhone 11",
]

APP_VERSIONS = ["1.0.0", "1.0.1", "1.1.0", "1.2.0", "1.2.1", "2.0.0", "2.0.1", "2.1.0"]


def generate_user(created_at: datetime) -> dict:
    """Generate a single user record."""
    is_male = random.random() < 0.5
    first_name = fake.first_name_male() if is_male else fake.first_name_female()
    last_name = fake.last_name()
    full_name = f"{first_name} {last_name}"

    user_id = str(uuid.uuid4())
    email = fake.email()
    phone = fake.phone_number()

    city = fake.city()
    region = fake.state()

    is_ios = random.random() < 0.3  # 30% iOS, 70% Android
    os_name = "iOS" if is_ios else "Android"
    device_model = random.choice(IOS_DEVICES if is_ios else ANDROID_DEVICES)
    app_version = random.choice(APP_VERSIONS)

    return {
        "user_id": user_id,
        "email": email,
        "phone": phone,
        "full_name": full_name,
        "first_name": first_name,
        "last_name": last_name,
        "city": city,
        "region": region,
        "country_code": "IN",
        "timezone": "Asia/Kolkata",
        "os_name": os_name,
        "device_model": device_model,
        "app_version": app_version,
        "created_at": created_at,
        "last_seen_at": created_at,
    }


def insert_users(database: str, users_per_day: int = 10000) -> None:
    """Insert users for each day from Jan 1, 2025 to March 31, 2025."""
    start_date = datetime(2025, 1, 1)
    end_date = datetime(2025, 3, 31)

    connection = None
    cursor = None

    insert_sql = """
        INSERT INTO users (
            user_id, email, phone, full_name, first_name, last_name,
            city, region, country_code, timezone,
            os_name, device_model, app_version,
            created_at, last_seen_at
        ) VALUES (
            %(user_id)s, %(email)s, %(phone)s, %(full_name)s, %(first_name)s, %(last_name)s,
            %(city)s, %(region)s, %(country_code)s, %(timezone)s,
            %(os_name)s, %(device_model)s, %(app_version)s,
            %(created_at)s, %(last_seen_at)s
        )
    """

    try:
        connection = get_connection(database)
        cursor = connection.cursor()

        current_date = start_date
        total_users = 0

        while current_date <= end_date:
            users = []
            for _ in range(users_per_day):
                # Spread user creation throughout the day
                created_at = current_date + timedelta(
                    hours=random.randint(0, 23),
                    minutes=random.randint(0, 59),
                    seconds=random.randint(0, 59),
                )
                users.append(generate_user(created_at))

            cursor.executemany(insert_sql, users)
            connection.commit()

            total_users += users_per_day
            print(
                f"Inserted {users_per_day} users for {current_date.strftime('%Y-%m-%d')} (Total: {total_users})"
            )

            current_date += timedelta(days=1)

        print(f"\nCompleted! Total users inserted: {total_users}")

    except mysql.connector.Error as e:
        print(f"Error inserting users: {e}")
        raise
    finally:
        if cursor:
            cursor.close()
        if connection and connection.is_connected():
            connection.close()


def update_random_users(database: str, percentage: float = 0.15) -> None:
    """Update a percentage of existing users with new device/location info."""
    connection = None
    cursor = None

    try:
        connection = get_connection(database)
        cursor = connection.cursor()

        # Get total user count
        cursor.execute("SELECT COUNT(*) FROM users")
        result = cursor.fetchone()
        total_users = cast(tuple[int], result)[0] if result else 0
        users_to_update = int(total_users * percentage)

        print(
            f"Total users: {total_users}, updating {users_to_update} ({percentage * 100:.0f}%)"
        )

        # Get random user IDs to update
        cursor.execute(
            "SELECT id FROM users ORDER BY RAND() LIMIT %s", (users_to_update,)
        )
        user_ids = [cast(tuple[int], row)[0] for row in cursor.fetchall()]

        update_sql = """
            UPDATE users SET
                city = %(city)s,
                region = %(region)s,
                os_name = %(os_name)s,
                device_model = %(device_model)s,
                app_version = %(app_version)s,
                last_seen_at = %(last_seen_at)s
            WHERE id = %(id)s
        """

        batch_size = 1000
        updated = 0

        for i in range(0, len(user_ids), batch_size):
            batch_ids = user_ids[i : i + batch_size]
            updates: list[dict[str, Any]] = []

            for user_id in batch_ids:
                city = fake.city()
                region = fake.state()
                is_ios = random.random() < 0.3
                os_name = "iOS" if is_ios else "Android"
                device_model = random.choice(IOS_DEVICES if is_ios else ANDROID_DEVICES)

                updates.append(
                    {
                        "id": user_id,
                        "city": city,
                        "region": region,
                        "os_name": os_name,
                        "device_model": device_model,
                        "app_version": random.choice(APP_VERSIONS),
                        "last_seen_at": datetime.now(),
                    }
                )

            cursor.executemany(update_sql, updates)
            connection.commit()

            updated += len(batch_ids)
            print(f"Updated {updated}/{users_to_update} users...")

        print(f"\nCompleted! Updated {updated} users")

    except mysql.connector.Error as e:
        print(f"Error updating users: {e}")
        raise
    finally:
        if cursor:
            cursor.close()
        if connection and connection.is_connected():
            connection.close()


if __name__ == "__main__":
    # insert_users("mixpanel")
    update_random_users("mixpanel", percentage=0.15)
