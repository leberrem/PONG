    Update package: sudo apt upgrade

    install plymouth : sudo apt-get install plymouth plymouth-themes

    Disable boot delay : Set boot_delay=0 in /boot/config.txt file

    Change resolution to 800x600 : Set hdmi_group=2 / hdmi_mode=9 in /boot/config.txt file

    Disable rainbow: Set disable_splash=1 in /boot/config.txt file

    reduce kernel output: Add quiet in /boot/cmdline.txt file

    Disable Pi logo's: Add logo.nologo to the /boot/cmdline.txt file

    Mute kernel logs (only show critical errors): Add loglevel=3 to the /boot/cmdline.txt file

    Remove blinking cursor: Add vt.global_cursor_default=0 to the /boot/cmdline.txt file


1.) Change /boot/cmdline.txt

sudo nano /boot/cmdline.txt

Change the console from tty1 to

console=tty3

Add this to the end of the line. 'loglevel=0' removes most of the messages from the boot. You can also use 'loglevel=3', but some boot messages may re-appear.

quiet splash loglevel=0 logo.nologo vt.global_cursor_default=0

If you are going to use Plymouth add this:

plymouth.ignore-serial-consoles

2.) Tell dmesg to be quiet

sudo vi /etc/rc.local

Add this before 'exit 0':

#Suppress Kernel Messages
dmesg --console-off

This should take care of most boot messages this far. #2 also took care of the 'watchdog watchdog0: watchdog did not stop!' message on shutdown for me.

3.) Change the auto login in systemd (Hides the login message when auto-login happens)

sudo vi /etc/systemd/system/autologin\@.service

Change your auto login ExecStart from:

ExecStart=-/sbin/agetty --autologin pi --noclear %I $TERM

To:

ExecStart=-/sbin/agetty --skip-login --noclear --noissue --login-options "-f pi" %I $TERM

Make sure to change 'pi' to the username you use!

OR

Run: sudo raspi-config
Choose option: 1 System Options
Choose option: S5 Boot / Auto Login
Choose option: B2 Console Autologin
Select Finish, and reboot the Raspberry Pi.

4.) Change /etc/pam.d/login (removes the Kernel version from showing when you auto-login)

sudo vi /etc/pam.d/login

Change the line

session    optional   pam_exec.so type=open_session stdout /bin/uname -snrvm

To be

session    optional   pam_exec.so type=open_session stdout

5.) Add .hushlogin

touch ~/.hushlogin

or Remove Message of the Day -MOTD (alternative to 5)

sudo update-rc.d motd remove

6.) Using Plymouth

plymouth-set-default-theme --list

sudo plymouth-set-default-theme yourtheme

sudo plymouthd
sudo plymouth --show-splash
sudo plymouth quit

sudo update-initramfs -c -k $(uname -r)
uname -r
initramfs initrd.img-6.1.21+ followkernel

7.) copy theme

cd /usr/share/plymouth/themes
mkdir atari
chmod 777 atari
scp * pong@192.168.1.48:/usr/share/plymouth/themes/atari

sudo plymouth-set-default-theme atari

sudo vi /usr/share/plymouth/plymouthd.defaults
------------------------------------------------------------------------------------------
# Distribution defaults. Changes to this file will get overwritten during
# upgrades.
[Daemon]
Theme=atari
ShowDelay=20
DeviceTimeout=8
------------------------------------------------------------------------------------------

7.) add game

scp game.py SevenSegment.ttf pong@192.168.1.48:~/.

sudo apt install libsdl*
sudo apt-get install libportmidi-dev

sudo apt-get install python3-pygame
