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


import argparse
import configparser
import itertools
import json
from dwave.system.samplers import DWaveSampler
import dwavebinarycsp as dbc
import dimod
from dimod.serialization.json import DimodEncoder
import minorminer
import crc8


#===============================================================================
def crc8_bqm_emb():

    # Parse command-line arguments

    parser = argparse.ArgumentParser(description =
        'Get command-line parameters.')
    parser.add_argument('-f', required=True, dest='cfpat',    action='store',
        help='output bqm/embedding file name pattern -- e.g., foo.{0:04d}.txt')
    parser.add_argument('-n', required=True, dest='ntries',   action='store',
        type=int,
        help='number of tries to find an embedding')
    parser.add_argument('-t', required=True, dest='nthreads', action='store',
        type=int,
        help='number of threads')
    parser.add_argument('-c', required=True, dest='crc8_str', action='store',
        help='crc8 octet -- string of eight 0/1/x')
    parser.add_argument('-i', required=True, dest='init_str', action='store',
        help='init octet -- string of eight 0/1/x')
    parser.add_argument('-d', required=True, dest='data',     action='store',
        nargs='+', metavar='OCTET',
        help='data octets -- each a string of eight 0/1/x')

    args = parser.parse_args()
    cfpat    = args.cfpat
    ntries   = args.ntries
    nthreads = args.nthreads
    crc8_str = args.crc8_str
    init_str = args.init_str
    data     = args.data

    # For each embedding, write a config file containing variables, bqm,
    # embedding, etc
    config = configparser.ConfigParser()
    config['System'] = {}
    config['Variables'] = {}
    config['Problem'] = {}
    config['Notes'] = {}

    num_data_octets = len(data)

    if 8 != len(crc8_str):
        print('crc8 must have exactly eight 0/1/x characters')
        quit()

    if 8 != len(init_str):
        print('init must have exactly eight 0/1/x characters')
        quit()

    for n in range(0, num_data_octets):
        if 8 != len(data[n]):
            print('data octets must have exactly eight 0/1/x characters each')
            quit()

    # Assign 0/1 values to fixed variables c0.0, c0.1, ... c0.7 representing
    # crc8 output bits
    fixed_crc8_var_dict = {}
    crc8_decision_var_list = []
    for j, x in zip(range(0, len(crc8_str)), reversed(crc8_str)):
        cvar = 'c0.' + str(j)  # e.g., 'c0.0'
#       print(cvar, x)
        if   '0' == x:
            fixed_crc8_var_dict[cvar] = 0
        elif '1' == x:
            fixed_crc8_var_dict[cvar] = 1
        elif 'x' == x:
            # not fixed -- a decision variable
            crc8_decision_var_list.append(cvar)
        else:
            raise ValueError('Unknown character in crc8 string -- not 0/1/x')

#   print('fixed_crc8_var_dict:\n', fixed_crc8_var_dict)
#   print('crc8_decision_var_list:\n', crc8_decision_var_list)

    config['Variables']['fixed_crc8_var_dict_json'] = json.dumps(fixed_crc8_var_dict)
    config['Variables']['crc8_decision_var_list_json'] = json.dumps(crc8_decision_var_list)

    # Assign 0/1 values to fixed variables i0.0, i0.1, ... i0.7 representing
    # init bits
    fixed_init_var_dict = {}
    init_decision_var_list = []
    for j, x in zip(range(0, len(init_str)), reversed(init_str)):
        ivar = 'i0.' + str(j)  # e.g., 'i0.0'
#       print(ivar, x)
        if   '0' == x:
            fixed_init_var_dict[ivar] = 0
        elif '1' == x:
            fixed_init_var_dict[ivar] = 1
        elif 'x' == x:
            # not fixed -- a decision variable
            init_decision_var_list.append(ivar)
        else:
            raise ValueError('Unknown character in init string -- not 0/1/x')

#   print('fixed_init_var_dict:\n', fixed_init_var_dict)
#   print('init_decision_var_list:\n', init_decision_var_list)

    config['Variables']['fixed_init_var_dict_json'] = json.dumps(fixed_init_var_dict)
    config['Variables']['init_decision_var_list_json'] = json.dumps(init_decision_var_list)

    # Assign 0/1 values to fixed variables representing input data bits.
    # For data octet 0: d0.0, d0.1, d0.2, ... d0.7
    # For data octet 1: d1.0, d1.1, d1.2, ... d1.7
    # For data octet 2: d2.0, d2.1, d2.2, ... d2.7
    # and so forth
    fixed_data_var_dict = {}
    data_decision_var_list = []
    for n in range(0, num_data_octets):
        for j, x in zip(range(0, len(data[n])), reversed(data[n])):
            dvar = 'd%d.' % (n) + str(j)  # e.g., 'd0.1' or 'd1.7'
#           print(dvar, x)
            if   '0' == x:
                fixed_data_var_dict[dvar] = 0
            elif '1' == x:
                fixed_data_var_dict[dvar] = 1
            elif 'x' == x:
                # not fixed -- a decision variable
                data_decision_var_list.append(dvar)
            else:
                raise ValueError('Unknown character in octet %d string -- not 0/1/x' % (n,))

#   print('fixed_data_var_dict:\n', fixed_data_var_dict)
#   print('data_decision_var_list:\n', data_decision_var_list)

    config['Variables']['num_data_octets'] = '{0:d}'.format(num_data_octets)
    config['Variables']['fixed_data_var_dict_json'] = json.dumps(fixed_data_var_dict)
    config['Variables']['data_decision_var_list_json'] = json.dumps(data_decision_var_list)

    # Get sampler
    sampler = DWaveSampler()
    _, target_edgelist, target_adjacency = sampler.structure

#   sampler_properties = sampler.properties
#   sampler_parameters = sampler.parameters
#   print('sampler properties:\n', sampler_properties)
#   print('sampler parameters:\n', sampler_parameters)
#   config['System']['sampler_properties_json'] = json.dumps(sampler_properties)
#   config['System']['sampler_parameters_json'] = json.dumps(sampler_parameters)

    # Get constraint satisfaction problem
    csp = dbc.ConstraintSatisfactionProblem('BINARY')

    # Compose bit/qubit names for crc8 circuits -- one circuit per octet of data
    for n in range(0, num_data_octets):
        # nth circuit
        if 0 == n:
            init_bit_names = ['i0.%d' % (i,) for i in range(0, 8)]
        else:
            # init is crc8 of previous octet
            init_bit_names = ['c%d.%d' % (n-1, i) for i in range(0, 8)]
        data_bit_names     = ['d%d.%d' % (n,   i) for i in range(0, 8)]
        crc8_bit_names     = ['c%d.%d' % (n,   i) for i in range(0, 8)]
        csp = crc8.build_crc8_circuit(csp, init_bit_names, data_bit_names, crc8_bit_names)

    # Get binary quadratic model
    bqm = dbc.stitch(csp, min_classical_gap = 0.1)

    # Fix qubits representing known bits of crc8 octet
    for var, value in fixed_crc8_var_dict.items():
        bqm.fix_variable(var, value)

    # Fix qubits representing known bits of init octet
    for var, value in fixed_init_var_dict.items():
        bqm.fix_variable(var, value)

    # Fix qubits representing known bits of data octets
    for var, value in fixed_data_var_dict.items():
        bqm.fix_variable(var, value)

    print('============================================================')
    print('Binary quadratic model with fixed variables:')
    print(bqm)

    # Write binary quadratic model to config file using JSON
    bqm_json = json.dumps(bqm, cls=DimodEncoder)
    config['Problem']['bqm_json'] = bqm_json

    # Try ntries times to find an embedding
    for n in range(0, ntries):

        print('============================================================')

        print('Attempt no. %d' % (n,))

        # Get an embedding
        embedding = minorminer.find_embedding(bqm.quadratic, target_edgelist,
            max_no_improvement=10,  # default 10
            chainlength_patience=10,  # default 10
            threads=nthreads,  # default 1
            verbose=1)  # default 0
        if bqm and not embedding:
            print('No embedding found')
            continue  # try again
        print(embedding)

        # Write embedding to config file using JSON
        emb_json = json.dumps(embedding)
        config['Problem']['embedding_json'] = emb_json

        # Gather statistics about the embedding
        embedding_len = len(embedding)
        max_chain_len = max(len(chain) for chain in embedding.values())
        avg_chain_len = float(sum(len(chain) for chain in embedding.values())) / float(embedding_len)

        print('embedding len {0:d}'.format(embedding_len))
        print('max chain len {0:d}'.format(max_chain_len))
        print('avg chain len {0:f}'.format(avg_chain_len))

        # Write crc8, init, data, and embedding statistics to config file
        config['Notes']['crc8_str'] = crc8_str
        config['Notes']['init_str'] = init_str
        config['Notes']['data'] = ' '.join(data)
        config['Notes']['embedding_len'] = '{0:d}'.format(embedding_len)
        config['Notes']['max_chain_len'] = '{0:d}'.format(max_chain_len)
        config['Notes']['avg_chain_len'] = '{0:f}'.format(avg_chain_len)

        # Write config file
        cfname = cfpat.format(n)
        with open(cfname, 'w') as configfile:
            config.write(configfile)

    print('============================================================')


#===============================================================================
# Run the program

crc8_bqm_emb()


