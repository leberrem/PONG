# Installation

## Pre-requis

Distribution Raspberry Pi OS Lite

```
sudo apt update
sudo apt upgrade
sudo apt install python3-pygame
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
scp -r game.* font sound pi@192.168.1.58:~/.
```

## auto-start

sudo vi /lib/systemd/system/pong.service

# --------------
[Unit]
Description=Start Pong

[Service]
Environment=DISPLAY=:0
WorkingDirectory=/home/pi
ExecStart=/bin/bash -c '/usr/bin/python3 game.py --fullscreen > game.log 2>&1'
Restart=always
RestartSec=10s
KillMode=process
TimeoutSec=infinity

[Install]
WantedBy=multi-user.target
# --------------

sudo systemctl daemon-reload
sudo systemctl enable pong.service

# Splash screen

```
scp -r mkl pi@192.168.1.58:~/.
```
```
sudo apt-get -y install plymouth
sudo mv mkl /usr/share/plymouth/themes
sudo plymouth-set-default-theme mkl
```

# custom cmdline

add at the end of line

```
sudo vi /boot/cmdline.txt
# -----------------
loglevel=3 logo.nologo quiet splash plymouth.ignore-serial-consoles vt.global_cursor_default=0
# -----------------
```

# custom boot

```
sudo vi /boot/config.txt
# -----------------
boot_delay=0
disable_splash=1
# -----------------
```

## change locale

Run: sudo raspi-config
- 5 Localisation Options
- L1 Locale
