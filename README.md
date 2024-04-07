# Westinghouse

Custom GPIO actions for a radio restoration.

## Installation

Modify `westinghouse.service` file line 9 to point to script location, default is `/home/rpi/westinghouse/westinghouse.py`

Then run these commands:

`sudo chmod +x westinghouse.service`

`cp westinghouse.service /usr/lib/systemd/system/`

`sudo systemctl daemon-reload`

`sudo systemctl enable westinghouse.service`

`sudo systemctl start westinghouse.service`

## Monitoring

`sudo systemctl status westinghouse.service`

`sudo journalctl -b -u westinghouse`