"""Rules from the second review pass: mid-warp arrivals spawn ahead, callers wait behind alerts, shield overflow,
centre console fit at four screen sizes, and the score shown at game over matching the score saved.
The score API is mocked, so this never writes to the real score file.
"""
import glob, os
from playwright.sync_api import sync_playwright
import sys; sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..'))
from _common import EXE as exe, URL, DOCS, OUT, ROOT
with sync_playwright() as p:
    b = p.chromium.launch(executable_path=exe, args=['--use-gl=swiftshader','--enable-unsafe-swiftshader','--ignore-gpu-blocklist'])
    errs=[]
    def fresh(w=844,h=390,css=None):
        pg = b.new_page(viewport={'width':w,'height':h}, has_touch=True)
        pg.on('pageerror', lambda e: errs.append('PAGEERR: '+str(e)))
        pg.on('console', lambda m: errs.append(m.text) if m.type=='error' else None)
        pg.route('**/api/scores', lambda r: r.fulfill(status=200, content_type='application/json', body='[{"name":"ACE","score":1634,"wave":1}]'))
        pg.goto(URL); pg.wait_for_timeout(900)
        if css: pg.add_style_tag(content=css)
        pg.tap('#bStart'); pg.wait_for_timeout(700); return pg
    # 1: fleet stepping in during the time-skip should be in FRONT of the drop-out point (negative z in ship frame)
    pg = fresh()
    pg.evaluate("(()=>{ SG.fleets.splice(1); const f=SG.fleets[0]; f.x=5; f.y=1; f.target=SG.bases[1]; f.t=5; f.comp=['F','F','F']; SG.openMap(); SG.S.sel={x:4,y:1}; SG.tryWarp(); })()")
    pg.wait_for_function('SG.S.mode==="flight"', timeout=60000)
    print('1 arrivals, z in ship frame (want all negative):', pg.evaluate("SG.enemies.map(e=>Math.round(SG.ship.worldToLocal(e.o.position.clone()).z))"))
    # 2: a waiting caller must not blank the scope; speech starts by itself even if an alert is being held up
    pg.evaluate("SG.S.comm=null; SG.S.commQ=[]; SG.S.msg='TEST ALERT'; SG.S.msgC='#ff4a3a'; SG.S.msgT=99; SG.hail('BETA','Testing.',2)"); pg.wait_for_timeout(1000)
    print('2 waiting behind an alert: comm.t =', pg.evaluate("SG.S.comm && SG.S.comm.t"), '(0 = scope still shows radar)')
    pg.wait_for_timeout(5000); print('2 after 5 s of a stuck alert: comm.t > 0 =', pg.evaluate("!!(SG.S.comm ? SG.S.comm.t>0 : true)"))
    pg.close()
    # 6: shield overflow
    pg = fresh(); pg.evaluate("SG.ship.rotateY(Math.PI)")
    pg.evaluate("(()=>{const f=SG.fleets[0]; f.x=SG.S.sx; f.y=SG.S.sy; f.comp=['C'];})()"); pg.wait_for_function('SG.enemies.length===1', timeout=20000)
    pg.evaluate("(()=>{const e=SG.enemies[0]; e.cd=99; SG.S.shield=2; e.o.position.copy(SG.ship.position);})()"); pg.wait_for_timeout(600)
    print('6 ram (25) into a 2-point shield: shield', pg.evaluate("SG.S.shield"), 'systems', pg.evaluate("JSON.stringify(SG.S.sys)"))
    pg.close()
    # 11: narrow layouts: do the centre buttons overlap the scope?
    for name,(w,h,css) in {'844 notch':(844,390,':root{--esl:47px!important;--esr:47px!important;--esb:21px!important}'),'812 notch':(812,375,':root{--esl:44px!important;--esr:44px!important;--esb:21px!important}'),'667 SE':(667,375,None),'1376 desk':(1376,886,None)}.items():
        pg = fresh(w,h,css); pg.wait_for_timeout(700)
        print('11', name, pg.evaluate("""(()=>{const r=id=>document.getElementById(id).getBoundingClientRect(), v=r('bView'), m=r('bMap'), cs=getComputedStyle(document.documentElement);
          const cl=parseFloat(cs.getPropertyValue('--cl')), cr=parseFloat(cs.getPropertyValue('--cr')), bw=parseFloat(cs.getPropertyValue('--bw')); const room=cr-cl-28, rad=Math.max(14,Math.min(42,(room-2*bw)/2)), cx=innerWidth/2;
          return JSON.stringify({view:[Math.round(v.left),Math.round(v.right)], scope:[Math.round(cx-rad),Math.round(cx+rad)], scan:[Math.round(m.left),Math.round(m.right)], overlap: v.right>cx-rad || m.left<cx+rad});})()"""))
        if name=='812 notch': pg.screenshot(path='narrow.png', clip={'x':0,'y':200,'width':812,'height':175})
        pg.close()
    # 12/13: save flow
    pg = fresh()
    pg.evaluate("SG.S.score=1234; SG.S.shield=0; SG.S.sys={RAD:0,COM:0,ENG:0}; SG.ship.rotateY(Math.PI)")
    pg.evaluate("(()=>{const f=SG.fleets[0]; f.x=SG.S.sx; f.y=SG.S.sy; f.comp=['F'];})()"); pg.wait_for_function('SG.enemies.length===1', timeout=20000)
    pg.evaluate("SG.enemies[0].o.position.copy(SG.ship.position)"); pg.wait_for_function('SG.S.mode==="over"', timeout=20000)
    print('12 fatal ram: shown', repr(pg.inner_text('#fin')), '| actual score', pg.evaluate("SG.S.score"))
    pg.tap('#bSave'); pg.wait_for_timeout(800); print('12 after save:', repr(pg.inner_text('#fin')), '| table lines:', len(pg.inner_text('#hi2').splitlines()), '(score API mocked)')
    pg.close()
    print('\n'.join(errs) or 'no errors'); b.close()
