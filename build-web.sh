#!/bin/sh
set -eu
cd "$(dirname "$0")"
stage=build/web-source/balde-space-invaders
mkdir -p "$stage/sounds" dist
cp play.py "$stage/main.py"
cp background.jpg player.png enemy.png bullet.png "$stage/"
cp player.png "$stage/favicon.png"
for sound in shot hit over clear; do
    ffmpeg -loglevel error -y -i "sounds/$sound.wav" -ac 2 -c:a vorbis -strict experimental "$stage/sounds/$sound.ogg"
done
python3 -m pygbag --build --archive --no_opt --width 800 --height 600 \
    --title "Balde Space Invaders" "$stage"
# Pygbag requests the tarball on localhost and the APK on itch.io.
webdir="$stage/build/web"
python3 - "$webdir/index.html" <<'PYTHON'
import sys
from pathlib import Path

index = Path(sys.argv[1])
html = index.read_text()
if "</body>" not in html:
    raise SystemExit("Could not locate the end of the Pygbag page")
index.write_text(html.replace("</body>", Path("web/fullscreen.html").read_text() + "</body>", 1))
PYTHON
(cd "$webdir" && zip -q ../web.zip index.html balde-space-invaders.tar.gz)
unzip -tq "$stage/build/web.zip"
cp "$stage/build/web.zip" dist/balde-space-invaders-web.zip
