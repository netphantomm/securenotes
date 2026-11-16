import db


def test_create_note(database, owner_id):
    db.create_note("Test title", "Test body", owner_id)

    notes = db.get_notes(owner_id)

    assert len(notes) == 1
    assert notes[0]["title"] == "Test title"

    # TODO: Assert that the saved body equals "Test body".
