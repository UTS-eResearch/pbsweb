#!/usr/bin/env python3
# -*- coding: utf-8 -*-

'''
Show information on the jobs.
'''

import os,sys
try:
    # Running from above the tests directory.
    sys.path.append(os.path.abspath("./src"))
    import pbs 
except:
    # Running from within the tests directory.
    sys.path.append(os.path.abspath("../src"))
    import pbs 

# You need to set the hostname of the PBS Server.
pbsserver = 'pbsserver'

conn = pbs.pbs_connect(pbsserver) 
if conn < 0:
    print('Error connecting to server.')
    sys.exit(1)

# Returns a batch_status structure.
b = pbs.pbs_statjob(conn, '', None, None) 

while b != None:
    print("\n------ Job: %s ------" % b.name)
    attribs = b.attribs
    while attribs != None:
        if attribs.resource != None:
            print("    %s.%s = %s" % (attribs.name, attribs.resource, attribs.value))
        else:
            print("    %s = %s" % (attribs.name, attribs.value))
        attribs = attribs.next

    b = b.next

