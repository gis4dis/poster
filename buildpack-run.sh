#!/usr/bin/env bash

pwd
mkdir modules/mc-client -p
rm -rf modules/mc-client/*
cd modules/mc-client
pwd
ls -la

curl -L https://github.com/gis4dis/mc-client/releases/download/v1.16/release.tar.gz | tar xvz
