"""Soak test: an autopilot fights through several waves with fleets sped up, checking 25 times a second that the
sector chart and the ships in space agree and that no spoken fleet count is stale. Prints one line per 30 s; want violations 0.
"""
import glob, os
from playwright.sync_api import sync_playwright
import sys; sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..'))
from _common import EXE as exe, URL, DOCS, OUT, ROOT
BOT = """
window.viol=[]; window.kills=0; window.warps=0; window.badHails=[];
const _hail=SG.hail;
setInterval(()=>{ const S=SG.S;
  if(S.mode==='over'){ SG.startGame(); return; }
  if(S.mode!=='flight') return;
  S.shield=100; S.energy=Math.max(S.energy,60);                 // keep the bot alive: we are testing bookkeeping, not difficulty
  // invariants between the chart and the sector
  const here=SG.fleets.filter(f=>f.x===S.sx&&f.y===S.sy);
  for(const f of here){ const n=SG.enemies.filter(e=>e.fleet===f).length; if(n!==f.comp.length) viol.push(`fleet at player sector lists ${f.comp.length} ships, ${n} in space`); }
  for(const e of SG.enemies){ if(!SG.fleets.includes(e.fleet)) viol.push('ship in space whose fleet is gone from the chart'); else if(e.fleet.x!==S.sx||e.fleet.y!==S.sy) viol.push('ship in space whose fleet is charted elsewhere'); }
  if(S.comm && /(\\d+) (to go|still out there|left on the board)/.test(S.comm.text)){ const m=+S.comm.text.match(/(\\d+) (to go|still out there|left on the board)/)[1]; if(m>SG.fleets.length) badHails.push(S.comm.text+' | fleets now '+SG.fleets.length); }
  let tgt=null,bd=1e9; for(const e of SG.enemies){const d=e.o.position.distanceTo(SG.ship.position); if(d<bd){bd=d;tgt=e.o.position;}}
  if(!tgt){ SG.input.x=SG.input.y=0; SG.input.fire=false;
    if(SG.fleets.length){ const f=SG.fleets[Math.random()*SG.fleets.length|0]; if(f.x!==S.sx||f.y!==S.sy){ SG.openMap(); S.sel={x:f.x,y:f.y}; SG.tryWarp(); warps++; } }
    return; }
  const l=SG.ship.worldToLocal(tgt.clone()), n=Math.hypot(l.x,l.y,l.z);
  SG.input.x=Math.max(-1,Math.min(1,l.x/n*4+(l.z>0?1:0))); SG.input.y=Math.max(-1,Math.min(1,-l.y/n*4)); SG.input.fire=l.z<0&&!!S.lock;
},40);
"""
with sync_playwright() as p:
    b = p.chromium.launch(executable_path=exe, args=['--use-gl=swiftshader','--enable-unsafe-swiftshader','--ignore-gpu-blocklist'])
    errs=[]
    pg = b.new_page(viewport={'width':844,'height':390}, has_touch=True)
    pg.on('pageerror', lambda e: errs.append('PAGEERR: '+str(e)))
    pg.goto(URL); pg.wait_for_timeout(900); pg.tap('#bStart'); pg.wait_for_timeout(300)
    pg.evaluate("SG.T.fleetStep=6; SG.T.warpDays=3")      # fast fleets, so they cross sector borders during warps as often as possible
    pg.evaluate(BOT)
    for i in range(2):
        pg.wait_for_timeout(30000)
        print(pg.evaluate("JSON.stringify({wave:SG.S.wave,score:SG.S.score,warps,fleets:SG.fleets.length,violations:viol.length,sample:[...new Set(viol)].slice(0,3),badHails:badHails.slice(0,2)})"))
    print('\n'.join(errs) or 'no errors'); b.close()
