# PONG

![Logo](image/logo.png)

Pong game in python with particules effects

## Hardware

- 1x 17'' LCD Screen with sound
- 1x Raspberry Pi 3 Model A+
- 1x Raspberry Pi Power Supply
- 2x EG STARTS Arcade Spinner for Arcade1UP
- 1x Thunderstick Studios 12 in 1 Interface Board
- 3x Concave black short arcade button - 28mm
- 1x Power switch

## Instruction for Raspberry Pi

[Raspberry Pi](RPI.md)

## Instruction for Compile

[Compilation](compile.md)

## Help

```
./game.py --help

     _______  _______  __    _  _______      _   .
    |       ||       ||  |  | ||       |    | | . _
    |    _  ||   _   ||   |_| ||    ___|    | |! |_|
    |   |_| ||  | |  ||       ||   | __     | | '
    |    ___||  |_|  ||  _    ||   ||  |    | |  '
    |   |    |       || | |   ||   |_| |    | |
    |___|    |_______||_|  |__||_______|    |_|

    Parameters:

    --help : This help message
    --no-effect : Disable visual effects
    --no-sound : Disable sound effects
    --fullscreen : Display in fullscreen
    --use-mouse : Use mouse control (useful for spinner)
    --revert-x-axis : Use GPIO (useful for spinner)
    --revert-y-axis : Use GPIO (useful for spinner)
    --rotate-txt : Rotate texte to play face-to-face
    --use-gpio : Use GPIO (useful for Raspberry)
    --help-gpio : Help on GPIO (useful for Raspberry)
    --show-fps : View Framerate
```

## Help GPIO

```
./game.py --help-gpio

        **************************************************************************************
        *                            RASPBERRY Pi GPIO Connector                             *
        **************************************************************************************
        *                     |                                         |                    *
        *                     |                  1   2                  |                    *
        *                     |            +3V3 [ ] [ ] +5V             |                    *
        *                     |  SDA1 / GPIO  2 [ ] [ ] +5V             |                    *
        *                     |  SCL1 / GPIO  3 [ ] [ ] GND             |                    *
        *                     |         GPIO  4 [ ] [ ] GPIO 14 / TXD0  |                    *
        *                     |             GND [ ] [ ] GPIO 15 / RXD0  |                    *
        *                     |         GPIO 17 [ ] [ ] GPIO 18         |                    *
        *                     |         GPIO 27 [ ] [ ] GND ------------|------[SWITCH LEFT] *
        *                     |         GPIO 22 [ ] [ ] GPIO 23 --------|------[SWITCH LEFT] *
        *                     |            +3V3 [ ] [ ] GPIO 24         |                    *
        *                     |  MOSI / GPIO 10 [ ] [ ] GND ------------|-----[SWITCH RIGHT] *
        *                     |  MISO / GPIO  9 [ ] [ ] GPIO 25 --------|-----[SWITCH RIGHT] *
        *                     |  SCLK / GPIO 11 [ ] [ ] GPIO  8 / CE0#  |                    *
        *                     |             GND [ ] [ ] GPIO  7 / CE1#  |                    *
        *                     | ID_SD / GPIO  0 [ ] [ ] GPIO  1 / ID_SC |                    *
        *                     |         GPIO  5 [ ] [ ] GND ------------|-----[SWITCH RESET] *
        *                     |         GPIO  6 [ ] [ ] GPIO 12 --------|-----[SWITCH RESET] *
        *                     |         GPIO 13 [ ] [ ] GND             |                    *
        *                     |  MISO / GPIO 19 [ ] [ ] GPIO 16 / CE2#  |                    *
        *                     |         GPIO 26 [ ] [ ] GPIO 20 / MOSI  |                    *
        *                     |             GND [ ] [ ] GPIO 21 / SCLK  |                    *
        *                     |                 39  40                  |                    *
        *                     |                                         |                    *
        **************************************************************************************
```