
import os
import sys
import psycopg2
from dotenv import load_dotenv

# Add backend to path
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'backend'))

load_dotenv()


def get_db_connection():
    conn = psycopg2.connect(
        host=os.getenv('DB_HOST', '192.168.88.188'),
        port=os.getenv('DB_PORT', '5432'),
        database=os.getenv('DB_NAME', 'xiaole_ai'),
        user=os.getenv('DB_USER', 'xiaole_user'),
        password=os.getenv('DB_PASS', 'Xiaole2025User'),
        client_encoding='UTF8'
    )
    return conn


def delete_reminder():
    conn = get_db_connection()
    try:
        with conn.cursor() as cur:
            print("Deleting reminder 77...")
            cur.execute("DELETE FROM reminders WHERE reminder_id = 77")
            conn.commit()
            print("Reminder 77 deleted.")
    except Exception as e:
        print(f"Error: {e}")
    finally:
        conn.close()


if __name__ == "__main__":
    delete_reminder()
