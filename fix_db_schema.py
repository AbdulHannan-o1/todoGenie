#!/usr/bin/env python3
"""
Script to fix the database schema by adding missing columns and fixing incorrect ones.
This addresses the issue where the migration didn't fully apply the required changes.
"""
import os
from sqlalchemy import create_engine, text

# Get database URL from environment or use default
DATABASE_URL = os.getenv('DATABASE_URL', 'postgresql://postgres:postgres@todogenie-postgresql:5432/postgres')

def fix_database_schema():
    try:
        engine = create_engine(DATABASE_URL)

        with engine.connect() as conn:
            # Check if reminder_time column exists
            result = conn.execute(text("""
                SELECT column_name
                FROM information_schema.columns
                WHERE table_name = 'task' AND column_name = 'reminder_time'
            """))

            if not result.fetchone():
                print("Adding missing reminder_time column...")
                conn.execute(text("ALTER TABLE task ADD COLUMN reminder_time TIMESTAMP WITH TIME ZONE;"))
                conn.commit()
                print("Added reminder_time column successfully.")
            else:
                print("reminder_time column already exists.")

            # Check if parent_task_id column exists
            result = conn.execute(text("""
                SELECT column_name
                FROM information_schema.columns
                WHERE table_name = 'task' AND column_name = 'parent_task_id'
            """))

            if not result.fetchone():
                print("Adding missing parent_task_id column...")
                conn.execute(text("ALTER TABLE task ADD COLUMN parent_task_id UUID REFERENCES task(id);"))
                conn.commit()
                print("Added parent_task_id column successfully.")
            else:
                print("parent_task_id column already exists.")

            # Check if recurrence_pattern column exists (the correct name)
            result = conn.execute(text("""
                SELECT column_name
                FROM information_schema.columns
                WHERE table_name = 'task' AND column_name = 'recurrence_pattern'
            """))

            if not result.fetchone():
                # Check if the incorrectly named 'recurrence' column exists
                result = conn.execute(text("""
                    SELECT column_name
                    FROM information_schema.columns
                    WHERE table_name = 'task' AND column_name = 'recurrence'
                """))

                if result.fetchone():
                    print("Renaming 'recurrence' column to 'recurrence_pattern'...")
                    conn.execute(text("ALTER TABLE task RENAME COLUMN recurrence TO recurrence_pattern;"))
                    conn.commit()
                    print("Renamed 'recurrence' to 'recurrence_pattern' successfully.")
                else:
                    print("Adding missing recurrence_pattern column...")
                    conn.execute(text("ALTER TABLE task ADD COLUMN recurrence_pattern JSON;"))
                    conn.commit()
                    print("Added recurrence_pattern column successfully.")
            else:
                print("recurrence_pattern column already exists.")

        print("Database schema fix completed successfully!")

    except Exception as e:
        print(f"Error fixing database schema: {str(e)}")
        raise

if __name__ == "__main__":
    fix_database_schema()