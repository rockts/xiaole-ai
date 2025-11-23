
import os
import sys
import psycopg2
from psycopg2.extras import RealDictCursor
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

def check_sleep_reminders():
    conn = get_db_connection()
    try:
        with conn.cursor(cursor_factory=RealDictCursor) as cur:
            print("--- Reminders with '睡觉' ---")
            cur.execute("""
                SELECT reminder_id, content, enabled, repeat, trigger_condition, created_at
                FROM reminders 
                WHERE content LIKE '%睡觉%'
            """)
            reminders = cur.fetchall()
            print(f"Found {len(reminders)} reminders:")
            for r in reminders:
                print(f"ID: {r['reminder_id']}")
                print(f"Content: {r['content']}")
                print(f"Enabled: {r['enabled']}")
                print(f"Repeat: {r['repeat']}")
                print(f"Condition: {r['trigger_condition']}")
                print(f"Created At: {r['created_at']}")
                print("-" * 30)

    except Exception as e:
        print(f"Error: {e}")
    finally:
        conn.close()

if __name__ == "__main__":
    check_sleep_reminders()
