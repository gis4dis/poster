#!/usr/bin/env bash
pwd
mkdir modules/mc-client -p
cd modules/mc-client
pwd

curl -L https://github.com/gis4dis/mc-client/releases/download/v1.4/release.tar.gz | tar xvz