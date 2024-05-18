sudo chmod +x westinghouse.service
sudo cp ./westinghouse.service /usr/lib/systemd/system/
sudo systemctl daemon-reload
sudo systemctl enable westinghouse.service
sudo systemctl start westinghouse.service
sudo systemctl status westinghouse.service