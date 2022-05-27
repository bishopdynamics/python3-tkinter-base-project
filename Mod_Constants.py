#!/usr/bin/env python3

# Constants Module
#   constant values used everywhere
#   yeah, I know: literally nothing I have in here is a const

# Created 2022 by James Bishop (james@bishopdynamics.com)

import pathlib
from Mod_Util import get_basedir

# static vars

# file paths
APP_FOLDER = get_basedir()
VERSION_FILE = APP_FOLDER.joinpath('VERSION')
COMMIT_ID_FILE = APP_FOLDER.joinpath('commit_id')
# config file lives at ~/.commandexplorer/config.yaml
LOCAL_DATA = pathlib.Path.home().joinpath('.commandexplorer')
CONFIG_FILE = LOCAL_DATA.joinpath('config.yaml')
