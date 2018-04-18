# Install:
sudo apt-get install python3-pip libglib2.0-dev
sudo pip3 install bluepy

# Run:
sudo python3 bluepy_scanner_test.py

# Add startup script to rc.local and log to file:
sudo sed -i -e '$i sudo python3 /home/pi/SIP/bluepy_scanner_test.py >> /home/pi/SIP/logs/main.log 2>&1\n' /etc/rc.local
