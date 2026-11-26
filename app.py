"""STARGUARD prototype server: serves the one-page game and a tiny high-score API.

Run:  .venv/bin/python app.py      (then open http://<this-machine-ip>:5000 on the phone)
"""
import json
import os
import re
import threading
import time

from flask import Flask, jsonify, request, send_from_directory

BASE = os.path.dirname(os.path.abspath(__file__))
SCORES = os.path.join(BASE, "scores.json")
KEEP = 50

app = Flask(__name__, static_folder=None)
lock = threading.Lock()


def load_scores():
    try:
        with open(SCORES) as f:
            data = json.load(f)
        # keep only well-formed rows so one bad entry cannot break sorting
        return [s for s in data if isinstance(s, dict) and isinstance(s.get("score"), int)] if isinstance(data, list) else []
    except (OSError, ValueError):
        return []


def save_scores(scores):
    tmp = SCORES + ".tmp"
    with open(tmp, "w") as f:
        json.dump(scores, f)
    os.replace(tmp, SCORES)


@app.get("/")
def index():
    resp = send_from_directory(BASE, "index.html")
    resp.headers["Cache-Control"] = "no-store"  # always pick up edits while prototyping
    return resp


@app.get("/api/scores")
def get_scores():
    return jsonify(load_scores()[:10])


@app.post("/api/scores")
def post_score():
    body = request.get_json(silent=True)
    if not isinstance(body, dict):
        return jsonify(error="expected a JSON object"), 400
    name = re.sub(r"[^A-Z0-9]", "", str(body.get("name", "")).upper())[:3] or "ACE"
    try:
        score = int(body.get("score", 0))
        wave = int(body.get("wave", 1))
    except (TypeError, ValueError, OverflowError):
        return jsonify(error="bad score"), 400
    if not (0 <= score <= 10_000_000 and 0 <= wave <= 999):
        return jsonify(error="out of range"), 400
    with lock:
        scores = load_scores()
        scores.append({"name": name, "score": score, "wave": wave, "t": int(time.time())})
        scores.sort(key=lambda s: -s["score"])
        save_scores(scores[:KEEP])
    return jsonify(scores[:10])


if __name__ == "__main__":
    app.run(host=os.environ.get("HOST", "0.0.0.0"), port=int(os.environ.get("PORT", 5000)), debug=False)
