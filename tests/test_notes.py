import re

import db


def test_invalid_edit_keeps_original_note(client):
    db.create_note("Original title", "Original body")
    note_id = db.get_notes()[0]["id"]

    page = client.get(f"/notes/{note_id}/edit")
    assert page.status_code == 200

    match = re.search(
        r'name="csrf_token"\s+value="([^"]+)"',
        page.get_data(as_text=True),
    )
    assert match is not None

    response = client.post(
        f"/notes/{note_id}/edit",
        data={
            "title": "   ",
            "body": "Changed body",
            "csrf_token": match.group(1),
        },
    )

    assert response.status_code == 400
    assert b"Title must contain" in response.data

    saved_note = db.get_note(note_id)
    assert saved_note is not None
    assert saved_note["title"] == "Original title"

    assert saved_note["body"] == "Original body"
def test_valid_edit_updates_note(client):
    db.create_note("Original title", "Original body")
    note_id = db.get_notes()[0]["id"]

    page = client.get(f"/notes/{note_id}/edit")
    assert page.status_code == 200

    match = re.search(
        r'name="csrf_token"\s+value="([^"]+)"',
        page.get_data(as_text=True),
    )
    assert match is not None

    response = client.post(
        f"/notes/{note_id}/edit",
        data={
            "title": "Updated title",
            "body": "Updated body",
            "csrf_token": match.group(1),
        },
    )

    assert response.status_code == 303

    saved_note = db.get_note(note_id)
    assert saved_note is not None
    assert saved_note["title"] == "Updated title"
    assert saved_note["body"] == "Updated body"
    assert len(db.get_notes()) == 1

def test_edit_without_csrf_keeps_original_note(client):
    db.create_note("Original title", "Original body")
    note_id = db.get_notes()[0]["id"]

    response = client.post(
        f"/notes/{note_id}/edit",
        data={
            "title": "Changed title",
            "body": "Changed body",
        },
    )

    assert response.status_code == 400
    assert b"The CSRF token is missing." in response.data

    saved_note = db.get_note(note_id)
    assert saved_note is not None
    assert saved_note["title"] == "Original title"

    assert saved_note["body"] == "Original body"
