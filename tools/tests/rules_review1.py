"""Rules from the first review pass: shield recharge delay, emergency jump, one-hit ramming, no docking under fire, comms-out silence.
"""
import glob, os
from playwright.sync_api import sync_playwright
import sys; sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..'))
from _common import EXE as exe, URL, DOCS, OUT, ROOT
with sync_playwright() as p:
    b = p.chromium.launch(executable_path=exe, args=['--use-gl=swiftshader','--enable-unsafe-swiftshader','--ignore-gpu-blocklist'])
    errs=[]
    def fresh():
        pg = b.new_page(viewport={'width':844,'height':390}, has_touch=True)
        pg.on('pageerror', lambda e: errs.append('PAGEERR: '+str(e)))
        pg.on('console', lambda m: errs.append(m.text) if m.type=='error' else None)
        pg.goto(URL); pg.wait_for_timeout(900); pg.tap('#bStart'); pg.wait_for_timeout(300)
        pg.evaluate("SG.ship.rotateY(Math.PI); SG.S.msgT=0"); return pg
    # shields: regen pauses after a hit
    pg = fresh()
    pg.evaluate("SG.S.shield=50; SG.S.shieldT=4"); pg.wait_for_timeout(1500); a=pg.evaluate("SG.S.shield")
    pg.evaluate("SG.S.shieldT=0"); pg.wait_for_timeout(1500); c=pg.evaluate("SG.S.shield")
    print(f'shield during delay {a:.1f} (want 50.0), after delay {c:.1f} (want >50)')
    # emergency jump
    pg.evaluate("SG.S.energy=3; SG.S.shield=80; SG.openMap(); SG.S.sel={x:7,y:5}; SG.tryWarp()"); print('low energy to open space ->', pg.evaluate("SG.S.mode"))
    pg.evaluate("SG.S.sel={x:4,y:1}; SG.tryWarp()"); print('low energy to a base ->', pg.evaluate("SG.S.mode"), pg.evaluate("JSON.stringify({en:SG.S.energy,sh:SG.S.shield})"))
    pg.wait_for_function('SG.S.mode==="flight"', timeout=60000); print('arrived', pg.evaluate("[SG.S.sx,SG.S.sy]")); pg.close()
    # cruiser ram: one hit, not a hit per frame
    pg = fresh()
    pg.evaluate("(()=>{const f=SG.fleets[0]; f.x=SG.S.sx; f.y=SG.S.sy; f.comp=['C'];})()"); pg.wait_for_function('SG.enemies.length===1', timeout=20000)
    pg.evaluate("(()=>{const e=SG.enemies[0]; e.o.position.copy(SG.ship.position); e.cd=99;})()"); pg.wait_for_timeout(1200)
    print('after cruiser ram:', pg.evaluate("JSON.stringify({mode:SG.S.mode,shield:Math.round(SG.S.shield),cruiserHp:SG.enemies[0]&&SG.enemies[0].hp})"))
    # docking with hostiles present
    pg.evaluate("SG.enemies[0].o.position.set(900,0,0); SG.enemies[0].cd=99; SG.S.dockCD=0; SG.ship.position.set(0,-8,-320)"); pg.wait_for_timeout(700)
    print('dock with hostile in sector: docked =', pg.evaluate("SG.S.docked"), '| msg:', pg.evaluate("SG.S.msg"))
    pg.close()
    # comms out: radio and SCAN flash stay quiet
    pg = fresh()
    pg.evaluate("(()=>{const f=SG.fleets[0]; f.x=SG.bases[1].x; f.y=SG.bases[1].y; SG.S.sys.COM=0;})()"); pg.wait_for_timeout(500)
    print('comms out, fleet on a base: SCAN flashing =', pg.evaluate("document.getElementById('bMap').classList.contains('alert')"))
    pg.close()
    print('\n'.join(errs) or 'no errors'); b.close()
