import sqlite3
import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
"""Checks that the database file location matches the db.py location"""

db_name = os.path.join(BASE_DIR, "habit_tracker.db")

def get_db_connection() -> sqlite3.Connection:

    """Establishes connection with the database"""

    conn = sqlite3.connect(db_name)
    conn.execute("pragma foreign_key = ON;")
    return conn


def init_db():

    """Creates databases 'users', 'habits', and 'completions' for storage of user, habits,
    and completion record's data"""

    try:
        with get_db_connection() as conn:
            cur = conn.cursor()

            cur.execute("""CREATE TABLE IF NOT EXISTS users(
                            id INTEGER PRIMARY KEY AUTOINCREMENT,
                            username TEXT UNIQUE NOT NULL,
                            password_hash TEXT NOT NULL
                        )"""
                        )
            
            cur.execute("""CREATE TABLE IF NOT EXISTS habits (
                            id INTEGER PRIMARY KEY AUTOINCREMENT,
                            user_id INTEGER NOT NULL,
                            name TEXT NOT NULL,
                            description TEXT,
                            periodicity TEXT NOT NULL CHECK (periodicity IN ('daily', 'weekly')),
                            start_date TEXT NOT NULL,
                            end_date TEXT NOT NULL,
                            FOREIGN KEY (user_id) REFERENCES users (id)
                        )"""
                        )
            
            cur.execute("""CREATE TABLE IF NOT EXISTS completions (
                            id INTEGER PRIMARY KEY AUTOINCREMENT,
                            habit_id INTEGER NOT NULL,
                            completion_date TEXT NOT NULL,
                            FOREIGN KEY (habit_id) REFERENCES habits (id) ON DELETE CASCADE
                        )"""
                        )
            conn.commit()
            
    except sqlite3.Error as e:

        print(f"An error occured: {e}")
        raise e