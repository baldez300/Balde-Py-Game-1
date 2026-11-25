#!/bin/sh
set -eu
cd "$(dirname "$0")"
if [ "$(python3 -c 'import platform; print(platform.machine())')" != arm64 ]; then
    echo "Use an arm64 Python environment to build the Apple Silicon app." >&2
    exit 1
fi
mkdir -p build
PYINSTALLER_CONFIG_DIR="$PWD/build/cache" python3 -m PyInstaller --noconfirm --windowed --onedir \
    --name "Balde Space Invaders" --target-arch arm64 --specpath "$PWD/build" \
    --add-data "$PWD/background.jpg:." --add-data "$PWD/player.png:." \
    --add-data "$PWD/enemy.png:." --add-data "$PWD/bullet.png:." "$PWD/play.py"
