#!/usr/bin/env python3

# Copyright (c) 2018-2019 Scott Davis
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#
# Please acknowledge my work if it is useful to you.


import sys
import argparse
import configparser
import itertools
import json
from dwave.system.samplers import DWaveSampler
import dwave.embedding
import dimod
from dimod.serialization.json import DimodDecoder
import crc8


#===============================================================================
def crc8_qpu():

    # Parse command-line arguments

    parser = argparse.ArgumentParser(description =
        'Get command-line parameters.')
    parser.add_argument('-f', required=True, dest='cfname', action='store',
        help='input config file containing variables, bqm, embedding, etc')
    parser.add_argument('-s', required=True, dest='sfname', action='store',
        help='output file containing samples read from QPU')
    parser.add_argument('-n', required=True, dest='nsamp', action='store', type=int,
        help='number of samples to read from QPU')

    args = parser.parse_args()
    cfname = args.cfname
    sfname = args.sfname
    nsamp = args.nsamp

    config = configparser.ConfigParser()
    config.read(cfname)

    # Get sampler
    sampler = DWaveSampler()
    _, target_edgelist, target_adjacency = sampler.structure

    bqm_json = config['Problem']['bqm_json']
    bqm = json.loads(bqm_json, cls=DimodDecoder)

    embedding_json = config['Problem']['embedding_json']
    embedding = json.loads(embedding_json)

    # Apply embedding to given problem to map it to sampler
    bqm_embedded = dwave.embedding.embed_bqm(bqm, embedding, target_adjacency)

    # Read samples from QPU
    kwargs = {}
    kwargs['num_reads'] = nsamp
    response = sampler.sample(bqm_embedded, **kwargs)

    # Convert back to original problem space
    samples = dwave.embedding.unembed_sampleset(response, embedding, bqm)

    samples_json = json.dumps(samples.to_serializable())

    with open(sfname, 'w') as outfile:
        outfile.write(samples_json)


#===============================================================================
# Run the program

crc8_qpu()


