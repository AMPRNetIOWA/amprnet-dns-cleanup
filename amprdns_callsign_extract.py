#!/usr/bin/python3

import re
import json

# Regular Expression for ITU format call signs
p = re.compile(r'\d?[a-zA-Z]{1,2}\d{1,4}[a-zA-Z]{1,3}')

records = {}

lines_read = 0
no_callsign = 0

# Loop through dns file
with open('ampr.org', encoding='utf-8') as a_file:
    for a_line in a_file:
        a_line = a_line.rstrip()

	# pull out all lines that are IN records (but not NS records)
        if ((a_line.find('IN') != -1) and (a_line.find('NS') == -1)):
            fields = a_line.split()

            # find first call sign in record
            call_signs = re.search(p, fields[0])

            # If a call sign is found update dictionary with DNS entry
            if ( call_signs != None ):
                if (records.get(call_signs.group().upper()) == None):
                    records[call_signs.group().upper()] = [ a_line ]
                else:
                    records[call_signs.group().upper()].append(a_line)
            else:
                no_callsign += 1
        lines_read += 1

calls = 0
for entry in sorted(records.keys()):
    print('CALL: ', entry) 
    
    line_count = 0
    for line in records.get(entry):
        print("\t", line)
        line_count += 1

    print('Line count= ', line_count)
    calls += 1

# print out dictionary in JSON format
#print(json.dumps(records, indent = 4))

print('Call count= ', calls)         	            
print('No call sign entries: ', no_callsign)
print('Lines processed: ', lines_read)


