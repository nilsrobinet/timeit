#!/bin/bash

# Install script for installing and building the app
# TODO: remove build once CI/CD is set up

if [ "$EUID" -eq 0 ]; then
    echo "Run as unprivileged user"
    exit 1
fi
SCRIPT_DIR=$( cd -- "$( dirname -- "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )
ROOT_DIR=$SCRIPT_DIR

echo "Running from $ROOT_DIR"

# Step 1: build  --------------------------------
cd $ROOT_DIR/frontend
npm run build

EXIT_CODE=$?
if [ $EXIT_CODE -ne 0 ]; then
    echo "Build failed with code $EXIT_CODE exiting."
    exit $EXIT_CODE
fi

# Step 2: install -------------------------------

APPDIR=/opt/webapps/timeit

echo "Copying files to $APPDIR"

mkdir -p $APPDIR

echo "Copying files..."
cp -r $ROOT_DIR/config $APPDIR/config
cp -r $ROOT_DIR/src $APPDIR/src
cp -r $ROOT_DIR/static $APPDIR/static
cp $ROOT_DIR/main.py $APPDIR/
cp $ROOT_DIR/requirements.txt $APPDIR/

echo "Setting up virtualenv..."
python3 -m venv $APPDIR/venv

echo "Activating venv..."
source $APPDIR/venv/bin/activate

echo "Installing dependencies..."
pip install -r $APPDIR/requirements.txt

cp $ROOT_DIR/util/timeit.service /etc/systemd/system/timeit.service

systemctl daemon-reload
systemctl enable timeit.service
echo "Service enabled."

deactivate

echo "Done."
