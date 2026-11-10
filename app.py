from flask import Flask, render_template
from db import get_notes

app = Flask(__name__)

@app.get("/")
def index():
    notes = get_notes()
    return render_template("index.html", title="SecureNotes", notes=notes)

@app.get("/health")
def health():
    return "ok"