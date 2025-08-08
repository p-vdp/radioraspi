# radioraspi

Custom GPIO actions for a radio restoration built on a Raspberry Pi 5.

## Install

Create Moode install on SD card using RPi Imager: https://www.raspberrypi.com/software/

ssh into Raspberry Pi

`sudo apt update`

`sudo apt upgrade`

`sudo apt install gh`

`gh auth login`

use token

`gh repo clone p-vdp/radioraspi`

`sudo bash ./radioraspi/install.sh`

## Monitoring

`sudo systemctl status radioraspi.service`

or

`sudo journalctl -b -u radioraspi`