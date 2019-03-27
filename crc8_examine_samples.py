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
import crc8


#===============================================================================
def crc8_examine_samples():

    # Parse command-line arguments

    parser = argparse.ArgumentParser(description =
        'Get command-line parameters.')
    parser.add_argument('-f', required=True, dest='cfname', action='store',
        help='input config file containing variables, bqm, embedding, etc')
    parser.add_argument('-s', required=True, dest='sfname', action='store',
        help='input file containing samples read from QPU')

    args = parser.parse_args()
    cfname = args.cfname
    sfname = args.sfname

    config = configparser.ConfigParser()
    config.read(cfname)

    fixed_crc8_var_dict    = json.loads(config['Variables']['fixed_crc8_var_dict_json'])
#   crc8_decision_var_list = json.loads(config['Variables']['crc8_decision_var_list_json'])

    fixed_init_var_dict    = json.loads(config['Variables']['fixed_init_var_dict_json'])
#   init_decision_var_list = json.loads(config['Variables']['init_decision_var_list_json'])

    num_data_octets = int(config['Variables']['num_data_octets'])

    fixed_data_var_dict    = json.loads(config['Variables']['fixed_data_var_dict_json'])
#   data_decision_var_list = json.loads(config['Variables']['data_decision_var_list_json'])

    with open(sfname, 'r') as sfile:
        samples = dimod.SampleSet.from_serializable(json.load(sfile))

#   print(samples)

#   print('samples.info:')
#   print(samples.info)

#   print('samples.variables:')
#   print(samples.variables)

#   print('len(samples.variables):')
#   print(len(samples.variables))

#   print('samples.vartype:')
#   print(samples.vartype)

#   print('samples.record:')
#   print(samples.record)

#   print('len(samples.record):')
#   print(len(samples.record))

#   print('len(samples.record[0]):')
#   print(len(samples.record[0]))

#   print('len(samples.record[0][0]):')
#   print(len(samples.record[0][0]))

    nsamples = len(samples.record)

    for samp_num in range(0, nsamples):

        decision_var_dict = dict(zip(samples.variables, samples.record[samp_num][0]))
        energy = float(samples.record[samp_num][1])

        # Merge fixed variables in with decision variables from sample.
        # Resulting dict should contain all crc8, init, and data bits
        combined_var_dict = decision_var_dict.copy()
        combined_var_dict.update(fixed_crc8_var_dict)
        combined_var_dict.update(fixed_init_var_dict)
        combined_var_dict.update(fixed_data_var_dict)

        crc8_ans_str = ''
        # c0.7, c0.6, ... c0.0
        for c_key in ['c0.%d' % (j,) for j in reversed(range(0, 8))]:
            crc8_ans_str += str(combined_var_dict[c_key])
        crc8_val = int(crc8_ans_str, 2)  # string represents number in base 2

        init_ans_str = ''
        # i0.7, i0.6, ... i0.0
        for i_key in ['i0.%d' % (j,) for j in reversed(range(0, 8))]:
            init_ans_str += str(combined_var_dict[i_key])
        init_val = int(init_ans_str, 2)  # string represents number in base 2

        data_ans_str_list = []
        data_val_list = []
        for n in range(0, num_data_octets):
            data_ans_str = ''
            # dn.7, dn.6, ... dn.0
            for d_key in ['d%d.%d' % (n, j) for j in reversed(range(0, 8))]:
                data_ans_str += str(combined_var_dict[d_key])
            data_ans_str_list.append(data_ans_str)
            data_val = int(data_ans_str, 2)  # string represents number in base 2
            data_val_list.append(data_val)

        computed_crc8_val = crc8.calc_crc8(init_val, data_val_list)
        computed_crc8_str = '{0:08b}'.format(computed_crc8_val)
        if computed_crc8_val == crc8_val:
            vstr = 'valid'
        else:
            vstr = ''

        print('crc8', crc8_ans_str,
              'init', init_ans_str,
              'data', ' '.join(data_ans_str_list),  # print list elements separated by spaces
              'energy', '{0:6.1f}'.format(energy),
              'computed-crc8', computed_crc8_str,
              vstr)


#===============================================================================
# Run the program

crc8_examine_samples()


