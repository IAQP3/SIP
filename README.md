# Install:
sudo apt-get install python3-pip libglib2.0-dev

sudo pip3 install bluepy

# Run manually:
sudo python3 bluepy_scanner_test.py

# Add startup service with auto-restart:
1. Copy iaqp.service to /lib/systemd/system/

2. Run commands:

sudo systemctl daemon-reload

sudo systemctl enable iaqp.service

This script runs run.sh script.

# Setup connection to open WiFi:
Add open WiFi network to /etc/wpa_supplicant/wpa_supplicant.conf
