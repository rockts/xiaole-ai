import asyncio
import os
import sys
from dotenv import load_dotenv
import psycopg2
from psycopg2.extras import RealDictCursor

# Add project root to sys.path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

load_dotenv()


def list_all_reminders():
    conn = psycopg2.connect(
        host=os.getenv('DB_HOST', '192.168.88.188'),
        port=os.getenv('DB_PORT', '5432'),
        database=os.getenv('DB_NAME', 'xiaole_ai'),
        user=os.getenv('DB_USER', 'xiaole_user'),
        password=os.getenv('DB_PASS', 'Xiaole2025User'),
        client_encoding='UTF8'
    )

    try:
        with conn.cursor(cursor_factory=RealDictCursor) as cur:
            print("\n--- All Reminders in DB ---")
            cur.execute("SELECT * FROM reminders ORDER BY created_at DESC")
            reminders = cur.fetchall()
            for r in reminders:
                print(
                    f"ID: {r['reminder_id']}, User: {r['user_id']}, Type: {r['reminder_type']}, Enabled: {r['enabled']}, Content: {r['content']}")
                print(f"   Trigger: {r['trigger_condition']}")
                print(f"   Last Triggered: {r['last_triggered']}")
                print("-" * 30)

            print(f"\nTotal count: {len(reminders)}")

    except Exception as e:
        print(f"Error: {e}")
    finally:
        conn.close()


if __name__ == "__main__":
    list_all_reminders()
