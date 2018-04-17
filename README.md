# Setup

Two Python Bluetooth Libraries are needed: pygatt and pygattlib

Pygatt and it’s installation instructions can be found here:
https://github.com/peplin/pygatt

Pygattlib and it’s installation instructions can be found here:
https://bitbucket.org/OscarAcena/pygattlib


# Install dependencies:
sudo apt-get install libboost-python-dev libboost-thread-dev libbluetooth-dev libglib2.0-dev -y

# Install libraries:

sudo pip3 install pygatt pexpect

pip3 download gattlib

tar xvzf ./gattlib-0.20150805.tar.gz

cd gattlib-0.20150805/

sed -ie 's/boost_python-py34/boost_python-py35/' setup.py

sudo pip3 install .

# Run:
sudo python3 bluepy_scanner_test.py