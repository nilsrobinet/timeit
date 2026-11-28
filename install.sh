#!/bin/bash
set -euo pipefail

# Install script for installing and building the app

if [[ "$EUID" -ne 0 ]]; then
    echo "Run as root!" >&2
    exit 1
fi
SCRIPT_DIR=$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" &>/dev/null && pwd)
ROOT_DIR=$SCRIPT_DIR

echo "Running from $ROOT_DIR"

# Step 1: build  --------------------------------
cd "$ROOT_DIR/frontend"
npm install
npm run build

# Step 2: install -------------------------------

APPDIR=/opt/webapps/timeit

echo "Copying files to $APPDIR"

mkdir -p "$APPDIR/config" "$APPDIR/src" "$APPDIR/static"

echo "Copying files..."
cp "$ROOT_DIR/config/app.conf" "$APPDIR/config/app.conf"
if [[ ! -f "$APPDIR/config/userconf.yaml" ]]; then
    cp "$ROOT_DIR/config/userconf.yaml" "$APPDIR/config/userconf.yaml"
fi
cp -a "$ROOT_DIR/src/." "$APPDIR/src/"
cp -a "$ROOT_DIR/static/." "$APPDIR/static/"
cp "$ROOT_DIR/main.py" "$APPDIR/main.py"
cp "$ROOT_DIR/requirements.txt" "$APPDIR/requirements.txt"

echo "Setting up virtualenv..."
python3 -m venv "$APPDIR/venv"

echo "Installing dependencies..."
"$APPDIR/venv/bin/python" -m pip install -r "$APPDIR/requirements.txt"

cp "$ROOT_DIR/util/timeit.service" /etc/systemd/system/timeit.service

systemctl daemon-reload
systemctl enable timeit.service
systemctl restart timeit.service
echo "Service enabled and restarted."

echo "Done."