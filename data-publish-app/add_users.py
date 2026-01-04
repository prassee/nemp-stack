import random
import uuid
from datetime import datetime, timedelta

import mysql.connector

from ddl import get_connection

# Indian male first names
MALE_FIRST_NAMES = [
    "Aarav",
    "Vivaan",
    "Aditya",
    "Vihaan",
    "Arjun",
    "Sai",
    "Reyansh",
    "Ayaan",
    "Krishna",
    "Ishaan",
    "Shaurya",
    "Atharva",
    "Advik",
    "Pranav",
    "Advaith",
    "Aarush",
    "Kabir",
    "Ritvik",
    "Anirudh",
    "Dhruv",
    "Harsh",
    "Karthik",
    "Nikhil",
    "Rohan",
    "Sahil",
    "Tanish",
    "Yash",
    "Arnav",
    "Darsh",
    "Dev",
    "Gaurav",
    "Hemant",
    "Jayesh",
    "Kunal",
    "Lakshya",
    "Manish",
    "Naveen",
    "Om",
    "Parth",
    "Rajat",
    "Siddharth",
    "Tushar",
    "Uday",
    "Varun",
    "Vikram",
    "Ankit",
    "Bharat",
    "Chirag",
    "Deepak",
    "Eshan",
]

# Indian female first names
FEMALE_FIRST_NAMES = [
    "Aadhya",
    "Diya",
    "Pihu",
    "Prisha",
    "Ananya",
    "Fatima",
    "Ira",
    "Aanya",
    "Myra",
    "Sara",
    "Aarohi",
    "Anika",
    "Kavya",
    "Riya",
    "Kiara",
    "Siya",
    "Avni",
    "Ishita",
    "Saanvi",
    "Pari",
    "Meera",
    "Nisha",
    "Pooja",
    "Shreya",
    "Tanvi",
    "Aditi",
    "Bhavna",
    "Charvi",
    "Divya",
    "Ekta",
    "Gauri",
    "Harini",
    "Isha",
    "Jyoti",
    "Komal",
    "Lavanya",
    "Mahi",
    "Neha",
    "Ojasvi",
    "Pallavi",
    "Radha",
    "Sakshi",
    "Tara",
    "Uma",
    "Vaishnavi",
    "Yamini",
    "Zara",
    "Aishwarya",
    "Bhakti",
    "Chhaya",
]

# Indian last names
LAST_NAMES = [
    "Sharma",
    "Verma",
    "Gupta",
    "Singh",
    "Kumar",
    "Patel",
    "Shah",
    "Mehta",
    "Joshi",
    "Rao",
    "Reddy",
    "Nair",
    "Menon",
    "Pillai",
    "Iyer",
    "Iyengar",
    "Mukherjee",
    "Banerjee",
    "Chatterjee",
    "Das",
    "Ghosh",
    "Bose",
    "Sen",
    "Agarwal",
    "Jain",
    "Kapoor",
    "Malhotra",
    "Chopra",
    "Khanna",
    "Bhatia",
    "Sethi",
    "Arora",
    "Garg",
    "Mittal",
    "Saxena",
    "Mishra",
    "Pandey",
    "Tiwari",
    "Dubey",
    "Shukla",
    "Srivastava",
    "Tripathi",
    "Chauhan",
    "Rathore",
    "Yadav",
    "Thakur",
    "Desai",
    "Patil",
    "Kulkarni",
    "Deshpande",
]

# Indian cities with regions
INDIAN_CITIES = [
    ("Mumbai", "Maharashtra"),
    ("Delhi", "Delhi"),
    ("Bangalore", "Karnataka"),
    ("Hyderabad", "Telangana"),
    ("Chennai", "Tamil Nadu"),
    ("Kolkata", "West Bengal"),
    ("Pune", "Maharashtra"),
    ("Ahmedabad", "Gujarat"),
    ("Jaipur", "Rajasthan"),
    ("Lucknow", "Uttar Pradesh"),
    ("Kanpur", "Uttar Pradesh"),
    ("Nagpur", "Maharashtra"),
    ("Indore", "Madhya Pradesh"),
    ("Thane", "Maharashtra"),
    ("Bhopal", "Madhya Pradesh"),
    ("Visakhapatnam", "Andhra Pradesh"),
    ("Patna", "Bihar"),
    ("Vadodara", "Gujarat"),
    ("Ghaziabad", "Uttar Pradesh"),
    ("Ludhiana", "Punjab"),
    ("Agra", "Uttar Pradesh"),
    ("Nashik", "Maharashtra"),
    ("Faridabad", "Haryana"),
    ("Meerut", "Uttar Pradesh"),
    ("Rajkot", "Gujarat"),
    ("Varanasi", "Uttar Pradesh"),
    ("Srinagar", "Jammu and Kashmir"),
    ("Aurangabad", "Maharashtra"),
    ("Dhanbad", "Jharkhand"),
    ("Amritsar", "Punjab"),
    ("Allahabad", "Uttar Pradesh"),
    ("Ranchi", "Jharkhand"),
    ("Coimbatore", "Tamil Nadu"),
    ("Jabalpur", "Madhya Pradesh"),
    ("Gwalior", "Madhya Pradesh"),
    ("Vijayawada", "Andhra Pradesh"),
    ("Jodhpur", "Rajasthan"),
    ("Madurai", "Tamil Nadu"),
    ("Raipur", "Chhattisgarh"),
    ("Kota", "Rajasthan"),
    ("Chandigarh", "Chandigarh"),
    ("Guwahati", "Assam"),
    ("Solapur", "Maharashtra"),
    ("Hubli", "Karnataka"),
    ("Tiruchirappalli", "Tamil Nadu"),
    ("Bareilly", "Uttar Pradesh"),
    ("Mysore", "Karnataka"),
    ("Tiruppur", "Tamil Nadu"),
    ("Gurgaon", "Haryana"),
    ("Noida", "Uttar Pradesh"),
]

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
    first_name = random.choice(MALE_FIRST_NAMES if is_male else FEMALE_FIRST_NAMES)
    last_name = random.choice(LAST_NAMES)
    full_name = f"{first_name} {last_name}"

    user_id = str(uuid.uuid4())
    email = f"{first_name.lower()}.{last_name.lower()}{random.randint(1, 999)}@{'gmail.com' if random.random() < 0.7 else 'yahoo.com'}"
    phone = f"+91{random.randint(7000000000, 9999999999)}"

    city, region = random.choice(INDIAN_CITIES)

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
        total_users = cursor.fetchone()[0]
        users_to_update = int(total_users * percentage)

        print(
            f"Total users: {total_users}, updating {users_to_update} ({percentage * 100:.0f}%)"
        )

        # Get random user IDs to update
        cursor.execute(
            "SELECT id FROM users ORDER BY RAND() LIMIT %s", (users_to_update,)
        )
        user_ids = [row[0] for row in cursor.fetchall()]

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
            updates = []

            for user_id in batch_ids:
                city, region = random.choice(INDIAN_CITIES)
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
    insert_users("mixpanel")
