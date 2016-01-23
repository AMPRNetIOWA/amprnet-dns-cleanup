#!/usr/bin/python3

'''
This script reads in the AMPRNet DNS zone file (ampr.org) and
an encap file (encap.txt) and determines whether there is a 
gateway assocated with each AMPRnet (44.0.0.0/8) A record in 
the zone file.

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

# Constants
AMPR_NET = ipaddress.ip_network('44.0.0.0/8')
ENCAP_FILE = 'encap.txt'
PORTAL_NETS_FILE = 'portal_nets.txt'
ZONE_FILE = 'ampr.org'

# Loop through portal nets file
subnets=[]
with open(PORTAL_NETS_FILE, encoding='utf-8') as portal_file:
    for portal_line in portal_file:
        portal_line = portal_line.rstrip()

        network = portal_line

        try:
            subnets.append(ipaddress.ip_network(network))
        except ValueError as err:
            print('ERROR: {0}'.format(err))

# Loop through encap file
gw_nets = {}

with open(ENCAP_FILE, encoding='utf-8') as encap_file:
    for encap_line in encap_file:
        encap_line = encap_line.rstrip()

        if (encap_line.find('addprivate') != -1): 
            encap_fields = encap_line.split()
            network = encap_fields[2]

            octet_list = network.split('.')
            slash_loc = network.find('/')

            # Add '.0's to subnet entries so they can be parsed by ipaddress module
            if ( len(octet_list) == 3 ):
                real_network = network[0:slash_loc] + ".0" + network[slash_loc:]
            elif ( len(octet_list) == 2 ):
                real_network = network[0:slash_loc] + ".0.0" + network[slash_loc:]
            elif ( len(octet_list) == 1 ):
                real_network = network[0:slash_loc] + ".0.0.0" + network[slash_loc:]
            elif ( len(octet_list) == 4 ):
                real_network = network
            else:
                print('Error network: ', network)

            gw_nets[ipaddress.ip_network(real_network)] = ipaddress.ip_address(encap_fields[4])


# Loop through dns zone file
addr_list=[]
with open(ZONE_FILE, encoding='utf-8') as a_file:
    for a_line in a_file:
        a_line = a_line.rstrip()

        # pull out all lines that are IN records (but not NS records)
        if ((a_line.find('IN') != -1) and (a_line.find('NS') == -1)):
            fields = a_line.split()
            
            # Pull out 'A' records only 
            if ( fields[2] == 'A' ):
                address = ipaddress.ip_address(fields[3])
                addr_list.append(address)

# Lookup portal net for address
addr_to_portal_file = open('address_to_portal_net.txt', 'w') 
for address in sorted(addr_list):
    # Check if address is in 44.0.0.0/8
    if (address in AMPR_NET):
        for subnet in sorted(subnets):
            if ( address in subnet ):
                addr_to_portal_file.write('\"{0}\",\"{1}\"\n'.format(str(address), str(subnet)))
                break
        else:
            addr_to_portal_file.write('\"{0}\",\"{1}\"\n'.format(str(address), 'PORTAL_NET_NOT_FOUND'))

addr_to_portal_file.close()

# Lookup gateway address for address
addr_to_gw_file = open('address_to_gw.txt', 'w') 
for address in sorted(addr_list):
    # Check if address is in 44.0.0.0/8
    if (address in AMPR_NET):
        for gw_net in sorted(gw_nets):
            if ( address in gw_net ):
                addr_to_gw_file.write('\"{0}\",\"{1}\"\n'.format(str(address), str(gw_nets[gw_net])))
                break
        else:
            addr_to_gw_file.write('\"{0}\",\"{1}\"\n'.format(str(address), 'GATEWAY_NOT_FOUND'))

addr_to_gw_file.close()

