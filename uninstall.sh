sudo systemctl stop radioraspi.service
sudo systemctl disable radioraspi.service
sudo rm /usr/lib/systemd/system/radioraspi.service
sudo systemctl daemon-reload