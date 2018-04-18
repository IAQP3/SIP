# Install:
sudo apt-get install python3-pip libglib2.0-dev

sudo pip3 install bluepy

# Run:
sudo python3 bluepy_scanner_test.py

# Run command to add startup script:
sudo sed -i -e '$i /home/pi/SIP/run.sh\n' /etc/rc.local

# Setup connection to open WiFi:
Add to /etc/network/interfaces

auto lo

iface lo inet loopback

iface eth0 inet dhcp


allow-hotplug wlan0

iface wlan0 inet manual

wpa-roam /etc/wpa_supplicant/wpa_supplicant.conf

iface default inet dhcp

