"""Step 4: render docs/requirements/index.html and screenshot each annotated figure into tools/out/look_*.png,
so the callout pins can be checked by eye against the elements they point at.
"""
import os, sys; sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..'))
from _common import EXE as exe, DOCS
from playwright.sync_api import sync_playwright
with sync_playwright() as p:
    b = p.chromium.launch(executable_path=exe)
    pg = b.new_page(viewport={'width': 1120, 'height': 800}, device_scale_factor=1.5)
    errs = []; pg.on('pageerror', lambda e: errs.append(str(e)))
    pg.goto('file://' + os.path.join(DOCS, 'index.html')); pg.wait_for_timeout(1200)
    for k, name in {'c': 'flight', 't': 'targeting', 'k': 'comms', 'm': 'nav'}.items():
        pg.locator('#shot-' + k).screenshot(path='look_' + name + '.png')
    print(errs or 'ok'); b.close()
