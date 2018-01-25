#!/usr/bin/env bash
PROFILE="${1}"
TARGET="target"
CONFIG="${TARGET}/config/"

#  BUILD MODULES
docker build -t iris:${PROFILE} iris/
docker build -t hephaestus:${PROFILE} hephaestus/

# rm -rf "${TARGET}" 
mkdir -p "${CONFIG}"
cp -r "./deployment/${PROFILE}/." "${CONFIG}"
mv "${CONFIG}/docker-compose.yml" "${TARGET}" 

pushd "$TARGET"
docker-compose up