import os
from flask import Flask, abort, redirect, render_template, request, url_for, session, url_for
from flask_wtf.csrf import CSRFProtect
from werkzeug.security import check_password_hash
from db import create_note, delete_note, get_note, get_notes, get_user_by_username, update_note
from sqlite3 import IntegrityError

from db import (
    create_note,
    create_user,
    delete_note,
    get_note,
    get_notes,
    get_user_by_username,
    update_note,
)

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


@app.get("/login")
def login_view():
    return render_template("login.html")

@app.post("/notes/<int:note_id>/edit")
def update_note_view(note_id):
    title = request.form.get("title", "").strip()
    body = request.form.get("body", "").strip()

    if not 1 <= len(title) <= 120:
        abort(400, description="Title must contain 1 to 120 characters.")

    if not 1 <= len(body) <= 5000:
        abort(400, description="Body must contain 1 to 5000 characters.")

    updated = update_note(note_id, title, body)

    if not updated:
        abort(404, description="Note not found.")

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

@app.get("/notes/<int:note_id>/edit")
def edit_note_view(note_id):
    note = get_note(note_id)
    if note is None:
        abort(404, description="Note not found.")
    return render_template("edit.html", note=note)


@app.post("/login")
def authenticate_view():
    username = request.form.get("username", "").strip()
    password = request.form.get("password", "")

    if not 1 <= len(username) <= 32 or not 1 <= len(password) <= 128:
        abort(401, description="Invalid username or password.")

    user = get_user_by_username(username)

    if user is None or not check_password_hash(user["password_hash"], password):
        abort(401, description="Invalid username or password.")

    session.clear()
    session["user_id"] = user["id"]

    return redirect(url_for("index"), code=303)


@app.get("/register")
def register_view():
    return render_template("register.html")

@app.post("/register")
def register_user_view():
    username = request.form.get("username", "").strip()
    password = request.form.get("password", "")
    password_confirm = request.form.get("password_confirm", "")

    if not 3 <= len(username) <= 32:
        abort(400, description="Username must contain 3 to 32 characters.")

    if not 12 <= len(password) <= 128:
        abort(400, description="Password must contain 12 to 128 characters.")

    if password != password_confirm:
        abort(400, description="Passwords do not match.")

    try:
        create_user(username, password)
    except IntegrityError:
        abort(409, description="Username is already taken.")

    return redirect(url_for("login_view"), code=303)