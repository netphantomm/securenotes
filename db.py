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

def delete_note(note_id):
    connection = sqlite3.connect(DB_PATH)
    try:
        cursor = connection.execute(
            "DELETE FROM notes WHERE id = ?",
            (note_id,),
        )
        connection.commit()
        return cursor.rowcount == 1
    finally:
        connection.close()


def get_note(note_id):
    connection = sqlite3.connect(DB_PATH)
    connection.row_factory = sqlite3.Row
    try:
        cursor = connection.execute(
            "SELECT id, title, body FROM notes WHERE id = ?",
            (note_id,),
        )
        note = cursor.fetchone()
        return note
    finally:
        connection.close()
def update_note(note_id, title, body):
    connection = sqlite3.connect(DB_PATH)
    try:
        cursor = connection.execute(
            "UPDATE notes SET title = ?, body = ? WHERE id = ?",
            (title, body, note_id,),
        )
        connection.commit()
        return cursor.rowcount == 1
    finally:
        connection.close()
