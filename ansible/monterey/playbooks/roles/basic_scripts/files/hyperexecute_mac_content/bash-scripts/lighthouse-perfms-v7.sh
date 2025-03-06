#!/bin/bash

cd /Users/ltuser/lrc/lambda-node-remote-client/lighthouse-binaries/$1/node_modules/lighthouse

./lighthouse-cli/index.js $2 --port=9225 --output=json --output=html --output-path=/Users/ltuser/lrc/lambda-node-remote-client/lighthouse-performance-reports/$3/lighthouse/ --enable-error-reporting --preset=desktop
