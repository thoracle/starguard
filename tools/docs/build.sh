#!/bin/sh
# Rebuild docs/requirements/ from the running game. Needs the game answering at STARGUARD_URL (default http://127.0.0.1:5079/).
set -e
HERE=$(cd "$(dirname "$0")" && pwd)
PY=${PYTHON:-"$HERE/../../.venv/bin/python"}
"$PY" "$HERE/shots.py"
"$PY" "$HERE/mkreq.py"
"$PY" "$HERE/mkpage.py"
"$PY" "$HERE/look.py"
echo "built docs/requirements/index.html; check tools/out/look_*.png"
