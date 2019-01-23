#!/usr/bin/env python
# -*- coding: utf-8 -*-

'''
Show information on the nodes.
'''

import os, sys
sys.path.append(os.path.abspath("../"))
import pbs 

# You need to set the hostname of the PBS Server.
pbsserver = 'hpcnode0'

conn = pbs.pbs_connect(pbsserver) 
if conn < 0:
    print 'Error connecting to server.' 
    sys.exit(1)

# Returns a batch_status structure.
b = pbs.pbs_statvnode(conn, '', None, None)

while b != None:
    print "\n------ Node: %s ------" % b.name
    attribs = b.attribs 
    while attribs != None: 
        if attribs.resource != None: 
            print "    %s.%s = %s" % (attribs.name, attribs.resource, attribs.value)
        else:
            print "    %s = %s" % (attribs.name, attribs.value)
    
        attribs = attribs.next

    b = b.next

