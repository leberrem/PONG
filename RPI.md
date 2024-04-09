# Installation

## Pre-requs

Distribution Raspberry Pi OS Lite

```
sudo apt update
sudo apt upgrade
sudo apt install python3-pygame
sudo apt install python3-colorama
```

## Resolution 800*600

```
sudo vi /boot/config.txt
# -----------------
hdmi_group=2
hdmi_mode=9
# -----------------
```

## Copy game

```
scp -r game.* font sound image pi@192.168.1.58:~/.
```

## auto-start

```
sudo vi /lib/systemd/system/pong.service
# --------------
[Unit]
Description=Start Pong

[Service]
Environment=DISPLAY=:0
WorkingDirectory=/home/pi
ExecStart=/bin/bash -c '/usr/bin/python3 game.py --fullscreen --rotate-txt --use-gpio --use-mouse > game.out 2>&1'
Restart=always
RestartSec=10s
KillMode=process
TimeoutSec=infinity

[Install]
WantedBy=multi-user.target
# --------------
```
```
sudo systemctl daemon-reload
sudo systemctl enable pong.service
```
# custom cmdline for Splash screen

add at the end of line

```
sudo vi /boot/cmdline.txt
# -----------------
logo.nologo vt.global_cursor_default=0 quiet loglevel=0 splash
# -----------------
```

# custom boot for Splash screen

```
sudo vi /boot/config.txt
# -----------------
boot_delay=0
disable_splash=1
# -----------------
```

# Splash screen

```
sudo apt install fbi
```
```
sudo vi /lib/systemd/system/splashscreen.service
# -----------------
[Unit]
Description=Splash screen
DefaultDependencies=no
After=local-fs.target

[Service]
ExecStart=/usr/bin/fbi -d /dev/fb0 --noverbose -a /home/pi/image/mkl.png
StandardInput=tty
StandardOutput=tty

[Install]
WantedBy=basic.target
# -----------------
```
```
sudo systemctl enable splashscreen
```

## change locale

Run: sudo raspi-config
- 5 Localisation Options
- L1 Locale
