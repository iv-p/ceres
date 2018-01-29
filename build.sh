#!/usr/bin/env bash
TARGET="target"
CONFIG="${TARGET}/config/"
PROFILE="${1}"

#  BUILD MODULES
docker build -t ceres config/

docker build -t data-fetcher data-fetcher/
docker build -t data-distributor data-distributor/
docker build -t decision-maker decision-maker/
docker build -t price-predictor price-predictor/
docker build -t stock-manager stock-manager/
docker build -t manager manager/

# rm -rf "${TARGET}" 
mkdir -p "${CONFIG}"
cp -r "./config/." "${CONFIG}"
mv "${CONFIG}/docker-compose.yml" "${TARGET}" 

pushd "$TARGET"
docker-compose down
if [ ! -z "${PROFILE}" ] 
then
    docker-compose up -d
else
    docker-compose up
fi