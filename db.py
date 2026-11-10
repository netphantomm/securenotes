import sqlite3
from pathlib import Path

DB_PATH = Path(__file__).resolve().parent / "instance" / "database.db"

def get_notes():
    connection = sqlite3.connect(DB_PATH)
    connection.row_factory = sqlite3.Row
    try:
        cursor = connection.execute("SELECT id, title, body FROM notes;")
        notes = cursor.fetchall()
        return notes
    finally:
        connection.close()
def create_note(title, body):
    connection = sqlite3.connect(DB_PATH)
    try:
        connection.execute(
            "INSERT INTO notes (title, body) VALUES (?, ?)",
            (title, body)
        )
        connection.commit()
    finally:
        connection.close()
