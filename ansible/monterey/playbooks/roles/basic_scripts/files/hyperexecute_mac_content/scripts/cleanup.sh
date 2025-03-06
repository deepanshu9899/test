#!/bin/bash

echo "Starting basic cleanup process"

echo "sleeping for 5 seconds to give leeway for recovery from infinite restart loop"
sleep 5

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
defaults write NSGlobalDomain AppleShowScrollBars -string "Always"
defaults delete -g AppleInterfaceStyle
sudo mkdir -p /Applications/"Sumo Logic Collector"/config/creds
sudo chmod +x /Users/ltuser/scripts/hypertest_sanity.sh
sudo touch /Applications/"Sumo Logic Collector"/config/creds/main.properties

### Running Mac Checkup ###
echo "Running Mac Checkup Script..."
mac_checkup_az_blob_url="https://hyperexecutestage.blob.core.windows.net/mac-utilities/mac_checkup.bash"
mac_checkup_path="/Users/ltuser/hyperexecute_mac_content/scripts/mac_checkup.bash"
mac_checkup_path_temp="/Users/ltuser/hyperexecute_mac_content/scripts/temp_mac_checkup.bash"
## Download the file using curl with error handling
if curl -o $mac_checkup_path_temp -L $mac_checkup_az_blob_url; then
    echo "File downloaded successfully."
    rm -rf $mac_checkup_path
    mv $mac_checkup_path_temp $mac_checkup_path
else
    echo "Download failed."
fi

chmod 755 $mac_checkup_path
sudo sh $mac_checkup_path

## Function to run the sanity script
hypertest_sanity() {
  echo "Running the sanity script..."
  export job-working-directory=$(pwd)
  # Add the command to run the sanity script here
  sudo bash /Users/ltuser/scripts/hypertest_sanity.sh
}

## Function to perform the reboot with a wait
perform_reboot() {
  echo "Rebooting the system..."
  sudo reboot
}

## Function to display countdown timer
countdown() {
  local duration=$1
  local remaining=$duration

  while [ $remaining -gt 0 ]; do
    printf "Sleeping for %s seconds...\033[0K\r" "$remaining"
    sleep 1
    ((remaining--))
  done

  echo -e "\n"
}

## Call the functions in sequence
hypertest_sanity
countdown 15
perform_reboot
