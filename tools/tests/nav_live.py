"""The dogfight keeps running behind the nav computer: the ship and enemies move, no firing from the map, and you can be destroyed there.
"""
import glob, os
from playwright.sync_api import sync_playwright
import sys; sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..'))
from _common import EXE as exe, URL, DOCS, OUT, ROOT
with sync_playwright() as p:
    b = p.chromium.launch(executable_path=exe, args=['--use-gl=swiftshader','--enable-unsafe-swiftshader','--ignore-gpu-blocklist'])
    errs=[]
    pg = b.new_page(viewport={'width':844,'height':390}, device_scale_factor=2, has_touch=True)
    pg.on('pageerror', lambda e: errs.append('PAGEERR: '+str(e)))
    pg.goto(URL); pg.wait_for_timeout(900); pg.tap('#bStart'); pg.wait_for_timeout(500)
    pg.evaluate("SG.ship.rotateY(Math.PI); (()=>{const f=SG.fleets[0]; f.x=SG.S.sx; f.y=SG.S.sy; f.comp=['C','F','F'];})()"); pg.wait_for_function('SG.enemies.length===3', timeout=20000)
    pg.tap('#bMap'); pg.wait_for_timeout(200)
    a = pg.evaluate("JSON.stringify({mode:SG.S.mode, sh:Math.round(SG.S.shield), z:Math.round(SG.ship.position.length()), e0:Math.round(SG.enemies[0].o.position.distanceTo(SG.ship.position))})")
    pg.keyboard.down('Space'); pg.keyboard.down('ArrowLeft'); pg.wait_for_timeout(9000); pg.keyboard.up('Space'); pg.keyboard.up('ArrowLeft')
    c = pg.evaluate("JSON.stringify({mode:SG.S.mode, sh:Math.round(SG.S.shield), z:Math.round(SG.ship.position.length()), e0:SG.enemies[0]?Math.round(SG.enemies[0].o.position.distanceTo(SG.ship.position)):null, charge:Math.round(SG.S.charge), enemies:SG.enemies.length})")
    print('map opened :', a); print('9 s later  :', c, '(ship and enemies moved; shields may have dropped; charge 100 = no firing from the map)')
    pg.screenshot(path='navlive.png')
    # die on the map
    pg.evaluate("SG.S.shield=0; SG.S.sys={RAD:0,COM:0,ENG:0}; SG.enemies.forEach(e=>{e.cd=0;})"); 
    try:
        pg.wait_for_function('SG.S.mode==="over"', timeout=40000); print('killed while on the map -> mode', pg.evaluate("SG.S.mode"), '|', pg.inner_text('#why'))
    except Exception as ex: print('not killed within 40 s:', pg.evaluate("JSON.stringify({mode:SG.S.mode,sh:SG.S.shield,bolts:SG.bolts.length})"))
    pg.close(); print('\n'.join(errs) or 'no errors'); b.close()
