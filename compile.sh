#!/bin/sh

PYTHONOPTIMIZE=1 pyinstaller --clean --onefile game.py -n pong --workpath build --distpath . --add-data "font/*:." --add-data="sfx/*:." --add-data="image/*:."