#!/bin/bash
set -x
# updating binaries
source ~/.bash_profile
echo "updating binaries"
/bin/bash /Users/ltuser/scripts/download_binaries.sh

# giving permissions to updated binaries
echo "executing permissions"
/Users/ltuser/scripts/permissions.sh

#starting necessary services
echo "staring foreman"
cd /Users/ltuser/foreman
/bin/bash -c "/Users/ltuser/scripts/foreman.sh"

#starting cleanup
#echo "starting Cleanup"
#/Users/ltuser/scripts/cleanup.sh
echo "all operations finished"
