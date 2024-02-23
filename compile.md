sudo pip3 install numba
sudo pip3 install pyinstaller

pyinstaller --onefile game.py -n pong --specpath build --workpath build --distpath . --clean