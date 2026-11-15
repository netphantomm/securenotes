import argparse
import sqlite3
from pathlib import Path


def migrate(database_path, owner_id):
    database_uri = Path(database_path).resolve().as_uri() + "?mode=rw"
    connection = sqlite3.connect(database_uri, uri=True)

    try:
        connection.execute("PRAGMA foreign_keys = ON")
        connection.execute("BEGIN IMMEDIATE")

        columns = [
            row[1]
            for row in connection.execute("PRAGMA table_info(notes)")
        ]
        if columns != ["id", "title", "body"]:
            raise RuntimeError("Unexpected notes schema. Migration cancelled.")

        owner = connection.execute(
            "SELECT id FROM users WHERE id = ?",
            (owner_id,),
        ).fetchone()

        if owner is None:
            raise RuntimeError("Selected owner does not exist.")

        original_notes = connection.execute(
            "SELECT id, title, body FROM notes ORDER BY id"
        ).fetchall()

        connection.execute("""
            CREATE TABLE notes_new (
                id INTEGER PRIMARY KEY,
                owner_id INTEGER NOT NULL REFERENCES users(id),
                title TEXT NOT NULL,
                body TEXT NOT NULL
            )
        """)

        connection.execute(
            """
            INSERT INTO notes_new (id, owner_id, title, body)
            SELECT id, ?, title, body FROM notes
            """,
            (owner_id,),
        )

        copied_notes = connection.execute(
            "SELECT id, title, body FROM notes_new ORDER BY id"
        ).fetchall()

        if original_notes != copied_notes:
            raise RuntimeError("Note contents differ. Migration cancelled.")

        connection.execute("DROP TABLE notes")
        connection.execute("ALTER TABLE notes_new RENAME TO notes")

        if connection.execute("PRAGMA foreign_key_check").fetchall():
            raise RuntimeError("Foreign key validation failed.")

        connection.commit()
    except Exception:
        connection.rollback()
        raise
    finally:
        connection.close()

    print(f"Migrated {len(original_notes)} notes to owner {owner_id}.")
    print(f"Database: {Path(database_path).resolve()}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--database", required=True)
    parser.add_argument("--owner-id", type=int, required=True)
    args = parser.parse_args()

    migrate(args.database, args.owner_id)
