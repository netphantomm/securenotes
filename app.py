from flask import Flask, render_template
from db import get_notes
import os 
from flask_wtf.csrf import CSRFProtect
app = Flask(__name__)

app.config["SECRET_KEY"] = os.environ["SECRET_KEY"]
CSRFProtect

@app.get("/")
def index():
    notes = get_notes()
    return render_template("index.html", title="SecureNotes", notes=notes)

@app.get("/health")
def health():
    return "ok"