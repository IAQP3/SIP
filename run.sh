#!/bin/bash

python3 /home/pi/SIP/bluepy_scanner_test.py >> /home/pi/SIP/logs/main.log 2>&1

#run error script if python crashes
python3 /home/pi/SIP/error.py

