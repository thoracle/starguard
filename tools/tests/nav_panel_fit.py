"""Nav computer side panel at three phone heights in its longest state: the text must end above the COCKPIT button.
"""
import glob, os
from playwright.sync_api import sync_playwright
import sys; sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..'))
from _common import EXE as exe, URL, DOCS, OUT, ROOT
NOTCH=':root{--esl:47px!important;--esr:47px!important;--esb:21px!important}'
with sync_playwright() as p:
    b = p.chromium.launch(executable_path=exe, args=['--use-gl=swiftshader','--enable-unsafe-swiftshader','--ignore-gpu-blocklist'])
    errs=[]
    for name,(w,h) in {'full':(844,390),'bars':(844,340),'tabs':(844,300)}.items():
        pg = b.new_page(viewport={'width':w,'height':h}, device_scale_factor=2, has_touch=True)
        pg.on('pageerror', lambda e: errs.append('PAGEERR: '+str(e)))
        pg.goto(URL); pg.wait_for_timeout(900); pg.add_style_tag(content=NOTCH); pg.tap('#bStart'); pg.wait_for_timeout(800)
        # worst case: hostiles here, comms down, emergency jump offered to a base with a fleet on it
        pg.evaluate("(()=>{const F=SG.fleets; F[0].x=SG.S.sx; F[0].y=SG.S.sy; F[1].x=4; F[1].y=1; F.forEach(f=>f.t=-999); SG.S.sys.COM=0; SG.S.energy=3;})()")
        pg.wait_for_function('SG.enemies.length>0', timeout=20000); pg.evaluate("SG.enemies.forEach(e=>e.cd=999)")
        pg.tap('#bMap'); pg.evaluate("SG.S.sel={x:4,y:1}"); pg.wait_for_timeout(700)
        r=pg.evaluate("(()=>{const q=id=>{const r=document.getElementById(id).getBoundingClientRect(); return [Math.round(r.top),Math.round(r.bottom)]}; return JSON.stringify({back:q('bBack'),warp:q('bWarp'),h:innerHeight})})()")
        print(name, r); pg.screenshot(path=f'mapfit_{name}.png', clip={'x':w-250,'y':0,'width':250,'height':h}); pg.close()
    print('\n'.join(errs) or 'no errors'); b.close()
