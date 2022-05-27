#!/bin/bash
# test without building the app

# Created 2022 by James Bishop (james@bishopdynamics.com)

APP_NAME='CommandExplorer'
VENV_NAME='venv'

function bail() {
	echo "An unexpected error occurred"
	exit 1
}

# create venv if missing
if [ ! -d "$VENV_NAME" ]; then
  ./setup-venv.sh || bail
fi

# we need modules in the venv
source "${VENV_NAME}/bin/activate" || bail

# run the python script locally (much faster than waiting for app to build)
python ${APP_NAME}.py || {
  deactivate
  bail
}

# all done, deactivate the venv
deactivate