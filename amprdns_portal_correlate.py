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

addr_to_portal_file = open('dns_entries_to_delete.txt', 'w') 

# Loop through dns zone file
with open(ZONE_FILE, encoding='utf-8') as a_file:
    for a_line in a_file:
        a_line = a_line.rstrip()

        # pull out all lines that are IN records (but not NS records)
        if ((a_line.find('IN') != -1) and (a_line.find('NS') == -1)):
            fields = a_line.split()
            
            # Pull out 'A' records only 
            if ( fields[2] == 'A' ):
                address = ipaddress.ip_address(fields[3])

                # Check if address is in 44.0.0.0/8
                if (address in AMPR_NET):
                    for subnet in sorted(subnets):
                        if ( address in subnet ):
                            break
                    else:
                        addr_to_portal_file.write('{0}\tDEL\tA\t{1}\n'.format(fields[0], str(address) ))

addr_to_portal_file.close()

