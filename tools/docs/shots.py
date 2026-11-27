"""Step 1 of the requirements-doc build: stage the game and capture the four figures into docs/requirements/.
Staging is fixed (fleets parked, ships placed by hand) so the callout pins in mkpage.py stay valid.
"""
import glob, os
from playwright.sync_api import sync_playwright
import sys; sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..'))
from _common import EXE as exe, URL, DOCS, OUT, ROOT
U=URL
STAGE = "(()=>{const S=SG.S,f=SG.fleets[0]; S.sx=f.x; S.sy=f.y; f.comp=COMP; S.energy=72; S.shield=58; S.score=2510; SG.ship.position.set(0,0,0); SG.ship.quaternion.identity(); SG.fleets.forEach(g=>g.t=-999); SG.bases.forEach(b=>{b.hp=100; b.warned=true;});})()"
PLACE = """(()=>{
  const spots=[[9,5,-150],[-95,22,-260],[220,-60,260]];
  SG.enemies.forEach((e,i)=>{ e.o.position.set(...spots[i]); e.cd=99; e.mode='evade'; e.modeT=9; e.evade.set(0,0,-1); e.o.lookAt(e.o.position.x+60,e.o.position.y+10,e.o.position.z-100); });
  SG.bolts.forEach((b,i)=>{ if(i===0){ b.o.position.set(95,-14,-300); b.vel.set(0,0,-40); b.life=99; } else b.life=0; });
  SG.S.msgT=0; SG.S.comm=null; SG.S.commQ=[]; SG.S.lowHail=true; SG.S.ammo.m=6; if(SG.S.wpn===0) SG.cycleWeapon();
})()"""
READ = """(()=>{
  const cam=SG.ship.children[0], W=innerWidth, H=innerHeight, out=[];
  for(const e of SG.enemies){ const p=e.o.position.clone(); const l=p.clone().applyMatrix4(cam.matrixWorldInverse); const n=p.clone().project(cam);
    out.push({type:e.type, front:l.z<0, x:Math.round((n.x+1)/2*W), y:Math.round((1-n.y)/2*H), lock:e===SG.S.lock, tgt:e===SG.S.target}); }
  for(const b of SG.bolts){ const n=b.o.position.clone().project(cam); out.push({k:'bolt',x:Math.round((n.x+1)/2*W),y:Math.round((1-n.y)/2*H)}); }
  return JSON.stringify(out);
})()"""
FREEZE = "window.requestAnimationFrame=()=>0"
with sync_playwright() as p:
    b = p.chromium.launch(executable_path=exe, args=['--use-gl=swiftshader','--enable-unsafe-swiftshader','--ignore-gpu-blocklist'])
    errs=[]
    def fight(comp):
        pg = b.new_page(viewport={'width':844,'height':390}, device_scale_factor=2, has_touch=True)
        pg.on('pageerror', lambda e: errs.append(str(e)))
        pg.goto(U); pg.wait_for_timeout(900); pg.tap('#bStart'); pg.wait_for_timeout(400)
        st = STAGE.replace('COMP', comp)
        pg.evaluate(st); pg.evaluate("(()=>{const f=SG.fleets[0]; SG.openMap(); SG.S.sel={x:f.x,y:f.y}; SG.S.sx=1; SG.S.sy=3; SG.tryWarp();})()")
        pg.wait_for_function('SG.S.mode==="flight" && SG.bolts.length>0', timeout=90000)
        pg.evaluate(st); pg.evaluate(PLACE); return pg
    # flight screen
    pg = fight("['F','F','S']"); pg.wait_for_timeout(350); pg.evaluate(FREEZE); pg.wait_for_timeout(300)
    print('cockpit', pg.evaluate(READ)); pg.screenshot(path=DOCS+'/cockpit.png'); pg.close()
    # comms
    pg = fight("['F','F','S']")
    pg.evaluate("SG.hail('BETA','Mayday, mayday. Beta Station is under attack. We need you here, Starguard.',2)")
    pg.wait_for_function('SG.S.comm && SG.S.comm.t>1.25', timeout=60000); pg.evaluate(FREEZE); pg.wait_for_timeout(300)
    pg.screenshot(path=DOCS+'/comm.png'); pg.close()
    # targeting: cruiser chosen, SHIELD selected and half gone, engine out
    pg = fight("['C','F','F']")
    pg.evaluate("(()=>{const e=SG.enemies.find(e=>e.type==='C'); SG.setTarget(e); SG.cycleSub(1); SG.cycleSub(1); e.sub.S=2; e.sub.E=0; e.hp=9; SG.S.msgT=0;})()")
    pg.wait_for_timeout(450); pg.evaluate(PLACE); pg.wait_for_timeout(200); print('target shot: comm active =', pg.evaluate('!!SG.S.comm'), '| target set =', pg.evaluate('!!SG.S.target')); pg.evaluate(FREEZE); pg.wait_for_timeout(300)
    print('target ', pg.evaluate(READ)); pg.screenshot(path=DOCS+'/target.png'); pg.close()
    # nav computer, fixed layout so the callout pins stay valid
    pg = b.new_page(viewport={'width':844,'height':390}, device_scale_factor=2, has_touch=True)
    pg.goto(U); pg.wait_for_timeout(900); pg.tap('#bStart'); pg.wait_for_timeout(400)
    pg.evaluate("""(()=>{ const F=SG.fleets; F.splice(3); const cells=[[7,2,2,['C','F','F']],[7,4,1,['F','F']],[7,0,2,['F','F']]];
      cells.forEach((c,i)=>{ if(!F[i]) F.push({t:0}); Object.assign(F[i],{x:c[0],y:c[1],target:SG.bases[c[2]],comp:c[3],t:-999}); });
      SG.S.energy=72; SG.S.shield=58; SG.S.score=2510; SG.S.comm=null; SG.S.commQ=[]; SG.openMap(); SG.S.sel={x:7,y:2}; })()""")
    pg.wait_for_timeout(350); pg.evaluate(FREEZE); pg.wait_for_timeout(300); pg.screenshot(path=DOCS+'/map.png'); pg.close()
    print(errs or 'no errors'); b.close()
