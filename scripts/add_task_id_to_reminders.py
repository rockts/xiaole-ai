import psycopg2
import os
from dotenv import load_dotenv

load_dotenv()


def migrate():
    conn = psycopg2.connect(
        host=os.getenv('DB_HOST', '192.168.88.188'),
        port=os.getenv('DB_PORT', '5432'),
        database=os.getenv('DB_NAME', 'xiaole_ai'),
        user=os.getenv('DB_USER', 'xiaole_user'),
        password=os.getenv('DB_PASS', 'Xiaole2025User'),
        client_encoding='UTF8'
    )

    try:
        with conn.cursor() as cur:
            # Check if column exists
            cur.execute("""
                SELECT column_name 
                FROM information_schema.columns 
                WHERE table_name='reminders' AND column_name='task_id';
            """)
            if cur.fetchone():
                print("Column task_id already exists in reminders table.")
            else:
                print("Adding task_id column to reminders table...")
                cur.execute("""
                    ALTER TABLE reminders 
                    ADD COLUMN task_id INTEGER REFERENCES tasks(id) ON DELETE CASCADE;
                """)
                print("Column added successfully.")

            conn.commit()
            print("Migration completed.")

    except Exception as e:
        conn.rollback()
        print(f"Migration failed: {e}")
    finally:
        conn.close()


if __name__ == "__main__":
    migrate()
