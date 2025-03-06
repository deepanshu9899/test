#!/bin/bash
source ~/.bashrc
source ~/.profile
vm_id=$(curl http://169.254.169.254/metadata/orka_vm_id | jq -r '.value')

NewHostName=hypertest-stage-${vm_id}

echo New name would be: $NewHostName
sudo scutil --set HostName $NewHostName
echo "Host Name changed"
sudo scutil --set LocalHostName $NewHostName
echo "Local Host Name changed"
sudo scutil --set ComputerName $NewHostName
echo "Computer Name changed"

ChangedName=`hostname`
echo "After changes, Name found to be now: $ChangedName"
