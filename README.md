# Balde Space Invaders

A single-player Python arcade game. Fly in four directions with the arrow keys or WASD and fire with Space. The ship can fly up to the edge of the enemy spawn area. Every 15 hits clears a wave. Every fifth wave replaces the six invaders with a 15-hit boss. It tracks your ship, locks its position, and marks its firing lanes in gold. Its volleys alternate between two outer bolts and three bolts that cover the middle as well. Defeat it to advance to the next regular wave. Hitting an enemy with your ship or letting one reach the bottom defense line ends the round.

From wave 2, a charging enemy stops and shows a gold warning. Move out of its lane or shoot it before the red bolt launches. An unshielded bolt hit ends the round. Later waves fire faster.

On the fifth hit of each wave, an enemy drops a cyan shield if your ship is unshielded. Fly into it to collect one charge. The cyan ring around your ship absorbs the next bolt and bursts. An unused charge carries into the next wave.

## Play

Open **Balde Space Invaders.app** on Apple Silicon, or run the source with a Python interpreter that has Pygame installed. On the original Intel Python setup, run `/usr/local/bin/python3 play.py` from the project directory.

Press Enter to start. P pauses or resumes play, and M toggles the arcade sounds for shots, hits, wave clears, and losses. After a loss, press R to use one of three restarts. Each restart begins at wave one with zero points. Once the restarts are spent, Enter starts a new game. Q or Escape quits. On macOS the personal best is saved in `~/Library/Application Support/Balde Space Invaders/best.txt`.

## Browser release on itch.io

The web build uses Pygbag 0.9.3 and needs network access to its hosted Python runtime. In a Python 3.11 environment, install `pygbag==0.9.3`, make FFmpeg available on your PATH, then run `./build-web.sh`. The upload file is `dist/balde-space-invaders-web.zip`.

Create an HTML project on itch.io, upload the ZIP intact, select **This file will be played in the browser**, and set the embed to **800 × 600**. Preview the draft before publishing. Click inside the game and press Enter. Use a desktop keyboard. Browser scores are saved locally when the browser permits storage. Click the upper-right fullscreen button to enlarge the game. Escape returns to the embedded view and preserves your run. Q returns to the title screen in the browser.

## Build the Apple Silicon app

From the project directory, using native Python 3.11:

```sh
python3.11 -m venv .venv-build
source .venv-build/bin/activate
python -m pip install pygame==2.6.1 pyinstaller==6.22.3
./build-mac.sh
```

The standalone app is in `dist/Balde Space Invaders.app`. This is a local build. Public distribution requires a separate release check on a second Mac and, for a standard Gatekeeper launch experience, Developer ID signing and notarization.
