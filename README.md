# Balde Space Invaders

A single-player Python arcade game. Move with the arrow keys and fire with Space. Every 15 hits clears a wave. Six faster enemies appear after a short break. An enemy reaching your row ends the round.

## Play

Open **Balde Space Invaders.app** on Apple Silicon, or run the source with a Python interpreter that has Pygame installed. On the original Intel Python setup, run `/usr/local/bin/python3 play.py` from the project directory.

Press Enter to start. After a loss, press R to use one of three restarts. Each restart begins at wave one with zero points. Once the restarts are spent, Enter starts a new game. Q or Escape quits. On macOS the personal best is saved in `~/Library/Application Support/Balde Space Invaders/best.txt`.

## Build the Apple Silicon app

From the project directory, using native Python 3.11:

```sh
python3.11 -m venv .venv-build
source .venv-build/bin/activate
python -m pip install pygame==2.6.1 pyinstaller==6.22.3
./build-mac.sh
```

The standalone app is in `dist/Balde Space Invaders.app`. This is a local build. Public distribution requires a separate release check on a second Mac and, for a standard Gatekeeper launch experience, Developer ID signing and notarization.
