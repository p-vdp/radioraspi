# Westinghouse

Custom GPIO actions for a radio restoration.
## Install

Create Moode install on SD card using RPi Imager: https://www.raspberrypi.com/software/

ssh into Raspberry Pi

`sudo apt update`

`sudo apt upgrade`

`sudo apt install gh`

`gh auth login`

use token

`gh repo clone p-vdp/westinghouse`

`sudo bash ./westinghouse/install.sh`

## Monitoring

`sudo systemctl status westinghouse.service`

or

`sudo journalctl -b -u westinghouse`