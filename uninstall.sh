sudo systemctl stop westinghouse.service
sudo systemctl disable westinghouse.service
sudo rm /usr/lib/systemd/system/westinghouse.service
sudo systemctl daemon-reload
sudo python -m pip uninstall gpiod --break-system-packages