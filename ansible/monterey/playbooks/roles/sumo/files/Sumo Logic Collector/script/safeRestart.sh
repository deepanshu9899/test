#!/bin/bash

homeDir="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
homeDir="$(dirname "$homeDir")"
logFile="$homeDir"/logs/safeRestart.log

echo "[$(date)]start safeRestart" >> "$logFile"
echo "[$(date)]PID $$ | HomeDir $homeDir" >> "$logFile"

echo "$homeDir"/collector stop >> "$logFile"
"$homeDir"/collector stop >> "$logFile" 2>&1

echo "$homeDir"/collector remove >> "$logFile"
"$homeDir"/collector remove >> "$logFile" 2>&1

echo systemctl daemon-reload >> "$logFile"
systemctl daemon-reload >> "$logFile" 2>&1

echo "$homeDir"/collector install >> "$logFile"
$"$homeDir"/collector install >> "$logFile" 2>&1

echo "$homeDir"/collector start >> "$logFile"
"$homeDir"/collector start >> "$logFile" 2>&1

echo "[$(date)]safeRestart complete" >> "$logFile"
