#!/bin/bash

set -x  # echo commands

time ./crc8_bqm_emb.py -f 'exp2.{0:04d}.txt' \
    -n 400 \
    -t 4 \
    -c 0x0111x1 \
    -i 000xx000 \
    -d 10101100 00011100 xxxxxxxx xxxxxxxx xxxxxxxx xxxxxxxx 01110001 11110000

