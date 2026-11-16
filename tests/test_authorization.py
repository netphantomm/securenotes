import re
import db


def test_anonymous_user_is_redirected_to_login(client):
    response = client.get("/")

    assert response.status_code == 302
    assert response.headers["Location"] == "/login"

def test_bob_cannot_open_alice_note(logged_in_client, owner_id):
    page = logged_in_client.get("/")
    assert page.status_code == 200

    match = re.search(
        r'name="csrf_token"\s+value="([^"]+)"',
        page.get_data(as_text=True),
    )
    assert match is not None

    response = logged_in_client.post(
        "/notes",
        data={
            "title": "Alice private note",
            "body": "Alice private content",
            "csrf_token": match.group(1),
        },
    )
    assert response.status_code == 303
    note_id = db.get_notes(owner_id)[0]["id"]

    bob_id = db.create_user("bob", "Training-password-123!")
    bob_client = logged_in_client.application.test_client()
    with bob_client.session_transaction() as saved_session:
        saved_session["user_id"] = bob_id

    response = bob_client.get(f"/notes/{note_id}/edit")
    assert response.status_code == 404
    page = bob_client.get("/")
    assert page.status_code == 200
    assert "Alice private content" not in page.get_data(as_text=True)
