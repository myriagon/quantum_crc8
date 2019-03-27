# quantum_crc8

## Overview

This project implements an 8-bit cyclic redundancy check (CRC8) algorithm on a
D-Wave quantum computer using the Python 3 programming language, the D-Wave
Ocean software development kit (SDK), and the D-Wave Leap cloud platform.

The CRC8 algorithm is expressed in terms of combinational logic, with qubits in
the quantum processing unit (QPU) representing the binary inputs, outputs, and
interconnections of the logic gates.

The user marks some or all of the CRC8, init, and data bits as unknown.
The quantum computer finds candidates for the unknown bits.  For each sample
(possible solution) read from the QPU, the init and data bits are used to
compute a CRC8 value on a conventional computer.  If the CRC8 from the
quantum computer matches the CRC8 from the conventional computer, the quantum
computer's answer is valid.

Please see "A study of hardware implementations of the CRC computation
algorithms", by Mytsko, Malchukov, Ryzova, and Kim [1].  The particular CRC8
algorithm implemented in this project is based on an example described in that
publication.  I thank the authors and recommend their article as a resource for
understanding this project.

Mytsko et al were thinking of conventional electronic circuitry with a one-way
flow from inputs to outputs.  But in this quantum computer implementation,
there is no direction, only logical relationships among the data, init, and CRC8
bits -- constraints that must be satisfied in order to yield a valid result.
The quantum computer considers all possible combinations of values for the
unknown bits simultaneously and settles on a solution.  This is typically done
hundreds or thousands of times in rapid succession to obtain a set of samples,
some of which are likely to be valid.

## Source code

### `crc8_bqm_emb.py`
- Reads command-line parameters defining the problem to be solved.
- Builds a constraint satisfaction problem (CSP).
- Translates the CSP into a binary quadratic model (BQM).
- Searches for embeddings that fit the BQM onto the QPU of one particular
quantum computer.
- For each embedding found, stores parameters, BQM, and embedding in a file,
using JSON for complicated data structures.
- Does not use QPU time.

### `crc8_qpu.py`
- Reads a file written by `crc8_bqm_emb.py` containing parameters, BQM, and
embedding.
- Runs the problem on the quantum computer remotely via the Leap cloud platform.
- Stores samples (answers) in a file using JSON.
- Uses QPU time.

### `crc8_examine_samples.py`
- Reads a file written by `crc8_qpu.py` containing samples (answers) from the
QPU.
- Extracts desired information from the sample data structures.
- Checks the validity of the samples and prints a table.
- Does not use QPU time.

### `crc8.py`
- Contains functions used by the programs above.

## Examples

Folders `1a`, `1b`, `1c`, `1d`, `1e`, `1f`, `2`, `3`, and `4` contain worked
examples.  In each folder look for a file called `expX.notes.txt`, where `X`
is the experiment name -- e.g., `1a/exp1a.notes.txt`.

In a nutshell, the workflow is:
- Run`crc8_bqm_emb.py` to formulate the problem and fit it to the QPU of a
specific quantum computer.  (All of these examples were executed on a machine
called DW_2000Q_2_1.)  Check the max chain len and avg chain len statistics of
the embeddings and pick one with short chains.
- Run `crc8_qpu.py` to submit the problem to the quantum computer, read samples
(answers) from the QPU, and store the results in a file.
- Run `crc8_examine_samples.py` to extract data from the results file, check
validity of samples (answers), and print a table.

## Details about usage of programs

### Details about `crc8_bqm_emb.py`

The following little `bash` script, `exp1a.cmd`, invokes `crc8_bqm_emb.py`
using the `time` command to measure CPU time and elapsed wall-clock time.
It can take hours to make hundreds of attempts to find an embedding.
It is worth it, because some embeddings are much better than others.
This program does not use QPU time, only CPU time on the local computer.

```$ cat exp1a.cmd
#!/bin/bash

set -x  # echo commands

time ./crc8_bqm_emb.py -f 'exp1a.{0:04d}.txt' \
    -n 400 \
    -t 4 \
    -c 00011111 \
    -i 00000000 \
    -d xxxxxxxx xxxxxxxx xxxxxxxx xxxxxxxx
```

The output of the script can be redirected to a log file and monitored
using `tail`.  In `bash`:

```./exp1a.cmd > exp1a.log 2>&1 &
tail -100f exp1a.log
```

The parameter `-f 'exp1a.{0:04d}.txt'` specifies a Python string formatting
pattern to be used for the names of output files containing variables, BQM,
embedding, etc.  Files will be named `exp1a.0000.txt`, `exp1a.0001.txt`, ...
`exp1a.0399.txt`.

The parameter `-n 400` specifies the number of BQM embedding attempts.
For each successful attempt, a file named according to the `-f` pattern will
be written.

The parameter `-t 4` means use four threads.  If in doubt, specify `-t 1`.

The parameter `-c 00011111` specifies the 8-bit cyclic redundancy check (CRC8)
value, in binary (base 2) notation.

The parameter `-i 00000000` specifies the 8-bit initialization value for the
CRC8 algorithm.

The parameter `-d xxxxxxxx xxxxxxxx xxxxxxxx xxxxxxxx` specifies four data
octets (8-bit bytes).  An `x` means that the value of a bit is unknown
(unfixed).  The quantum computer will find values for the unknown bits.

Note that any or all of the CRC8, init, or data bits can be marked as unknown
with an 'x'.  If all of the bits are marked as unknown, the quantum computer
will attempt to pull values out of thin air that satisfy the constraints of the
CRC8 algorithm!  See experiment 4, `4/exp4.notes.txt`.

It does not make sense to fix all of the CRC8, init, and data bits with 0 or 1
values.  Then there is no problem for the quantum computer to solve.

### Details about `crc8_qpu.py`

```./crc8_qpu.py -f exp1a.0381.txt -s exp1a.0381.sampset.01.txt -n 1000
```

The parameter `-f exp1a.0381.txt` tells the program to use the variables, BQM,
embedding, etc stored in the file `exp1a.0381.txt`, which was written by
`crc8_emb_bqm.py`.

`crc8_qpu.py` submits the problem to the quantum computer remotely via the Leap
platform.

The parameter `-n 1000` tells it to read 1000 samples (answers) from the QPU --
i.e., to execute the program 1000 times in rapid succession.

The parameter `-s exp1a.0381.sampset.01.txt` specifies the name of the file in
which the samples (answers) will be stored using JSON.  This is an ASCII text
file, but it is hard to interpret by eye.

### Details about `crc8_examine_samples.py`

`crc8_examine_samples.py` reads a file of samples (answers) from the QPU,
unpacks the information, checks validity of samples, and pretty-prints a table.
It does not use QPU time.

```./crc8_examine_samples.py -f exp1a.0381.txt -s exp1a.0381.sampset.01.txt | egrep valid
crc8 00011111 init 00000000 data 11010111 11110100 11110111 11101001 energy  120.0 computed-crc8 00011111 valid
crc8 00011111 init 00000000 data 11010111 11100100 11111111 01111001 energy  115.0 computed-crc8 00011111 valid
crc8 00011111 init 00000000 data 11010111 11100100 11111111 01111001 energy   74.0 computed-crc8 00011111 valid
crc8 00011111 init 00000000 data 11010111 11100100 11111111 01111001 energy   92.0 computed-crc8 00011111 valid
crc8 00011111 init 00000000 data 11010111 11100100 11111111 01111001 energy  110.0 computed-crc8 00011111 valid
crc8 00011111 init 00000000 data 11010111 11110100 11110111 11101001 energy  109.0 computed-crc8 00011111 valid
...
```

## System requirements

In order to run this software, you will need to install Python 3, install the
D-Wave Ocean software development kit, and get an account on the D-Wave Leap
cloud platform for remote access to a quantum computer.  I developed and tested
the software initially on macOS, then on Linux.

## Far-out speculation

Thousands of exoplanets have been found, and the tally is growing.  I hope NASA
will send a probe to another planetary system in my lifetime.  I might not live
to see it get there, but I might live to see it get well on the way.

The spacecraft's signals, crossing a vast gulf of space, will be very weak when
they reach Earth.  The spacecraft will have to transmit very slowly so that we
can copy its signals.  On the other hand, the powerful transmitters and huge
antennas of NASA's Deep Space Network (DSN) will be able to transmit data more
rapidly to the spacecraft.  I think that quantum computers could help with the
limited downlink budget problem.

Imagine that for each n-bit blob of data to be sent to Earth, the spacecraft
computes some kind of checksum, hash, or message digest using an algorithm that
can be expressed in terms of combinational logic.  The spacecraft transmits the
message digest to Earth.  A quantum computer on Earth runs a program along the
lines of the one implemented in this project to discover possible values for the
data blob.  The candidate reconstructed blob is transmitted to the spacecraft.
The spacecraft responds "Yes, you got it" or "No, that is wrong; here is another
message digest computed with algorithm B".

Using a D-Wave 2000Q with 2048 qubits, it is possible to use the software
contained in this project to discover as many as 9 octets (72 bits) of unknown
data consistent with a given 8-bit CRC and a given 8-bit init value.  (See
example `1f`.)  The D-Wave team is working on a next-generation machine with
5000 qubits and more interconnections among qubits.  It seems reasonable to hope
that 10 or 20 years from now, when a probe could be reaching the outer limits of
the solar system, hurtling on its way toward another star, quantum computers
with tens of thousands of highly interconnected qubits might be available.  It
might be possible to scale up and refine the concept proven here to discover
thousands of bits of unknown data given a message digest that is much bigger
than 8 bits, but only a tiny fraction of the size of the data.

## References

[1] Evgeniy Mytsko, Andrey Malchukov, Svetlana Ryzova, Valeriy Kim.
A study of hardware implementations of the CRC computation algorithms.
MATEC Web of Conferences 48, 04001 (2016).
DOI: 10.1051/matecconf/20164804001.

[2] Factoring with the D-Wave System.  Jupyter notebook by D-Wave Systems Inc.

## Copyright

Copyright (c) 2018-2019 Scott Davis, myriagon@sddw.net

## License

Apache 2.0

Please acknowledge my work if it is useful to you.

