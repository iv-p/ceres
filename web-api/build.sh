#!/usr/bin/env bash

rm -rf ./config
mkdir -p ./config
cp ../config/*.yaml ./config/

pip3 install pymongo flask pyyaml
python3 main.py