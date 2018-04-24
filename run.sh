#!/bin/bash

sudo python3 -u /home/pi/SIP/bluepy_scanner_test.py 2>&1 | tee -a /home/pi/SIP/logs/main.log

echo "python crashed"

#run error script if python crashes
sudo python3 /home/pi/SIP/error.py

return 0