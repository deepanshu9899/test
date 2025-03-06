#!/bin/bash
if [ "$BASH_VERSION" = '' ]; then
    echo "This script is for bash only, try 'bash unsecureFiles.sh'"
    exit 999
fi

# usage: unsecureFiles.sh [homeDir]
# Make collector directory accessible from all accounts (for backward compatible)
# Arguments: homeDir - optional, the root directory of collector installation (if not specified, use parent folder of this script)

homeDir=$1

if [ "$homeDir" = "" ]; then
    homeDir="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
    homeDir="$(dirname "$homeDir")"
fi
if [ ! -d "$homeDir" ]; then
    echo "Directory $homeDir is not found!"
    exit 1
fi
echo "Start unsecuring files under $homeDir..."

get_group() {
    unameStr="$(uname)"
    groupName=$1
    if [ "$unameStr" = "FreeBSD" ]; then
        pw groupshow $groupName
    elif [ "$unameStr" = "Darwin" ]; then
        dscl . read /Groups/$groupName
    else
        getent group $groupName
    fi
}

unsecure_folders_permission() {
    find "$1" -type d -exec chmod 755 {} &>/dev/null \;
}

unsecure_files_permission() {
    find "$1" -type f -print | while read one
    do
        if [ -x $one ]; then
            chmod g=+r+x,o=+r+x "$one" &>/dev/null
        else
            chmod g=+r,o=+r "$one" &>/dev/null
        fi
    done
}

unsecure_folders_permission "$homeDir" &>/dev/null
if [ $? -ne 0 ]; then
    echo "Fail to set folders permission; ignore."
fi

unsecure_files_permission "$homeDir" &>/dev/null
if [ $? -ne 0 ]; then
    echo "Fail to set files permission; ignore."
fi

get_group staff &>/dev/null
staff_exist=$?
get_group root &>/dev/null
root_exist=$?

if [ $root_exist -eq 0 ]; then
    chown -R root:root "$homeDir" &>/dev/null
elif [ $staff_exist -eq 0 ]; then
    chown -R root:staff "$homeDir" &>/dev/null
else
    chown -R root: "$homeDir" &>/dev/null
fi
if [ $? -ne 0 ]; then
    echo "Fail to set files permission; ignore."
fi

echo "Unsecuring files succeed."