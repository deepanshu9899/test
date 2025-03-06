#!/bin/bash

ScreenId=$1
width=$2
height=$3

if [ $width == "1366" ] && [ $height == "768" ]
 then 
 width=1024
 height=768
fi

echo $width
echo $height

RES="$width"x"$height"
/Users/ltuser/lrc/displayplacer "id\:$ScreenId res\:$RES scaling\:off"
