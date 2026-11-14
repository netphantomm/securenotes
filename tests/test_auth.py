import re

import db


def test_valid_login_creates_session(client):
    password = "Training-password-123!"
    user_id = db.create_user("alice", password)

    page = client.get("/login")
    assert page.status_code == 200

    match = re.search(
        r'name="csrf_token"\s+value="([^"]+)"',
        page.get_data(as_text=True),
    )
    assert match is not None

    response = client.post(
        "/login",
        data={
            "username": "alice",
            "password": password,
            "csrf_token": match.group(1),
        },
    )

    assert response.status_code == 303
    assert response.headers["Location"] == "/"

    with client.session_transaction() as saved_session:
        assert saved_session.get("user_id") == user_id
