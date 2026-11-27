"""Tap-to-target: tap the station and a cruiser on the glass, step subsystems, check hits go to the selected subsystem,
and that a destroyed weapon stops firing and a destroyed engine slows the ship.
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
    pg.on('console', lambda m: errs.append(m.text) if m.type=='error' else None)
    pg.goto(URL); pg.wait_for_timeout(1000); pg.tap('#bStart'); pg.wait_for_timeout(600)
    # station: tap it on the glass
    pos = pg.evaluate("(()=>{const c=SG.ship.children[0]; const v=SG.ship.position.clone().set(0,-8,-330).project(c); return [(v.x+1)/2*innerWidth,(1-v.y)/2*innerHeight];})()")
    pg.touchscreen.tap(pos[0], pos[1]); pg.wait_for_timeout(500)
    print('tap station ->', pg.evaluate("SG.S.target===SG.BASE_T"), '| sub buttons hidden:', pg.evaluate("document.getElementById('bSubP').hidden"))
    pg.screenshot(path='tg_base.png', clip={'x':264,'y':250,'width':316,'height':115})
    pg.tap('#bTgt'); print('tap scope clears ->', pg.evaluate("SG.S.target"))
    # bring in a cruiser and two raiders, park them in view
    pg.evaluate("SG.ship.rotateY(Math.PI); (()=>{const f=SG.fleets[0]; f.x=SG.S.sx; f.y=SG.S.sy; f.comp=['C','F','F'];})()"); pg.wait_for_function('SG.enemies.length===3', timeout=20000)
    hold = "(()=>{const sp=[[30,10,-170],[-90,25,-240],[120,-20,-260]]; SG.enemies.forEach((e,i)=>{ e.o.position.copy(SG.ship.localToWorld(new (SG.ship.position.constructor)(...sp[i]))); e.cd=99; e.mode='evade'; e.modeT=99; e.evade.copy(new (SG.ship.position.constructor)(0,0,-1).applyQuaternion(SG.ship.quaternion)); }); SG.S.throttle=0; SG.S.speed=0; SG.S.msgT=0; SG.S.comm=null; SG.S.commQ=[];})()"
    pg.evaluate(hold); pg.wait_for_timeout(250)
    pos = pg.evaluate("(()=>{const c=SG.ship.children[0]; const v=SG.enemies[0].o.position.clone().project(c); return [(v.x+1)/2*innerWidth,(1-v.y)/2*innerHeight];})()")
    pg.touchscreen.tap(pos[0], pos[1]); pg.wait_for_timeout(300)
    print('tap cruiser ->', pg.evaluate("SG.S.target && SG.S.target.def.name"), '| sub buttons shown:', pg.evaluate("!document.getElementById('bSubP').hidden"))
    pg.tap('#bSubN'); pg.tap('#bSubN'); pg.wait_for_timeout(200); print('next x2 -> subsystem index', pg.evaluate("SG.S.subI"), '(2 = SHIELD)')
    # fire lasers with shield selected: where do the hits go?
    pg.evaluate(hold); pg.evaluate("window.fz=setInterval(()=>{ const e=SG.enemies.find(e=>e.type==='C'); if(e){ e.hp=14; } },50); SG.input.fire=true")
    pg.evaluate("(()=>{const e=SG.S.target; const l=SG.ship.worldToLocal(e.o.position.clone()); })()")
    # aim at it
    pg.evaluate("window.aim=setInterval(()=>{const e=SG.S.target; if(!e||!SG.enemies.includes(e))return; const l=SG.ship.worldToLocal(e.o.position.clone()), n=Math.hypot(l.x,l.y,l.z); SG.input.x=Math.max(-1,Math.min(1,l.x/n*4)); SG.input.y=Math.max(-1,Math.min(1,-l.y/n*4));},30)")
    pg.wait_for_function("SG.S.target && SG.S.target.sub.S===0", timeout=60000)
    print('shield selected, after shield is destroyed:', pg.evaluate("JSON.stringify(SG.S.target.sub)"), '| msg:', pg.evaluate("SG.S.msg"))
    pg.evaluate("SG.input.fire=false"); pg.wait_for_timeout(300); pg.screenshot(path='tg_ship.png'); pg.screenshot(path='tg_scope.png', clip={'x':264,'y':250,'width':316,'height':115})
    # effects: weapon out => no firing; engine out => crawl
    pg.evaluate("clearInterval(fz); clearInterval(aim); SG.input.x=SG.input.y=0; (()=>{const e=SG.S.target; e.sub.E=0; e.sub.W=0; e.cd=0; e.mode='attack';})()"); n0=pg.evaluate("SG.bolts.length"); pg.wait_for_timeout(2500)
    print('weapon+engine out: speed', pg.evaluate("Math.round(SG.S.target.vel.length()*10)/10"), '(normal 22) | shots fired by it:', pg.evaluate("SG.bolts.length")-n0)
    pg.evaluate("(()=>{SG.S.target.hp=0.1; SG.cycleSub(0);})()"); 
    print('missile prefers target:', pg.evaluate("(()=>{SG.S.wpn=1; SG.S.fireCD=0; SG.input.fire=true; return true;})()")); pg.wait_for_timeout(400)
    print('  missile target is chosen ship:', pg.evaluate("SG.ords.length? SG.ords[0].target===SG.S.target : 'none fired'")); pg.evaluate("SG.input.fire=false")
    pg.close(); print('\n'.join(errs) or 'no errors'); b.close()
