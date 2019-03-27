#!/bin/bash

set -x  # echo commands

time ./crc8_bqm_emb.py -f 'exp4.{0:04d}.txt' \
    -n 400 \
    -t 4 \
    -c xxxxxxxx \
    -i xxxxxxxx \
    -d xxxxxxxx xxxxxxxx xxxxxxxx xxxxxxxx xxxxxxxx xxxxxxxx

