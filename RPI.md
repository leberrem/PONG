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
scp -r game.* font sound atari@192.168.1.58:~/.
```

## auto-start

```
sudo vi /home/atari/.bashrc
# -----------------
if [[ -z $SSH_TTY ]]
then
    cd /home/atari
    ./game.sh
fi
# -----------------
```

## auto-login

Run: sudo raspi-config
- 1 System Options
- S5 Boot / Auto Login
- B2 Console Autologin

# Remove messages

```
sudo update-rc.d motd remove
sudo su -c 'echo "" > /etc/motd'
sudo rm -f /etc/update-motd.d/*
touch ~/.hushlogin
```

replace "ExecStart=........." command line
```
sudo vi /etc/systemd/system/getty@tty1.service.d/autologin.conf
# -----------------
ExecStart=-/sbin/agetty --skip-login --noclear --noissue --login-options "-f atari" %I $TERM
# -----------------
```

# Splash screen

```
scp -r atari atari@192.168.1.58:~/.
```
```
sudo apt-get -y install plymouth
sudo mv atari /usr/share/plymouth/themes
sudo plymouth-set-default-theme atari
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
