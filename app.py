import os
from flask import Flask, abort, redirect, render_template, request, url_for
from flask_wtf.csrf import CSRFProtect
from db import create_note, get_notes, delete_note

app = Flask(__name__)

app.config["SECRET_KEY"] = os.environ["SECRET_KEY"]
CSRFProtect(app)

@app.get("/")
def index():
    notes = get_notes()
    return render_template("index.html", title="SecureNotes", notes=notes)
@app.post("/notes")
def create_note_view():
    title = request.form.get("title", "").strip()
    body = request.form.get("body", "").strip()
    if not 1 <= len(title) <= 120:
        abort(400, description="Title must contain 1 to 120 characters.")
    if not 1 <= len(body) <= 5000:
        abort(400, description="Body must contain 1 to 5000 characters.")
    create_note(title, body)
    return redirect(url_for("index"), code=303)

@app.get("/health")
def health():
    return "ok"

@app.post("/notes/<int:note_id>/delete")
def delete_note_view(note_id):
    deleted = delete_note(note_id)
    if not deleted:
        abort(404, description="Note not found.")
    return redirect(url_for("index"), code=303)
