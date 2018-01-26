#!/usr/bin/env bash
TARGET="target"
CONFIG="${TARGET}/config/"

#  BUILD MODULES
docker build -t iris iris/
docker build -t janus janus/
docker build -t hephaestus hephaestus/

# rm -rf "${TARGET}" 
mkdir -p "${CONFIG}"
cp -r "./config/." "${CONFIG}"
mv "${CONFIG}/docker-compose.yml" "${TARGET}" 

pushd "$TARGET"
docker-compose up