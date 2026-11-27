"""TARGET NEXT / PREV: button sizes and positions at three layouts, and the order they step through.
"""
import glob, os
from playwright.sync_api import sync_playwright
import sys; sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..'))
from _common import EXE as exe, URL, DOCS, OUT, ROOT
NOTCH=':root{--esl:47px!important;--esr:47px!important;--esb:21px!important}'
with sync_playwright() as p:
    b = p.chromium.launch(executable_path=exe, args=['--use-gl=swiftshader','--enable-unsafe-swiftshader','--ignore-gpu-blocklist'])
    errs=[]
    for name,(w,h,css) in {'notch':(844,390,NOTCH),'flat':(844,390,None),'desk':(1376,886,None)}.items():
        pg = b.new_page(viewport={'width':w,'height':h}, device_scale_factor=2, has_touch=True)
        pg.on('pageerror', lambda e: errs.append('PAGEERR: '+str(e)))
        pg.goto(URL); pg.wait_for_timeout(900)
        if css: pg.add_style_tag(content=css)
        pg.tap('#bStart'); pg.wait_for_timeout(900)
        q = "(()=>{const q=id=>{const r=document.getElementById(id).getBoundingClientRect(); return [Math.round(r.left),Math.round(r.top),Math.round(r.width),Math.round(r.height)]}; return JSON.stringify({next:q('bTgN'),prev:q('bTgP'),view:q('bView'),scan:q('bMap')});})()"
        print(name, pg.evaluate(q), '| dim with nothing to target but the base:', pg.evaluate("document.getElementById('bTgN').classList.contains('off')"))
        pg.evaluate("SG.ship.rotateY(Math.PI); (()=>{const f=SG.fleets[0]; f.x=SG.S.sx; f.y=SG.S.sy; f.comp=['C','F','F'];})()"); pg.wait_for_function('SG.enemies.length===3', timeout=20000)
        pg.evaluate("(()=>{SG.enemies.forEach(e=>e.cd=99); SG.S.msgT=0; SG.S.comm=null; SG.S.commQ=[];})()")
        seq=[]
        for btn in ['#bTgN','#bTgN','#bTgN','#bTgN','#bTgN','#bTgP']:
            pg.tap(btn); pg.wait_for_timeout(80); seq.append(pg.evaluate("SG.S.target ? (SG.S.target.base ? 'BASE' : SG.S.target.def.name+'@'+Math.round(SG.S.target.o.position.distanceTo(SG.ship.position))) : 'none'"))
        print('  next x5, prev x1 ->', seq)
        pg.evaluate("SG.S.msgT=0; SG.S.comm=null; SG.S.commQ=[]"); pg.wait_for_timeout(300); pg.screenshot(path=f'tgb_{name}.png')
        pg.close()
    print('\n'.join(errs) or 'no errors'); b.close()
