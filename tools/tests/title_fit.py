"""Title screen at five screen heights with a full score table (mocked): LAUNCH must stay visible.
"""
import glob, os, json, urllib.request
from playwright.sync_api import sync_playwright
import sys; sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..'))
from _common import EXE as exe, URL, DOCS, OUT, ROOT
U=URL
fake=json.dumps([{"name":"ACE","score":123450-i*9000,"wave":9-i} for i in range(5)])
with sync_playwright() as p:
    b = p.chromium.launch(executable_path=exe, args=['--use-gl=swiftshader','--enable-unsafe-swiftshader','--ignore-gpu-blocklist'])
    for name,(w,h) in {'iphone full':(844,390),'iphone safari bars':(844,340),'iphone tab bar':(844,300),'SE':(667,320),'desk':(1376,886)}.items():
        pg = b.new_page(viewport={'width':w,'height':h}, device_scale_factor=2, has_touch=True)
        pg.route('**/api/scores', lambda r: r.fulfill(status=200, content_type='application/json', body=fake))   # a full score table, the worst case for height
        pg.goto(U); pg.wait_for_timeout(1200)
        r = pg.evaluate("(()=>{const q=id=>{const r=document.getElementById(id).getBoundingClientRect(); return [Math.round(r.top),Math.round(r.bottom)]}; return {h:innerHeight, title:q('ovTitle').length&&[Math.round(document.querySelector('#ovTitle h1').getBoundingClientRect().top)], launch:q('bStart')}})()")
        print(f"{name:20} height {r['h']}: title top {r['title'][0]}, LAUNCH {r['launch']} -> {'visible' if r['launch'][0]>=0 and r['launch'][1]<=r['h'] else 'CLIPPED'}")
        if name in ('iphone safari bars','iphone tab bar'): pg.screenshot(path=f"title_{h}.png")
        pg.close()
    b.close()
