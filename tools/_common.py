"""Shared setup for the browser scripts in tools/.

Importing this module:
  - finds a headless Chromium (Playwright's download, else Playwright's default)
  - reads the game URL from STARGUARD_URL (default: the local service on port 5079)
  - moves into tools/out/ so screenshots and intermediate files land there
"""
import glob
import os

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DOCS = os.path.join(ROOT, "docs", "requirements")
OUT = os.path.join(ROOT, "tools", "out")
URL = os.environ.get("STARGUARD_URL", "http://127.0.0.1:5079/")

_shells = sorted(glob.glob(os.path.expanduser("~/.cache/ms-playwright/chromium_headless_shell-*/*/chrome-headless-shell")))
EXE = _shells[-1] if _shells else None   # None lets Playwright use its own default browser

os.makedirs(OUT, exist_ok=True)
os.chdir(OUT)
