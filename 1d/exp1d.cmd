#!/bin/bash

set -x  # echo commands

time ./crc8_bqm_emb.py -f 'exp1d.{0:04d}.txt' \
    -n 400 \
    -t 4 \
    -c 00011111 \
    -i 00000000 \
    -d xxxxxxxx xxxxxxxx xxxxxxxx xxxxxxxx xxxxxxxx xxxxxxxx xxxxxxxx

