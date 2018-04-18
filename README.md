# Install:
sudo apt-get install python3-pip libglib2.0-dev
sudo pip3 install bluepy

# Run:
sudo python3 bluepy_scanner_test.py

# Add startup script to rc.local and log to file:
sudo sed -i -e '$i sudo python3 /home/pi/SIP/bluepy_scanner_test.py >> /home/pi/SIP/logs/main.log 2>&1\n' /etc/rc.local

# Setup connection to open WiFi:
Add to /etc/network/interfaces

auto lo

iface lo inet loopback
iface eth0 inet dhcp

allow-hotplug wlan0
iface wlan0 inet manual
wpa-roam /etc/wpa_supplicant/wpa_supplicant.conf
iface default inet dhcp
