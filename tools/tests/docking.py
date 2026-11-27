"""Docking: the FASTER button reads LAUNCH and flashes once serviced, SLOWER dims, and a tap launches.
"""
import glob, os
from playwright.sync_api import sync_playwright
import sys; sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..'))
from _common import EXE as exe, URL, DOCS, OUT, ROOT
with sync_playwright() as p:
    b = p.chromium.launch(executable_path=exe, args=['--use-gl=swiftshader','--enable-unsafe-swiftshader','--ignore-gpu-blocklist'])
    errs=[]
    pg = b.new_page(viewport={'width':844,'height':390}, device_scale_factor=3, has_touch=True)
    pg.on('pageerror', lambda e: errs.append('PAGEERR: '+str(e)))
    pg.goto(URL); pg.wait_for_timeout(1000)
    pg.tap('#bStart'); pg.wait_for_timeout(500)
    print('flying:', pg.inner_text('#bBoost').replace('\n',' | '))
    pg.evaluate("SG.S.dockCD=0; SG.ship.position.set(0,-8,-300); SG.S.energy=60")
    pg.wait_for_function("SG.S.docked", timeout=30000); pg.wait_for_timeout(600)
    print('flashing:', pg.evaluate("document.getElementById('bBoost').classList.contains('alert')"), 'docked:', pg.inner_text('#bBoost').replace('\n',' | '), '| slower dimmed:', pg.evaluate("document.getElementById('bBrake').classList.contains('off')"))
    pg.screenshot(path='dock_btn.png', clip={'x':580,'y':205,'width':264,'height':185})
    pg.wait_for_timeout(1500); pg.tap('#bBoost'); pg.wait_for_timeout(300)
    print('after tapping LAUNCH: docked =', pg.evaluate("SG.S.docked"), '| label:', pg.inner_text('#bBoost').replace('\n',' | '), '| throttle', pg.evaluate("SG.S.throttle"))
    pg.close(); print('\n'.join(errs) or 'no errors'); b.close()
