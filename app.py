from flask import Flask

app = Flask(__name__)

@app.get("/")
def index():
    return "SecureNotes: first version"
