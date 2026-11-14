import re

from werkzeug.security import check_password_hash
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

def test_registration_creates_user(client):
    password = "qwerty123456"

    page = client.get("/register")
    assert page.status_code == 200

    match = re.search(
        r'name="csrf_token"\s+value="([^"]+)"',
        page.get_data(as_text=True),
    )
    assert match is not None

    response = client.post(
        "/register",
        data={
            "username": "new_user",
            "password": password,
            "password_confirm": password,
            "csrf_token": match.group(1),
        },
    )

    assert response.status_code == 303
    assert response.headers["Location"] == "/login"

    user = db.get_user_by_username("new_user")
    assert user is not None
    assert check_password_hash(user["password_hash"], password)


    assert client.get("/").status_code == 200
def test_logout_clears_session(client):
    user_id = db.create_user("alice", "Training-password-123!")

    with client.session_transaction() as saved_session:
        saved_session["user_id"] = user_id

    page = client.get("/")
    assert page.status_code == 200

    match = re.search(
        r'name="csrf_token"\s+value="([^"]+)"',
        page.get_data(as_text=True),
    )
    assert match is not None

    response = client.post(
        "/logout",
        data={"csrf_token": match.group(1)},
    )

    assert response.status_code == 303
    assert response.headers["Location"] == "/login"

    with client.session_transaction() as saved_session:
        assert "user_id" not in saved_session
