import sqlite3
from uuid import uuid4

from app.core.config import settings
from app.core.security import hash_password


def init_db():
    connection = sqlite3.connect(settings.DATABASE_PATH)
    connection.row_factory = sqlite3.Row
    cursor = connection.cursor()
    cursor.execute("PRAGMA foreign_keys = ON")
    try:
        cursor.executescript(
            """
        CREATE TABLE IF NOT EXISTS Categories (
          category_id TEXT PRIMARY KEY,
          title TEXT NOT NULL UNIQUE
        );

        CREATE TABLE IF NOT EXISTS Statuses (
          status_id TEXT PRIMARY KEY,
          title TEXT NOT NULL UNIQUE
        );

        CREATE TABLE IF NOT EXISTS Users (
          user_id TEXT PRIMARY KEY,
          first_name TEXT NOT NULL,
          last_name TEXT NOT NULL,
          email TEXT NOT NULL UNIQUE,
          hashed_password TEXT NOT NULL,
          role TEXT NOT NULL CHECK(role IN ('admin', 'user', 'guest'))
        );

        CREATE TABLE IF NOT EXISTS Items (
          item_id TEXT PRIMARY KEY,
          title TEXT NOT NULL,
          description TEXT,
          created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
          updated_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
          category_id TEXT NULL,
          status_id TEXT NULL,
          user_id TEXT NOT NULL,
          FOREIGN KEY (category_id) REFERENCES Categories(category_id) ON DELETE SET NULL,
          FOREIGN KEY (status_id)   REFERENCES Statuses(status_id)   ON DELETE SET NULL,
          FOREIGN KEY (user_id) REFERENCES Users(user_id) ON DELETE CASCADE
        );
        """
        )
        hashed = hash_password(settings.ADMIN_PASSWORD)
        cursor.execute(
            """
            INSERT INTO Users (user_id, first_name, last_name, email, hashed_password, role)
            VALUES (?, ?, ?, ?, ?, 'admin')
            ON CONFLICT(email) DO NOTHING
            """,
            (str(uuid4()), "Admin", "User", settings.ADMIN_EMAIL, hashed),
        )
        connection.commit()

    except sqlite3.Error as e:
        connection.rollback()
        print(f"Database error: {e}")
    finally:
        connection.close()


# if __name__ == "__main__":
#     init_db()
