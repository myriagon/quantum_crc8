#!/bin/bash

set -x  # echo commands

time ./crc8_formulate_problem.py -f 'exp11m.{0:04d}.txt' \
    -n 1000 \
    -t 4 \
    -c 00011111 \
    -i 00000000 \
    -d xxxxxxxx xxxxxxxx xxxxxxxx xxxxxxxx xxxxxxxx xxxxxxxx xxxxxxxx xxxxxxxx \
       xxxxxxxx xxxxxxxx xxxxxxxx xxxxxxxx xxxxxxxx xxxxxxxx xxxxxxxx xxxxxxxx

