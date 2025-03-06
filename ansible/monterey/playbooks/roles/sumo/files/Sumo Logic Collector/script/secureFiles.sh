#!/bin/bash
if [ "$BASH_VERSION" = '' ]; then
    echo "This script is for bash only, try 'bash secureFiles.sh'"
    exit 999
fi

# usage: secureFiles.sh [homeDir] [runAs]
# Make collector directory accessible only from "sumologic_collector" group members
# Arguments: homeDir - optional, the root directory of collector installation (if not specified, use parent folder of this script)
#            runAs   - optional, the name of account who launch the collector (if not specified, use current user; e.g. 'root' under 'sudo')

homeDir=$1
runAs=$2
group=sumologic_collector

if [ "$homeDir" = "" ]; then
    homeDir="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
    homeDir="$(dirname "$homeDir")"
fi
if [ ! -d "$homeDir" ]; then
    echo "Directory $homeDir is not found!"
    exit 1
fi

if [ "$runAs" = "" ]; then
    runAs=$USER
else
    regex=".*[^a-zA-Z0-9\._].*"
    if echo $runAs | grep -E -q $regex; then
        echo "RunAs should only contains letter, number, underscore or dot."
        exit 2
    fi
fi
echo "Start securing files under $homeDir with [$runAs:$group]..."

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

new_group() {
    unameStr="$(uname)"
    groupName=$1
    if [ "$unameStr" = "FreeBSD" ]; then
        pw groupadd $groupName &>/dev/null
    elif [ "$unameStr" = "Darwin" ]; then
        dscl . create /Groups/$groupName &>/dev/null
        dscl . delete /Groups/$groupName gid &>/dev/null
        dscl . append /Groups/$groupName gid 3377 &>/dev/null
    else
        groupadd $groupName &>/dev/null
    fi
}

join_group() {
    unameStr="$(uname)"
    groupName=$1
    userName=$2
    if [ "$unameStr" = "FreeBSD" ]; then
        pw groupmod $groupName -M $userName &>/dev/null
    elif [ "$unameStr" = "Darwin" ]; then
        dseditgroup -o edit -a $userName -t user $groupName &>/dev/null
    else
        usermod -a -G $groupName $userName &>/dev/null
    fi
}

get_member() {
    unameStr="$(uname)"
    groupName=$1
    if [ "$unameStr" = "FreeBSD" ]; then
        pw groupshow $groupName 
    elif [ "$unameStr" = "Darwin" ]; then
        dscl . -read /Groups/$groupName GroupMembership
    else
        getent group $groupName
    fi
}

remove_group() {
    unameStr="$(uname)"
    groupName=$1
    if [ "$unameStr" = "FreeBSD" ]; then
        pw groupdel $groupName &>/dev/null
    elif [ "$unameStr" = "Darwin" ]; then
        dscl . delete /Groups/$groupName &>/dev/null
    else
        groupdel $groupName &>/dev/null
    fi
}

secure_folders_permission() {
    find "$1" -type d -exec chmod 770 {} &>/dev/null \;
}

secure_files_permission() {
    find "$1" ! -name 'wrapper' -type f -exec chmod o=-r-w-x {} &>/dev/null \;
}

get_group $group &>/dev/null
if [ $? -ne 0 ]; then
    new_group $group &>/dev/null
fi
join_group $group $runAs &>/dev/null
get_member $group | grep $runAs &>/dev/null
if [ $? -ne 0 ]; then
    echo "Fail to add account $runAs into group $group; abort."
    exit 3
fi
join_group $group root &>/dev/null
get_member $group | grep root &>/dev/null
if [ $? -ne 0 ]; then
    echo "Fail to add account 'root' into group $group; ignore."
fi

chown -R $runAs:$group "$homeDir" &>/dev/null
if [ $? -ne 0 ]; then
    echo "Fail to set ownership to $runAs:$group; abort."
    exit 4
fi

secure_folders_permission "$homeDir" &>/dev/null
if [ $? -ne 0 ]; then
    echo "Fail to set folders permission; abort."
    exit 5
fi

secure_files_permission "$homeDir" &>/dev/null
if [ $? -ne 0 ]; then
    echo "Fail to set files permission; abort."
    exit 6
fi

echo "Securing files succeed."