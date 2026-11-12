import sqlite3
from pathlib import Path
import secrets
import pytest

import db


@pytest.fixture
def database(tmp_path, monkeypatch):
    db_path = tmp_path / "test.db"
    monkeypatch.setattr(db, "DB_PATH", db_path)

    schema_path = Path(__file__).resolve().parents[1] / "schema.sql"

    connection = sqlite3.connect(db_path)
    try:
        connection.executescript(schema_path.read_text(encoding="utf-8"))
    finally:
        connection.close()

    return db_path

@pytest.fixture
def client(database, monkeypatch):
    secret_key = secrets.token_hex(32)
    monkeypatch.setenv("SECRET_KEY", secret_key)

    from app import app

    monkeypatch.setitem(app.config, "TESTING", True)
    monkeypatch.setitem(app.config, "SECRET_KEY", secret_key)

    return app.test_client()