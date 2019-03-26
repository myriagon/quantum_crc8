#!/bin/bash

set -x  # echo commands

time ./crc8_bqm_emb.py -f 'exp3.{0:04d}.txt' \
    -n 400 \
    -t 4 \
    -c 00110011 \
    -i 00000000 \
    -d 00001111 xxxxxxxx 00110011 xxxxxxxx 01010101 xxxxxxxx 10011001 xxxxxxxx

