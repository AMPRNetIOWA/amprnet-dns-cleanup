#!/usr/bin/python3

'''
This script reads in the AMPRNet DNS zone file (ampr.org) and
an encap file (encap.txt) and determines whether there is a
gateway assocated with each AMPRnet (44.0.0.0/8) A record in
the zone file.
'''
'''
    Copyright (C) 2016  Neil Johnson

    This program is free software; you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation; either version 2 of the License, or
    (at your option) any later version.

    This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License along
    with this program; if not, write to the Free Software Foundation, Inc.,
    51 Franklin Street, Fifth Floor, Boston, MA 02110-1301 USA.
'''

import ipaddress

subnets={}

ampr_net = ipaddress.ip_network('44.0.0.0/8')

# Loop through encap file
with open('encap.txt', encoding='utf-8') as encap_file:
    for encap_line in encap_file:
        encap_line = encap_line.rstrip()

        if (encap_line.find('private') != -1):
            encap_fields = encap_line.split()
            network = encap_fields[2]
            octet_list = network.split('.')

            if ( len(octet_list) == 3 ):
                slash_loc = network.find('/')
                real_network = network[0:slash_loc] + ".0" + network[slash_loc:]
            elif ( len(octet_list) == 2 ):
                slash_loc = network.find('/')
                real_network = network[0:slash_loc] + ".0.0" + network[slash_loc:]
            elif ( len(octet_list) == 1 ):
                slash_loc = network.find('/')
                real_network = network[0:slash_loc] + ".0.0.0" + network[slash_loc:]
            else:
                real_network = network

            subnets[encap_fields[4]] = ipaddress.ip_network(real_network)

addr_list=[]

# Loop through dns zone file
with open('ampr.org', encoding='utf-8') as a_file:
    for a_line in a_file:
        a_line = a_line.rstrip()

        # pull out all lines that are IN records (but not NS records)
        if ((a_line.find('IN') != -1) and (a_line.find('NS') == -1)):
            fields = a_line.split()

            # Pull out 'A' records only
            if ( fields[2] == 'A' ):
                address = ipaddress.ip_address(fields[3])
                addr_list.append(address)

# Lookup gateway for address
for address in sorted(addr_list):
    # Check if address is in 44.0.0.0/8
    if (address in ampr_net):
        for gateway in sorted(subnets.keys()):
            if ( address in subnets[gateway] ):
                print('\"', str(address), '\",\"', str(gateway),'\"')
                break
        else:
            print('\"', address, '\",\"GATEWAY_NOT_FOUND\"')
