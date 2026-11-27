# Starguard

A first-person space shooter in an 80s vector-arcade style, built as a prototype to find the fun. You fly one ship from a cockpit, fight raider fleets, and use a sector map to decide where to fight. It targets an iPhone-size screen in landscape with touch controls, and also runs in a desktop browser.

**Play:** https://dev.retroverse.ai/starguard/

![Cockpit with a cruiser targeted](docs/requirements/target.png)

## The game

- Raider fleets cross an 8 by 6 sector grid toward three stations. Lose HOME CONTROL, or your ship, and the run is over. There is no win state: the aim is score and waves survived.
- SCAN opens the nav computer. Tap a sector and WARP there. Jumps cost energy and time, and the fight in your sector keeps running while you read the chart.
- Lasers, homing missiles and aft-only torpedoes. Tap a ship to target it, then pick its weapon, shield or engine to concentrate your hits.
- Fly into a station ring to refuel, repair and rearm.
- Stations and the raider leader hail you over a comms channel with talking heads.

## Controls

| Touch | Keyboard | Action |
|---|---|---|
| Left thumb, anywhere on the left side | WASD or arrows | Steer |
| FIRE | Space | Fire the selected weapon |
| WEAPON | Q | Cycle laser, missile, torpedo |
| FASTER / SLOWER (tap) | `=` / `-` | Step the throttle |
| FASTER (hold) | Shift | Boost |
| SLOWER (hold) | X | Full stop |
| VIEW | V | Fore or aft view |
| Tap a ship, or TARGET NEXT / PREV | T / Shift+T | Choose a target |
| Scope arrows | `[` / `]` | Choose a subsystem |
| SCAN, then WARP | M, then Enter | Nav computer and warp |
| Pause (top right) | P or Esc | Pause and settings |

## Run it locally

Needs Python 3. No Node.js and no build step.

```sh
python3 -m venv .venv
.venv/bin/pip install -r requirements.txt
.venv/bin/python app.py          # http://localhost:5000
```

`HOST` and `PORT` environment variables change the address. The page loads three.js and one typeface from public CDNs, so the browser needs internet access.

## What is in here

| Path | What it is |
|---|---|
| `index.html` | The whole game: markup, styles and one JavaScript module using three.js. All tuning values sit in the `T` block at the top of the script. |
| `app.py` | Flask app. Serves the page and a small high-score API (`GET` and `POST /api/scores`), stored in `scores.json`. |
| `deploy/` | systemd unit (gunicorn on port 5079), the nginx block that mounts it at `/starguard/`, and `publish.sh`, which installs both. |
| `docs/requirements/` | The requirements document: numbered requirements plus annotated screenshots of the cockpit, targeting, comms and nav computer. Open `index.html` in a browser. |

## Deployment

`sh deploy/publish.sh` installs the service and adds the nginx block on the dev box, then reloads nginx. It is safe to re-run. The service serves this folder directly, so edits to `index.html` are live as soon as they are saved.

## Status

A prototype. It has been tested in a headless desktop browser at phone sizes; touch feel, frame rate and audio on real iPhone and iPad hardware are not yet confirmed. High scores are submitted by the browser and are not verified. Balance is untuned, and the open questions are listed at the end of the requirements document.
