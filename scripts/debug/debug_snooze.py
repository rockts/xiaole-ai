import psycopg2
import json
import os
from datetime import datetime


def get_db_connection():
    return psycopg2.connect(
        host='192.168.88.188',
        port='5432',
        database='xiaole_ai',
        user='xiaole_user',
        password='Xiaole2025User',
        client_encoding='UTF8'
    )


def check_reminders():
    try:
        conn = get_db_connection()
        cur = conn.cursor()

        print("\n=== Checking Reminders ===")
        cur.execute(
            "SELECT reminder_id, content, trigger_condition, last_triggered, enabled FROM reminders WHERE user_id = 'default_user'")
        rows = cur.fetchall()

        for row in rows:
            rid, content, trigger, last, enabled = row
            print(f"ID: {rid}")
            print(f"Content: {content}")
            print(f"Trigger: {trigger}")
            print(f"Last Triggered: {last}")
            print(f"Enabled: {enabled}")
            print("-" * 20)

        conn.close()
    except Exception as e:
        print(f"Error: {e}")


if __name__ == "__main__":
    check_reminders()
