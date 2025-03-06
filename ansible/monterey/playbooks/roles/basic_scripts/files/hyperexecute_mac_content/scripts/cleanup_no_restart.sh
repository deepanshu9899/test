#!/bin/bash

echo "Starting basic cleanup process"
sudo rm -rf /Users/ltuser/lrc/lambda-node-remote-client/logs/*
sudo rm /Users/ltuser/lrc/lambda-node-remote-client/*.log
sudo rm /Users/ltuser/lrc/*.log
sudo rm -rf /Users/ltuser/foreman
sudo rm -rf /Users/ltuser/lrc/edge/*
sudo rm -rf /Users/ltuser/.npm*
cp -r /Users/ltuser/hyperexecute_mac_content/foreman /Users/ltuser/
sudo networksetup -setwebproxystate Ethernet off
sudo networksetup -setsecurewebproxystate Ethernet off
sudo networksetup -setautoproxystate Ethernet off
