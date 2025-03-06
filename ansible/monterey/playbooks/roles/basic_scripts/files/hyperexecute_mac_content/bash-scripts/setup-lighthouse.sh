#!/bin/bash

echo "action : " $1

if [[ $1 == "new" ]];
then
	echo "### Proceeding with a new setup for lighthouse. ###"
else
	echo "### Proceeding with an update to the existing lighthouse setup, so removing existing first. ###"
	cd /Users/ltuser/lrc/lambda-node-remote-client/
	rm -fr lighthouse-binaries/
	cd bash-scripts/
	rm -fr lighthouse-perfms.sh
fi

cd /Users/ltuser/lrc/lambda-node-remote-client/

echo "### Downloading lighthouse binaries ###"
curl -O https://lambda-devops-use-only.s3.amazonaws.com/magicleap/lighthouse/lighthouse-binaries.zip

echo "## Unzip lighthouse binaries ###"
unzip lighthouse-binaries.zip
chmod 755 lighthouse-binaries/

echo "## Removing lighthouse-binaries.zip file ###"
rm -fr lighthouse-binaries.zip

cd bash-scripts/

echo "### Downloading lighthouse script ###"
curl -O https://lambda-devops-use-only.s3.amazonaws.com/magicleap/lighthouse/lighthouse-perfms.sh
chmod 755 lighthouse-perfms.sh

echo "done for lighthouse setup :)"
