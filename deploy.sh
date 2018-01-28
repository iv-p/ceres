#!/usr/bin/env bash

tar -czf ceres.tzar \
    config/ \
    data-distributor/ \
    data-fetcher/ \
    decision-maker/ \
    manager/ \
    price-predictor/ \
    stock-manager/ \
    build.sh

ssh root@159.65.24.75 "cd /opt/target && docker-compose kill && cd /opt && rm -rf *"

scp ceres.tzar root@159.65.24.75:/tmp/

ssh root@159.65.24.75 "cd /opt && tar -zxf /tmp/ceres.tzar && /opt/build.sh live"