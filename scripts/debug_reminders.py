import os
import sys
import psycopg2
from psycopg2.extras import RealDictCursor
from dotenv import load_dotenv
import json

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


def check_reminders():
    conn = get_db_connection()
    try:
        with conn.cursor(cursor_factory=RealDictCursor) as cur:
            print("--- Active Reminders (enabled=true) ---")
            cur.execute("""
                SELECT reminder_id, content, enabled, repeat, repeat_interval, 
                       last_triggered, trigger_condition, trigger_count
                FROM reminders 
                WHERE enabled = true
            """)
            reminders = cur.fetchall()
            for r in reminders:
                print(f"ID: {r['reminder_id']}")
                print(f"Content: {r['content']}")
                print(f"Enabled: {r['enabled']}")
                print(f"Repeat: {r['repeat']}")
                print(f"Interval: {r['repeat_interval']}")
                print(f"Last Triggered: {r['last_triggered']}")
                print(f"Trigger Count: {r['trigger_count']}")
                print(f"Condition: {r['trigger_condition']}")
                print("-" * 30)

            print("\n--- Recent History (Last 5) ---")
            cur.execute("""
                SELECT * FROM reminder_history 
                ORDER BY triggered_at DESC LIMIT 5
            """)
            history = cur.fetchall()
            for h in history:
                print(
                    f"ID: {h['history_id']}, ReminderID: {h['reminder_id']}, Time: {h['triggered_at']}")

    except Exception as e:
        print(f"Error: {e}")
    finally:
        conn.close()


if __name__ == "__main__":
    check_reminders()
