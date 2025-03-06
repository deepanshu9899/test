#!/bin/bash

### Check 1
## Cleanup the Devices Folder
directory="/Users/ltuser/Library/Developer/CoreSimulator"

echo Check if the directory exists ...
if [ -d "$directory/Devices" ]; then
    echo "Directory exists. Deleting..."
    cd /Users/ltuser/Library/Developer/CoreSimulator
    rm -r "$directory/Devices"
    du  -hd1 .
else
    echo "Directory does not exist. Skipping..."
fi

### Check 2
echo Enable the Remote automation ...
sudo /usr/bin/safaridriver --enable

### Check 3
echo Allow the Safari Downloads and Geolocation ...
file_path="/Users/ltuser/hyperexecute_mac_content/PerSitePreferences.db"
file_path_temp="/Users/ltuser/hyperexecute_mac_content/temp_PerSitePreferences.db"
az_blob_url="https://hyperexecutestage.blob.core.windows.net/mac-utilities/PerSitePreferences.db"
safari_preferences_path="/Users/ltuser/Library/Safari/"

## Download the file using curl with error handling
if curl -o $file_path_temp -L $az_blob_url; then
    echo "File downloaded successfully."
    rm -rf $file_path
    mv $file_path_temp $file_path
else
    echo "Download failed."
fi

echo "Now delete the existing PerSitePreferences.db"
cd $safari_preferences_path
sudo rm -rf "PerSitePreferences.db"
ls -lah
echo "Now Copy this file in $safari_preferences_path"
sudo cp -r $file_path $safari_preferences_path
ls -lah
sudo chmod 644 "PerSitePreferences.db"
# echo "Updating default_preferences table..."
sudo sqlite3 /Users/ltuser/Library/Safari/PerSitePreferences.db "UPDATE default_preferences SET default_value='0' WHERE preference='PerSitePreferencesDownloads';"
# sudo sqlite3 /Users/ltuser/Library/Safari/PerSitePreferences.db "UPDATE default_preferences SET default_value='2' WHERE preference='PerSitePreferencesGeolocation';"
# sudo sqlite3 /Users/ltuser/Library/Safari/PerSitePreferences.db "UPDATE default_preferences SET default_value='1' WHERE preference='PerSitePreferencesPopUpWindow';"
# sudo sqlite3 /Users/ltuser/Library/Safari/PerSitePreferences.db "INSERT INTO default_preferences (preference, default_value) VALUES ('PerSitePreferencesDownloads', '0');"
# sudo sqlite3 /Users/ltuser/Library/Safari/PerSitePreferences.db "INSERT INTO default_preferences (preference, default_value) VALUES ('PerSitePreferencesGeolocation', '2');"
# sudo sqlite3 /Users/ltuser/Library/Safari/PerSitePreferences.db "INSERT INTO default_preferences (preference, default_value) VALUES ('PerSitePreferencesPopUpWindow', '1');"


### Check 4
echo "Close any Preview window that is open"
if pgrep -x "Preview" > /dev/null
  then
    # Get the PID of the Preview process
    PID=$(pgrep -x "Preview")

    # Terminate the Preview process
    kill -9 $PID
    echo "Preview has been closed (PID: $PID)."
  else
    echo "Preview is not running."
fi

### Check 5
echo "Turn Off the Bluetooth"
brew install blueutil
blueutil --power 0

