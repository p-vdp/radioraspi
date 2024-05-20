# Westinghouse

Custom GPIO actions for a radio restoration.

## Install GPIOD

    sudo python -m pip install gpiod --break-system-packages

## Service Installation

Modify `westinghouse.service` file line 9 to point to script location, default is `/home/rpi/westinghouse/westinghouse.py`

Then run these commands:

    sudo chmod +x westinghouse.service
    sudo cp westinghouse.service /usr/lib/systemd/system/
    sudo systemctl daemon-reload
    sudo systemctl enable westinghouse.service
    sudo systemctl start westinghouse.service

## Monitoring

`sudo systemctl status westinghouse.service`

or

`sudo journalctl -b -u westinghouse`