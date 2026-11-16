import re
import db
import pytest

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


@pytest.mark.parametrize("action", ["edit", "delete"])
def test_bob_cannot_modify_alice_note(logged_in_client, owner_id, action):
    db.create_note("Alice title", "Alice body", owner_id)
    note_id = db.get_notes(owner_id)[0]["id"]

    bob_id = db.create_user("bob", "Training-password-123!")
    bob_client = logged_in_client.application.test_client()

    with bob_client.session_transaction() as saved_session:
        saved_session["user_id"] = bob_id

    page = bob_client.get("/")
    assert page.status_code == 200

    match = re.search(
        r'name="csrf_token"\s+value="([^"]+)"',
        page.get_data(as_text=True),
    )
    assert match is not None

    data = {"csrf_token": match.group(1)}

    if action == "edit":
        data["title"] = "Changed by Bob"
        data["body"] = "Changed body"

    response = bob_client.post(
        f"/notes/{note_id}/{action}",
        data=data,
    )

    assert response.status_code == 404

    saved_note = db.get_note(note_id, owner_id)
    assert saved_note is not None
    assert saved_note["title"] == "Alice title"
    assert saved_note["body"] == "Alice body"

def test_owner_can_edit_and_delete_selected_note(logged_in_client, owner_id):
    db.create_note("Keep title", "Keep body", owner_id)
    db.create_note("Target title", "Target body", owner_id)

    notes = db.get_notes(owner_id)
    keep_id = notes[0]["id"]
    target_id = notes[1]["id"]

    # Get a CSRF token from the owner's edit form.
    page = logged_in_client.get(f"/notes/{target_id}/edit")
    assert page.status_code == 200

    match = re.search(
        r'name="csrf_token"\s+value="([^"]+)"',
        page.get_data(as_text=True),
    )
    assert match is not None
    csrf_token = match.group(1)

    # Edit the selected note.
    response = logged_in_client.post(
        f"/notes/{target_id}/edit",
        data={
            "title": "Updated title",
            "body": "Updated body",
            "csrf_token": csrf_token,
        },
    )
    assert response.status_code == 303

    updated_note = db.get_note(target_id, owner_id)
    assert updated_note is not None
    assert updated_note["title"] == "Updated title"
    assert updated_note["body"] == "Updated body"

    # Delete the selected note using the same session.
    response = logged_in_client.post(
        f"/notes/{target_id}/delete",
        data={"csrf_token": csrf_token},
    )
    assert response.status_code == 303
    assert db.get_note(target_id, owner_id) is None

    # Verify that the other note remains unchanged.
    remaining_notes = db.get_notes(owner_id)
    assert len(remaining_notes) == 1
    assert remaining_notes[0]["id"] == keep_id
    assert remaining_notes[0]["title"] == "Keep title"
    assert remaining_notes[0]["body"] == "Keep body"
