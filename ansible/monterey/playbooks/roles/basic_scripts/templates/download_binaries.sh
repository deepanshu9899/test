#!/bin/bash

# cp ~/binaries/hypertest-foreman /Users/ltuser/foreman/foreman
# chmod +x /Users/ltuser/foreman/foreman
/usr/local/bin/azcopy copy "https://{% if hostvars[inventory_hostname].ENV == 'stage' %}hyperexecutestage{% else %}hypertestproduction{% endif %}.blob.core.windows.net/{% if 'debug' in group_names and hostvars[inventory_hostname].ENV != 'stage' %}ht-binaries-beta{% else %}ht-binaries{% endif %}/darwin/hypertest-foreman" "/Users/ltuser/foreman/foreman"
