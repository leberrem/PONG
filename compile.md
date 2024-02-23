```
sudo pip3 install numba
sudo pip3 install pyinstaller

PYTHONOPTIMIZE=1 pyinstaller --clean --onefile game.py -n pong --workpath build --distpath . --add-data "font/*:." --add-data="sfx/*:." --add-data="image/*:."
```