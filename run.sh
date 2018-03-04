#!/usr/bin/env bash
CUDA_VISIBLE_DEVICES="" nohup './main.py' &
nohup './train.py' &