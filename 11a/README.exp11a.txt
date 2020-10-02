$ cat exp11a.cmd
#!/bin/bash

set -x  # echo commands

time ./crc8_formulate_problem.py -f 'exp11a.{0:04d}.txt' \
    -n 400 \
    -t 4 \
    -c 00011111 \
    -i 00000000 \
    -d xxxxxxxx xxxxxxxx xxxxxxxx xxxxxxxx

$ ./exp11a.cmd > exp11a.log 2>&1 &

$ ls exp11a.[0-9][0-9][0-9][0-9].txt | wc -l
400

All 400 attempts to find an embedding succeeded.

$ egrep 'max_chain_len' exp11a.[0-9][0-9][0-9][0-9].txt | sort -k 3n | head -12
exp11a.0315.txt:max_chain_len = 3  <<--
exp11a.0003.txt:max_chain_len = 4
exp11a.0009.txt:max_chain_len = 4
exp11a.0012.txt:max_chain_len = 4
exp11a.0013.txt:max_chain_len = 4
exp11a.0018.txt:max_chain_len = 4
exp11a.0024.txt:max_chain_len = 4
exp11a.0025.txt:max_chain_len = 4
exp11a.0026.txt:max_chain_len = 4
exp11a.0029.txt:max_chain_len = 4
exp11a.0033.txt:max_chain_len = 4
exp11a.0037.txt:max_chain_len = 4

$ egrep 'avg_chain_len' exp11a.[0-9][0-9][0-9][0-9].txt | sort -k 3n | head -12
exp11a.0139.txt:avg_chain_len = 1.416667
exp11a.0069.txt:avg_chain_len = 1.432292
exp11a.0148.txt:avg_chain_len = 1.432292
exp11a.0025.txt:avg_chain_len = 1.447917
exp11a.0037.txt:avg_chain_len = 1.447917
exp11a.0237.txt:avg_chain_len = 1.447917
exp11a.0271.txt:avg_chain_len = 1.447917
exp11a.0136.txt:avg_chain_len = 1.453125
exp11a.0172.txt:avg_chain_len = 1.453125
exp11a.0315.txt:avg_chain_len = 1.453125  <<--
exp11a.0330.txt:avg_chain_len = 1.453125
exp11a.0221.txt:avg_chain_len = 1.458333

Embedding 0315 appears to be a good candidate.
Its max chain len, 3, is the shortest found in 400 embedding attempts.
Its avg chain len, 1.453125, is not much more than the lowest average.

$ ./crc8_run_on_qpu.py -f exp11a.0315.txt -s exp11a.0315.sampset.01.txt -n 1000
$ ./crc8_run_on_qpu.py -f exp11a.0315.txt -s exp11a.0315.sampset.02.txt -n 1000

$ ./crc8_check_results.py -f exp11a.0315.txt -s exp11a.0315.sampset.01.txt > exp11a.0315.sampset.01.all.txt
$ ./crc8_check_results.py -f exp11a.0315.txt -s exp11a.0315.sampset.02.txt > exp11a.0315.sampset.02.all.txt

$ cat exp11a.0315.sampset.0[1-2].all.txt | egrep valid
crc8 00011111 init 00000000 data 10010010 11101100 10101100 10100100 energy   44.0 computed-crc8 00011111 valid
crc8 00011111 init 00000000 data 11111101 10111010 01101100 11010011 energy   46.0 computed-crc8 00011111 valid
crc8 00011111 init 00000000 data 11011100 10010111 01001101 01101011 energy   48.0 computed-crc8 00011111 valid
crc8 00011111 init 00000000 data 01111110 00000110 10111000 11011111 energy   55.0 computed-crc8 00011111 valid
crc8 00011111 init 00000000 data 10111000 00011100 00101001 10110011 energy   47.0 computed-crc8 00011111 valid
crc8 00011111 init 00000000 data 01001011 10110110 11100000 10010111 energy   48.0 computed-crc8 00011111 valid
crc8 00011111 init 00000000 data 11000010 00110001 01001000 10101101 energy   48.0 computed-crc8 00011111 valid
crc8 00011111 init 00000000 data 00100010 01011000 10101001 10100110 energy   62.0 computed-crc8 00011111 valid

$ cat exp11a.0315.sampset.0[1-2].all.txt | egrep valid | wc -l
8

$ cat exp11a.0315.sampset.0[1-2].all.txt | egrep valid | cut -c29-68
data 10010010 11101100 10101100 10100100
data 11111101 10111010 01101100 11010011
data 11011100 10010111 01001101 01101011
data 01111110 00000110 10111000 11011111
data 10111000 00011100 00101001 10110011
data 01001011 10110110 11100000 10010111
data 11000010 00110001 01001000 10101101
data 00100010 01011000 10101001 10100110

$ cat exp11a.0315.sampset.0[1-2].all.txt | egrep valid | cut -c29-68 | sort | uniq -c
      1 data 00100010 01011000 10101001 10100110
      1 data 01001011 10110110 11100000 10010111
      1 data 01111110 00000110 10111000 11011111
      1 data 10010010 11101100 10101100 10100100
      1 data 10111000 00011100 00101001 10110011
      1 data 11000010 00110001 01001000 10101101
      1 data 11011100 10010111 01001101 01101011
      1 data 11111101 10111010 01101100 11010011

In two runs of 1000 samples each, the Advantage_system1.1 solver found
8 distinct valid solutions.

