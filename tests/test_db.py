import db


def test_create_note(database):
    db.create_note("Test title", "Test body")

    notes = db.get_notes()

    assert len(notes) == 1
    assert notes[0]["title"] == "Test title"

    # TODO: Assert that the saved body equals "Test body".
