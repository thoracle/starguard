"""Fleets timed to step into, or out of, the destination sector during a warp. Want ships charted = ships in space, same sector.
"""
import glob, os, sys
from playwright.sync_api import sync_playwright
import sys; sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..'))
from _common import EXE as exe, URL, DOCS, OUT, ROOT
snap = "JSON.stringify({mode:SG.S.mode, at:[SG.S.sx,SG.S.sy], shipsHere:SG.enemies.length, fleets:SG.fleets.map(f=>({at:[f.x,f.y],ships:f.comp.length}))})"
with sync_playwright() as p:
    b = p.chromium.launch(executable_path=exe, args=['--use-gl=swiftshader','--enable-unsafe-swiftshader','--ignore-gpu-blocklist'])
    errs=[]
    def fresh():
        pg = b.new_page(viewport={'width':844,'height':390}, has_touch=True)
        pg.on('pageerror', lambda e: errs.append('PAGEERR: '+str(e)))
        pg.goto(URL); pg.wait_for_timeout(900); pg.tap('#bStart'); pg.wait_for_timeout(300)
        return pg
    # A: a fleet one step from BETA, timed to step INTO it just after we drop out of warp there
    pg = fresh()
    pg.evaluate("(()=>{ SG.fleets.splice(1); const f=SG.fleets[0]; f.x=5; f.y=1; f.target=SG.bases[1]; f.t=5; f.comp=['F','F','F']; SG.openMap(); SG.S.sel={x:4,y:1}; SG.tryWarp(); })()")
    pg.wait_for_function('SG.S.mode==="flight"', timeout=60000); pg.wait_for_timeout(1500)
    print('A  fleet arrives during warp-out :', pg.evaluate(snap)); pg.close()
    # B: a fleet already AT the destination, timed to step away during the warp-out while its ships are in front of us
    pg = fresh()
    pg.evaluate("(()=>{ SG.fleets.splice(1); const f=SG.fleets[0]; f.x=6; f.y=1; f.target=SG.bases[1]; f.t=5; f.comp=['F','F','F']; SG.openMap(); SG.S.sel={x:6,y:1}; SG.tryWarp(); })()")
    pg.wait_for_function('SG.S.mode==="flight"', timeout=60000); pg.wait_for_timeout(1500)
    print('B  fleet leaves during warp-out  :', pg.evaluate(snap)); pg.close()
    print('\n'.join(errs) or 'no errors'); b.close()
