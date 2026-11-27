"""STARGUARD prototype server: serves the one-page game.

Run:  .venv/bin/python app.py      (then open http://<this-machine-ip>:5000 on the phone)
"""
import os

from flask import Flask, send_from_directory

BASE = os.path.dirname(os.path.abspath(__file__))

app = Flask(__name__, static_folder=None)
app.config["MAX_CONTENT_LENGTH"] = 4096  # nothing here accepts uploads; refuse large bodies outright


@app.get("/")
def index():
    resp = send_from_directory(BASE, "index.html")
    resp.headers["Cache-Control"] = "no-store"  # always pick up edits while prototyping
    return resp


if __name__ == "__main__":
    app.run(host=os.environ.get("HOST", "0.0.0.0"), port=int(os.environ.get("PORT", 5000)), debug=False)
