"""Step 3: assemble docs/requirements/index.html from the fragments mkreq.py wrote, the page styles and base callout data
in callouts_base.html, and the callout edits below. Pin positions (p, t) are in the 844 x 390 screenshots' CSS pixels.
"""
import os, subprocess, sys; sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..'))
from _common import DOCS, ROOT
HERE = os.path.dirname(os.path.abspath(__file__))
COMMIT = subprocess.run(['git', '-C', ROOT, 'rev-parse', '--short', 'HEAD'], capture_output=True, text=True).stdout.strip() or 'unknown'
import re
old = open(os.path.join(HERE, 'callouts_base.html')).read()
def cut(a, b): i = old.index(a); return old[i:old.index(b, i)]
css = cut('<style>', '</style>') + '</style>'
cockpit = cut('const COCKPIT = [', 'const COMMS = [')
comms = cut('const COMMS = [', 'const MAP = [')
mapd = cut('const MAP = [', "const NS = ")
builder = cut("const NS = ", "build('c', COCKPIT)")
def rep(s, a, b):
    assert s.count(a) == 1, (s.count(a), a[:70]); return s.replace(a, b)

# ---- flight screen callouts: new pins for the re-shot figure, and text for the rules that changed
cockpit = rep(cockpit, "p: [530, 62], t: [468, 108],", "p: [540, 62], t: [479, 106],")
cockpit = rep(cockpit, "p: [240, 54], t: [278, 87],", "p: [244, 52], t: [283, 85],")
cockpit = rep(cockpit, "Lasers and torpedoes then lead the target for you, and missiles home on it.", "Lasers and torpedoes then lead that ship for you. This lock is automatic; choosing a target by tapping is separate (see Targeting).")
cockpit = rep(cockpit, "d: 'Red, drawn around every hostile on the glass and sized by distance.", "d: 'Red, drawn around every hostile on the glass and sized by distance. Tap one to make it your chosen target.")
cockpit = rep(cockpit, "A hit costs 13 shield and stops the shields recharging for 4 seconds. They are slow enough to dodge,", "A hit costs 13 shield and stops the shields recharging for 4 seconds. They travel at 130, so they can be dodged but not outrun by boosting.")
cockpit = rep(cockpit, " your lasers can shoot them down (for no score), and a torpedo blast clears them.", " Your lasers can shoot them down (for no score), and a torpedo blast clears them.")
cockpit = rep(cockpit, "and gives way to a talking head while someone is speaking to you.", "and gives way to the target scope while a target is chosen, or to a talking head while someone is speaking.")
cockpit = rep(cockpit, "<b>Missiles</b> home on the locked target, or on whatever is ahead: one kills a raider or a saucer, a cruiser takes three.", "<b>Missiles</b> home on your chosen target, else the locked ship, else whatever is ahead: one kills a raider or a saucer, a shielded cruiser takes about four.")
cockpit = rep(cockpit, "enough to kill a cruiser caught in the inner half.", "enough to kill a cruiser in the inner half once its shield is down.")
cockpit = rep(cockpit, "While docked the top half reads LAUNCH and flashes.", "While docked the top half reads LAUNCH, and flashes once repair and rearm are done (1.3 s).")
cockpit = rep(cockpit, "Lasers: about 7.7 shots per second until the capacitor runs down after roughly 7 seconds, then about 3 per second.", "Lasers: about 7.7 shots per second until the capacitor runs down after roughly 7 seconds, then about 3 per second. Every hit also damages one subsystem of the ship it lands on.")

# ---- centre console: TARGET NEXT/PREV | radar (a caller takes it over) | target scope | VIEW over SCAN. Renumber and re-pin.
cockpit = re.sub(r"\{ n: (\d+),", lambda m: "{ n: %d," % (int(m.group(1)) + 2) if int(m.group(1)) >= 14 else m.group(0), cockpit)
items = re.findall(r"    \{ n: \d+, s: .*?\},\n(?=    \{ n|  \]\})", cockpit, flags=re.S)
by = {int(re.match(r"    \{ n: (\d+)", it).group(1)): it for it in items}
view, radar, scan = by[11], by[12], by[13]
new_view = rep(rep(view, "n: 11,", "n: 14,"), "p: [301, 243], t: [301, 268]", "p: [578, 288]")
new_scan = rep(rep(scan, "n: 13,", "n: 15,"), "p: [543, 243], t: [543, 268]", "p: [578, 330]")
new_radar = rep(rep(radar, "p: [422, 241], t: [422, 266]", "p: [359, 243], t: [359, 264]"), "and gives way to the target scope while a target is chosen, or to a talking head while someone is speaking.", "and gives way to a talking head while someone is speaking to you. Choosing a target does not hide it.")
tgt_btns = """    { n: 11, s: 'real', name: 'TARGET NEXT / PREV', p: [280, 243], t: [280, 268],
      d: 'Step through the hostiles in the sector and then the station, wrapping round. With nothing chosen, either button picks the nearest hostile. Dimmed when there is nothing to target. Tapping a ship on the glass does the same job directly.' },
"""
scope_item = """    { n: 13, s: 'real', name: 'Target scope', p: [453, 243], t: [453, 264],
      d: 'Reads NO TARGET until you choose one, then shows its wireframe and subsystems (see Targeting).' },
"""
cockpit = cockpit.replace(view + radar + scan, tgt_btns + new_radar + scope_item + new_view + new_scan)
assert "name: 'Target scope'" in cockpit and "name: 'TARGET NEXT / PREV'" in cockpit

target = r"""const TARGET = [
  { g: 'On the glass', items: [
    { n: 1, s: 'real', name: 'Chosen-target bracket', p: [560, 40], t: [522, 48],
      d: 'Tap a ship or the station to choose it. It gains a second, white bracket outside the red one. Tap it again to let go. Here the cruiser is both chosen (white bracket) and auto-locked (red diamond).' },
    { n: 2, s: 'real', name: 'Range and name', p: [532, 198], t: [482, 196],
      d: 'The chosen target always shows its range in large digits and its type, whether or not the lasers are locked on it. If it leaves the glass, its edge arrow turns white.' },
  ]},
  { g: 'Target scope (beside the radar)', items: [
    { n: 3, s: 'real', name: 'Wireframe', p: [453, 243], t: [453, 264],
      d: 'A slowly turning wireframe of the chosen ship or station, drawn from the same model you see in space. Tapping the wireframe releases the target. The radar stays in view beside it.' },
    { n: 4, s: 'real', name: 'Subsystem markers', p: [516, 248], t: [470, 290],
      d: 'Three squares on the hull: WEAPON at the nose, SHIELD amidships, ENGINE at the tail. Green is intact, amber damaged, red destroyed. The selected one has a flashing white box. This cruiser has a damaged shield (selected) and a destroyed engine.' },
    { n: 5, s: 'real', name: 'Subsystem selector', p: [406, 234], t: [407, 338],
      d: 'The two arrows along the bottom step through HULL, WEAPON, SHIELD and ENGINE; the line at the top of the scope names the item and shows it as a percentage, or OUT. With a subsystem selected, 80% of your hits on this ship land on it. Weapon out: it cannot fire. Engine out: it crawls at a quarter speed. Shield up: it soaks half of all hull damage, so stripping it first pays off on a cruiser. For a station the scope shows hull only.' },
    { n: 6, s: 'real', name: 'TARGET NEXT / PREV', p: [280, 243], t: [280, 268],
      d: 'Step to the next or previous target without taking a thumb off the console. The order is the hostiles in the sector, then the station.' },
  ]},
];
"""
comms = rep(comms, "p: [422, 243], t: [422, 264],", "p: [359, 243], t: [359, 264],")
comms = rep(comms, "It shows who is calling at a glance, but you have no radar until they finish.", "It shows who is calling at a glance, but you have no radar until they finish. The target scope beside it stays up.")
comms = rep(comms, "Green for your stations, red for the raider leader.", "Green for your stations, red for the raider leader. The three station heads are friendly robots of different shapes: square with one antenna, round with two feelers and a headset, and wide with a speaker grille.")
mapd = rep(mapd, "Closes the map and resumes the dogfight exactly where it froze.", "Returns to the cockpit. The fight has been running the whole time.")
mapd = rep(mapd, "The faint cockpit view showing through is the frozen 3D scene.", "The faint cockpit view showing through is the live 3D scene.")
mapd = rep(mapd, "Your energy and shield are repeated below.", "Your energy and shield are repeated below, and UNDER ATTACK flashes while hostiles are in your sector.")
mapd = rep(mapd, "Losing HOME ends the game; the other two can be lost.", "Losing HOME ends the game; the other two can be lost, at the cost of their wave-clear bonus and a place to dock.")

css = css.replace("</style>", """.toc{display:flex;flex-wrap:wrap;gap:6px 16px;font-family:var(--mono);font-size:12px;letter-spacing:.06em}
.toc a{color:var(--real);text-decoration:none;border-bottom:1px solid var(--line)}
.toc a:hover,.toc a:focus-visible{border-bottom-color:var(--real);outline:none}
.reqs{display:flex;flex-direction:column}
.req{display:grid;grid-template-columns:64px 1fr;gap:4px 12px;padding:9px 4px;border-top:1px solid var(--line)}
.req .id{font-family:var(--mono);font-size:12px;color:var(--mute);padding-top:2px;font-variant-numeric:tabular-nums}
.req p{max-width:74ch}
.req b{font-weight:600;color:#fff}
table.tune{border-collapse:collapse;width:100%;font-size:14px}
table.tune th{text-align:left;font-weight:500;color:var(--mute);font-family:var(--mono);font-size:12px;letter-spacing:.04em;padding:8px 14px 8px 4px;white-space:nowrap;vertical-align:top;border-top:1px solid var(--line)}
table.tune td{padding:8px 4px;border-top:1px solid var(--line)}
.wide{overflow-x:auto}
section{scroll-margin-top:12px}
</style>""")
css = css.replace(".rank{", ".x-rank{")   # ranking styles are no longer used

page = f"""<title>Starguard Requirements</title>
<meta name="claude:viewport-fit-sides" content="cover">
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=IBM+Plex+Sans:wght@400;500;600&family=Share+Tech+Mono&display=swap">
{css}

<div class="wrap">
  <header>
    <div class="eyebrow">Starguard prototype &middot; requirements</div>
    <h1>Starguard Requirements</h1>
    <p>What the game must do, written from the build as it stands at commit <code>{COMMIT}</code>. Each requirement has an ID so it can be referred to and changed on its own. The cockpit section keeps the annotated screenshots as the interface specification.</p>
    <p class="hint">Numbers are the current tuning values and are expected to move. Rules stated without a number are intended to hold.</p>
    <nav class="toc" aria-label="Sections">{open('req_nav.html').read()} <a href="#ui">Cockpit interface</a> <a href="#tuning">Tuning values</a> <a href="#open">Open questions</a></nav>
  </header>

{open('req_body.html').read()}
  <section id="ui">
    <h2>Cockpit interface</h2>
    <p>The four screens below are the interface specification. Every numbered element is required. Each note says what the element does; the tag says whether it is wired to game state.</p>
    <ul class="key">
      <li><span class="tag real">Real</span> wired to game state or input</li>
      <li><span class="tag part">Partly</span> real, with a catch</li>
      <li><span class="tag dress">Dressing</span> looks only, changes nothing</li>
    </ul>
    <div class="verdict">
      <h3>Decoration, by intent</h3>
      <ul>
        <li>No control is decorative. The stick and every button act on the game, and every bar shows a live value.</li>
        <li>Decorative only: the radar sweep line, the dashboard outline and panel seams, the scanlines, the stars and planet, and the nav computer bezel.</li>
        <li>The thruster-icon bar is the energy tank, not engine health. System damage has no console indicator of its own; the subspace radio reports it.</li>
        <li>DATE on the nav computer is a real clock that nothing reads.</li>
      </ul>
    </div>
  </section>

  <section>
    <h2>Flight screen</h2>
    <div class="scroll"><div class="shot" id="shot-c"><img src="cockpit.png" alt="Cockpit view with three hostiles in the sector, one auto-locked, missiles selected"></div></div>
    <p class="hint">Tap a number to jump to its note. Staged shot: two raiders and a saucer, one raider locked, missiles selected.</p>
    <div class="groups" id="legend-c"></div>
  </section>

  <section>
    <h2>Targeting</h2>
    <div class="scroll"><div class="shot" id="shot-t"><img src="target.png" alt="Cockpit with a cruiser chosen as target, its wireframe on the centre scope with the shield subsystem selected"></div></div>
    <p class="hint">Staged shot: a cruiser chosen by tapping it, SHIELD selected and at 40%, engine destroyed.</p>
    <div class="groups" id="legend-t"></div>
  </section>

  <section>
    <h2>Comms channel</h2>
    <div class="scroll"><div class="shot" id="shot-k"><img src="comm.png" alt="Cockpit with a green faceted head on the centre display and Beta Station's mayday typed on the bottom strip"></div></div>
    <p class="hint">Staged shot: Beta Station calling a mayday. The head has taken over the radar; the target scope beside it reads NO TARGET.</p>
    <div class="groups" id="legend-k"></div>
  </section>

  <section>
    <h2>Nav computer</h2>
    <div class="scroll"><div class="shot" id="shot-m"><img src="map.png" alt="Sector map with three stations, three red fleets and a selected warp target"></div></div>
    <p class="hint">Opened with SCAN. Nothing stops while it is open: fleets keep moving and the dogfight in your sector goes on without you at the controls.</p>
    <div class="groups" id="legend-m"></div>
  </section>

  <section id="tuning">
    <h2>Tuning values</h2>
    <p class="hint">Current settings, all in the tuning block at the top of the game script.</p>
    <div class="wide"><table class="tune"><tbody>
{open('req_tune.html').read()}
    </tbody></table></div>
    <h3 style="margin-top:14px">Keyboard, for desktop testing</h3>
    <p>{open('req_keys.html').read()}</p>
  </section>

  <section id="open">
    <h2>Open questions</h2>
    <p class="hint">Known gaps and decisions not yet made. None of these is a requirement.</p>
    <div class="reqs">
{open('req_open.html').read()}
    </div>
  </section>
</div>

<script>
// p = pin position, t = point the leader ends on (omit for no leader); both in the 844 x 390 screenshot's CSS pixels.
{cockpit}{target}{comms}{mapd}{builder}build('c', COCKPIT); build('t', TARGET); build('k', COMMS); build('m', MAP);
</script>
"""
open('artifact.html', 'w').write(page)                      # body-only form, for publishing as an artifact
open(os.path.join(DOCS, 'index.html'), 'w').write('<!doctype html>\n<html lang="en">\n<head>\n<meta charset="utf-8">\n<meta name="viewport" content="width=device-width,initial-scale=1">\n</head>\n<body style="margin:0">\n' + page + '</body>\n</html>\n')
names = re.findall(r"\{ n: (\d+), s: '(\w+)', name: '([^']+)'", page)
print(len(names), 'callouts;', page.count('class="req"'), 'requirement rows;', len(page)//1024, 'KB')
