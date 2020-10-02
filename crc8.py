# Copyright (c) 2018-2020 Scott Davis
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


from dwave.system.samplers import DWaveSampler
import dwavebinarycsp as dbc


#===============================================================================
def calc_crc8(init_val, octet_list):

    c0 = c1 = c2 = c3 = c4 = c5 = c6 = c7 = 0

    # Extract bits of init value
    init_str = '{0:08b}'.format(init_val)
    i7 = int(init_str[0], 2)
    i6 = int(init_str[1], 2)
    i5 = int(init_str[2], 2)
    i4 = int(init_str[3], 2)
    i3 = int(init_str[4], 2)
    i2 = int(init_str[5], 2)
    i1 = int(init_str[6], 2)
    i0 = int(init_str[7], 2)

    for n in range(0, len(octet_list)):

        if n > 0:
            # Use crc8 of previous octet as init for this octet
            i0 = c0
            i1 = c1
            i2 = c2
            i3 = c3
            i4 = c4
            i5 = c5
            i6 = c6
            i7 = c7

        # Extract bits of data octet
        data_str = '{0:08b}'.format(octet_list[n])
        d7 = int(data_str[0], 2)
        d6 = int(data_str[1], 2)
        d5 = int(data_str[2], 2)
        d4 = int(data_str[3], 2)
        d3 = int(data_str[4], 2)
        d2 = int(data_str[5], 2)
        d1 = int(data_str[6], 2)
        d0 = int(data_str[7], 2)

        # XOR init bits with data bits
        e0 = xor_i0_d0 = (i0 + d0) % 2
        e1 = xor_i1_d1 = (i1 + d1) % 2
        e2 = xor_i2_d2 = (i2 + d2) % 2
        e3 = xor_i3_d3 = (i3 + d3) % 2
        e4 = xor_i4_d4 = (i4 + d4) % 2
        e5 = xor_i5_d5 = (i5 + d5) % 2
        e6 = xor_i6_d6 = (i6 + d6) % 2
        e7 = xor_i7_d7 = (i7 + d7) % 2

        xor_e0_e1 = (e0 + e1) % 2
        xor_e0_e4 = (e0 + e4) % 2
        c5        = (e1 + e5) % 2
        xor_e2_e6 = (e2 + e6) % 2
        xor_e3_e7 = (e3 + e7) % 2
        xor_e0_e1_e3_e7 = (xor_e0_e1 + xor_e3_e7) % 2
        c0 = (xor_e0_e1 + xor_e2_e6) % 2
        c1 = (xor_e2_e6 + e5) % 2
        c2 = (c5 + e4) % 2
        c3 = (xor_e0_e4 + e3) % 2
        c4 = (xor_e0_e1_e3_e7 + e6) % 2
        c6 = (xor_e0_e4 + e7) % 2
        c7 = (xor_e0_e1_e3_e7 + e2) % 2

    crc8_str = str(c7) + str(c6) + str(c5) + str(c4) + str(c3) + str(c2) + str(c1) + str(c0)

    crc8_val = int(crc8_str, 2)  # string represents number in base 2

    return crc8_val

    
#===============================================================================
# init_bit_names should be a list of eight distinct names such as, for example:
# ['i0.0', 'i0.1', 'i0.2', 'i0.3', 'i0.4', 'i0.5', 'i0.6', 'i0.7']
# or
# ['i1.0', 'i1.1', 'i1.2', 'i1.3', 'i1.4', 'i1.5', 'i1.6', 'i1.7']
#
# data_bit_names should be a list of eight distinct names such as, for example:
# ['d0.0', 'd0.1', 'd0.2', 'd0.3', 'd0.4', 'd0.5', 'd0.6', 'd0.7']
# or
# ['d1.0', 'd1.1', 'd1.2', 'd1.3', 'd1.4', 'd1.5', 'd1.6', 'd1.7']
#
# crc8_bit_names should be a list of eight distinct names such as, for example:
# ['c0.0', 'c0.1', 'c0.2', 'c0.3', 'c0.4', 'c0.5', 'c0.6', 'c0.7']
# or
# ['c1.0', 'c1.1', 'c1.2', 'c1.3', 'c1.4', 'c1.5', 'c1.6', 'c1.7']

def build_crc8_circuit(csp, init_bit_names, data_bit_names, crc8_bit_names):

    # Compose bit/qubit names

    i0 = init_bit_names[0]
    i1 = init_bit_names[1]
    i2 = init_bit_names[2]
    i3 = init_bit_names[3]
    i4 = init_bit_names[4]
    i5 = init_bit_names[5]
    i6 = init_bit_names[6]
    i7 = init_bit_names[7]

    d0 = data_bit_names[0]
    d1 = data_bit_names[1]
    d2 = data_bit_names[2]
    d3 = data_bit_names[3]
    d4 = data_bit_names[4]
    d5 = data_bit_names[5]
    d6 = data_bit_names[6]
    d7 = data_bit_names[7]

    c0 = crc8_bit_names[0]
    c1 = crc8_bit_names[1]
    c2 = crc8_bit_names[2]
    c3 = crc8_bit_names[3]
    c4 = crc8_bit_names[4]
    c5 = crc8_bit_names[5]
    c6 = crc8_bit_names[6]
    c7 = crc8_bit_names[7]

    # Compose names for qubits representing XORed init and data bits
    e0 = '%s^%s' % (i0, d0)
    e1 = '%s^%s' % (i1, d1)
    e2 = '%s^%s' % (i2, d2)
    e3 = '%s^%s' % (i3, d3)
    e4 = '%s^%s' % (i4, d4)
    e5 = '%s^%s' % (i5, d5)
    e6 = '%s^%s' % (i6, d6)
    e7 = '%s^%s' % (i7, d7)

    # Compose names for qubits representing XORs of XORs
    xor_e0_e1 = '(%s)^(%s)' % (e0, e1)
    xor_e0_e4 = '(%s)^(%s)' % (e0, e4)
    xor_e2_e6 = '(%s)^(%s)' % (e2, e6)
    xor_e3_e7 = '(%s)^(%s)' % (e3, e7)
    xor_e0_e1_e3_e7 = '(%s)^(%s)' % (xor_e0_e1, xor_e3_e7)

    # Build logic gates using bit/qubit names

    e0_gate = dbc.factories.xor_gate([ i0, d0, e0 ])
    e1_gate = dbc.factories.xor_gate([ i1, d1, e1 ])
    e2_gate = dbc.factories.xor_gate([ i2, d2, e2 ])
    e3_gate = dbc.factories.xor_gate([ i3, d3, e3 ])
    e4_gate = dbc.factories.xor_gate([ i4, d4, e4 ])
    e5_gate = dbc.factories.xor_gate([ i5, d5, e5 ])
    e6_gate = dbc.factories.xor_gate([ i6, d6, e6 ])
    e7_gate = dbc.factories.xor_gate([ i7, d7, e7 ])

    xor_e0_e1_gate       = dbc.factories.xor_gate([ e0, e1, xor_e0_e1 ])
    xor_e0_e4_gate       = dbc.factories.xor_gate([ e0, e4, xor_e0_e4 ])
    c5_gate              = dbc.factories.xor_gate([ e1, e5, c5 ])
    xor_e2_e6_gate       = dbc.factories.xor_gate([ e2, e6, xor_e2_e6 ])
    xor_e3_e7_gate       = dbc.factories.xor_gate([ e3, e7, xor_e3_e7 ])
    xor_e0_e1_e3_e7_gate = dbc.factories.xor_gate([ xor_e0_e1, xor_e3_e7, xor_e0_e1_e3_e7 ])
    c0_gate = dbc.factories.xor_gate([ xor_e0_e1, xor_e2_e6, c0 ])
    c1_gate = dbc.factories.xor_gate([ xor_e2_e6,        e5, c1 ])
    c2_gate = dbc.factories.xor_gate([ c5,               e4, c2 ])  # c5 is e1^e5
    c3_gate = dbc.factories.xor_gate([ xor_e0_e4,        e3, c3 ])
    c4_gate = dbc.factories.xor_gate([ xor_e0_e1_e3_e7,  e6, c4 ])
    c6_gate = dbc.factories.xor_gate([ xor_e0_e4,        e7, c6 ])
    c7_gate = dbc.factories.xor_gate([ xor_e0_e1_e3_e7,  e2, c7 ])

    # Add constraints to CSP
    csp.add_constraint(e0_gate)
    csp.add_constraint(e1_gate)
    csp.add_constraint(e2_gate)
    csp.add_constraint(e3_gate)
    csp.add_constraint(e4_gate)
    csp.add_constraint(e5_gate)
    csp.add_constraint(e6_gate)
    csp.add_constraint(e7_gate)
    csp.add_constraint(xor_e0_e1_gate)
    csp.add_constraint(xor_e0_e4_gate)
    csp.add_constraint(c5_gate)
    csp.add_constraint(xor_e2_e6_gate)
    csp.add_constraint(xor_e3_e7_gate)
    csp.add_constraint(xor_e0_e1_e3_e7_gate)
    csp.add_constraint(c0_gate)
    csp.add_constraint(c1_gate)
    csp.add_constraint(c2_gate)
    csp.add_constraint(c3_gate)
    csp.add_constraint(c4_gate)
    csp.add_constraint(c6_gate)
    csp.add_constraint(c7_gate)

    return csp


