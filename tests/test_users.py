import sqlite3

from werkzeug.security import check_password_hash

import db


def test_create_user_stores_password_hash(database):
    password = "Training-password-123!"
    user_id = db.create_user("alice", password)

    assert type(user_id) is int

    connection = sqlite3.connect(database)
    connection.row_factory = sqlite3.Row

    try:
        user = connection.execute(
            "SELECT username, password_hash FROM users WHERE id = ?",
            (user_id,),
        ).fetchone()
    finally:
        connection.close()

    assert user is not None
    assert user["username"] == "alice"
    assert user["password_hash"] != password
    assert check_password_hash(user["password_hash"], password)

    assert not check_password_hash(user["password_hash"], "Wrong-password-123!")