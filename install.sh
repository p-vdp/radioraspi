sudo chmod +x radioraspi.service
sudo cp ./radioraspi.service /usr/lib/systemd/system/
sudo systemctl daemon-reload
sudo systemctl enable radioraspi.service
sudo systemctl start radioraspi.service
sudo systemctl status radioraspi.service
