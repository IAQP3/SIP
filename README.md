# Install:
sudo apt-get install python3-pip libglib2.0-dev
sudo pip3 install bluepy

# Run:
sudo python3 bluepy_scanner_test.py

# Setup startup script:
sudo sed -i -e '$i sudo python3 ~/SIP/bluepy_scanner_test.py >> ~/SIP/logs/main.log 2>&1\n' /etc/rc.local

This adds following startup script to rc.local: sudo python3 ~/SIP/bluepy_scanner_test.py >> ~/SIP/logs/main.log 2>&1
