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

## How this project may be useful to you

This project may be useful to you even if you are not interested in a cyclic
redundancy check algorithm.

It shows a way of representing a problem in terms of combinational logic gates.
Many different problems can be represented this way.

It shows a clean way of organizing a project in three parts.

(1) The first part formulates a problem in terms that a D-Wave quantum computer
can work on, searches for ways to fit the problem to a particular D-Wave quantum
computer, and stores the problem fittings (embeddings) in files for later use.

(2) The second part reads an embedding, submits the problem to the D-Wave
quantum computer for execution via the Leap cloud platform, and writes the
results to a file for later validation and interpretation.

(3) The third part examines the results obtained from the D-Wave quantum
computer, checks them for validity, and prints a tabular summary.

## Source code

### `crc8_formulate_problem.py`
- Reads command-line parameters defining the problem to be solved.
- Builds a constraint satisfaction problem (CSP).
- Translates the CSP into a binary quadratic model (BQM).
- Searches for embeddings that fit the BQM onto the QPU of one particular
quantum computer.
- For each embedding found, stores parameters, BQM, and embedding in a file,
using JSON for complicated data structures.
- Does not use QPU time.

### `crc8_run_on_qpu.py`
- Reads a file written by `crc8_formulate_problem.py` containing parameters,
BQM, and embedding.
- Runs the problem on the quantum computer remotely via the Leap cloud platform.
- Stores samples (answers) in a file using JSON.
- Uses QPU time.

### `crc8_check_results.py`
- Reads a file written by `crc8_run_on_qpu.py` containing samples (answers) from
the QPU.
- Extracts desired information from the sample data structures.
- Checks the validity of the samples and prints a table.
- Does not use QPU time.

### `crc8.py`
- Contains functions used by the programs above.

## Workflow

In a nutshell, the workflow is:
- Run`crc8_formulate_problem.py` to formulate the problem and fit it to the QPU
of a specific quantum computer.  Check the max chain len and avg chain len
statistics of the embeddings and pick one with short chains.
- Run `crc8_run_on_qpu.py` to submit the problem to the quantum computer, read
samples (answers) from the QPU, and store the results in a file.
- Run `crc8_check_results.py` to extract data from the results file, check
validity of samples (answers), and print a table.

## Worked example problems

### Problems worked on Advantage_system1.1 in October 2020

```
          Explanatory text file
Folder    (inside the folder)
------    ---------------------
11a       README.exp11a.txt
11m       README.exp11m.txt
11u       README.exp11u.txt
11w       README.exp11w.txt
```

### Problems worked on a previous-generation 2000Q

```
          Explanatory text file
Folder    (inside the folder)
------    ---------------------
1a        exp1a.notes.txt
1b        exp1b.notes.txt
1c        exp1c.notes.txt
1d        exp1d.notes.txt
1e        exp1e.notes.txt
1f        exp1f.notes.txt
2         exp2.notes.txt
3         exp3.notes.txt
4         exp4.notes.txt
```

## Usage of programs illustrated with examples

### Usage of `crc8_formulate_problem.py`

`crc8_formulate_problem.py` builds a CSP, translates the CSP to a BQM, and
attempts to find embeddings.

For example:

The following little `bash` script, `exp11a.cmd`, invokes
`crc8_formulate_problem.py` using the `time` command to measure CPU time and
elapsed wall-clock time.
It can take hours to make hundreds of attempts to find an embedding.
It is worth it, because some embeddings are much better than others.
This program does not use QPU time, only CPU time on the local computer.

```
#!/bin/bash

set -x  # echo commands

time ./crc8_formulate_problem.py -f 'exp11a.{0:04d}.txt' \
    -n 400 \
    -t 4 \
    -c 00011111 \
    -i 00000000 \
    -d xxxxxxxx xxxxxxxx xxxxxxxx xxxxxxxx
```

The output of the script can be redirected to a log file and monitored
using `tail`.  In `bash`:

```
./exp11a.cmd > exp11a.log 2>&1 &
tail -100f exp11a.log
```

The parameter `-f 'exp11a.{0:04d}.txt'` specifies a Python string formatting
pattern to be used for the names of output files containing variables, BQM,
embedding, etc.  Files will be named `exp11a.0000.txt`, `exp11a.0001.txt`, ...
`exp11a.0399.txt`.

The parameter `-n 400` specifies the number of BQM embedding attempts.
For each successful attempt, a file named according to the `-f` pattern will
be written.

The parameter `-t 4` means use four threads.  If in doubt, specify `-t 1`.

The parameter `-c 00011111` specifies the 8-bit cyclic redundancy check (CRC8)
value, in binary (base 2) notation.  The string must contain exactly eight `0`,
`1`, and/or `x` characters, with `x` denoting an unknown (unfixed) bit for which
the QPU will find a value.

The parameter `-i 00000000` specifies the 8-bit initialization value for the
CRC8 algorithm, in binary.  The string must contain exactly eight `0`, `1`,
and/or `x` characters.

The parameter `-d xxxxxxxx xxxxxxxx xxxxxxxx xxxxxxxx` specifies four data
octets (8-bit bytes), in binary.  Each data octet string must contain exactly
eight `0`, `1`, and/or `x` characters.  If more than one data octet is
specified, the octets must be separated by spaces as in this example.

Note that any or all of the CRC8, init, or data bits can be marked as unknown
with an `x`.  If all of the bits are marked as unknown, the quantum computer
will attempt to pull values out of thin air that satisfy the constraints of the
CRC8 algorithm!  See experiment 4, `4/exp4.notes.txt`.

It does not make sense to fix all of the CRC8, init, and data bits with `0` or
`1` values.  Then there is no problem for the quantum computer to solve.

### Usage of `crc8_run_on_qpu.py`

`crc8_run_on_qpu.py` submits a problem to a quantum computer remotely via the
Leap platform.

For example:

```
./crc8_run_on_qpu.py -f exp11a.0315.txt -s exp11a.0315.sampset.01.txt -n 1000
```

The parameter `-f exp11a.0315.txt` specifies the input file containing
variables, BQM, embedding, etc that was written by `crc8_formulate_problem.py`.

The parameter `-n 1000` tells the program to read 1000 samples (answers) from
the QPU.

The parameter `-s exp11a.0315.sampset.01.txt` specifies the output file in which
the samples (answers) obtained from the QPU will be written using JSON.  This is
an ASCII text file, but it is hard to interpret by eye.

### Usage of `crc8_check_results.py`

`crc8_check_results.py` reads a file of samples (answers) from the QPU,
unpacks the information, checks validity of samples, and prints a table.
It does not use QPU time.

```
./crc8_check_results.py -f exp11a.0315.txt -s exp11a.0315.sampset.01.txt | egrep valid
crc8 00011111 init 00000000 data 10010010 11101100 10101100 10100100 energy   44.0 computed-crc8 00011111 valid
crc8 00011111 init 00000000 data 11111101 10111010 01101100 11010011 energy   46.0 computed-crc8 00011111 valid
crc8 00011111 init 00000000 data 11011100 10010111 01001101 01101011 energy   48.0 computed-crc8 00011111 valid
crc8 00011111 init 00000000 data 01111110 00000110 10111000 11011111 energy   55.0 computed-crc8 00011111 valid
```

The parameter `-f exp11a.0315.txt` specifies the input file containing variables,
BQM, embedding, etc that was written by `crc8_formulate_problem.py`.

The parameter `-s exp11a.0315.sampset.01.txt` specifies the input file of samples
(answers) from the QPU that was written by `crc8_run_on_qpu.py`.

In the output table, `crc8` designates the CRC8 value obtained from the QPU.
The `init` and `data` values obtained from the QPU are used to calculate a CRC8
value on the local conventional computer.  This is designated as `computed-crc8`
in the table.  If `crc8` and `computed-crc8` match, the answer from the QPU is
valid, and the word `valid` appears at the end of the row in the table.

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

Imagine that for each blob of data to be sent to Earth, the spacecraft computes
some kind of checksum, hash, or message digest using an algorithm that can be
expressed in terms of combinational logic.  The spacecraft transmits the message
digest and the size of the blob to Earth.  A quantum computer on Earth runs a
program along the lines of the one implemented in this project to discover
possible values for the data blob.  The candidate reconstructed data blob is
transmitted to the spacecraft.  The spacecraft responds "Yes, you got it" or
"No, that is wrong; here is another message digest computed with algorithm B".

In early October 2020, using the new D-Wave Advantage_system1.1 with 5436
qubits, it is possible to use the software contained in this project to
discover at least 32 octets (256 bits) of unknown data consistent with a given
8-bit CRC and a given 8-bit init value.  (See experiment `11w`.)
It seems reasonable to hope
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

## License

Copyright (c) 2018-2020 Scott Davis

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

    http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.

Please acknowledge my work if it is useful to you.


