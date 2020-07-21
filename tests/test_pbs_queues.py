#!/usr/bin/env python
# -*- coding: utf-8 -*-

'''
Show information on the queues.

Queue Name =  smallq

if attribs.resource == None we get the attribs:
   name       : value
   ----         -----
   queue_type : Execution
   total_jobs : 49
   state_count : Transit:0 Queued:18 Held:0 Waiting:0 Running:30 Exiting:0 Begun:1 
   max_run : 12
   enabled : True
   started : True
   
if attribs.resource != None we get the attribs:
   name          :      resource = value
   ----                 --------   -----
   resources_max :      mem      = 32gb
   resources_max :      ncpus    = 2
   resources_max :      walltime = 200:00:00
   resources_default :  walltime = 24:00:00
   resources_assigned : mem      = 598gb
   resources_assigned : ncpus    = 57
   resources_assigned : nodect   = 29

We will have an attributes dictionary that will hold all of the above. 
To do this we will rename the name+resource to be a key like this:

resources_max       =>  res_max_mem       
resources_max       =>  res_max_ncpus 
resources_max       =>  res_max_walltime 
resources_default   =>  res_default_walltime 
resources_assigned  =>  res_assigned_mem 
resources_assigned  =>  res_assigned_ncpus 
resources_assigned  =>  res_assigned_nodect   

'''

import os,sys
try:
    # Running from above the tests directory.
    sys.path.append(os.path.abspath("./"))
    import pbs 
except:
    # Running from within the tests directory.
    sys.path.append(os.path.abspath("../"))
    import pbs 

# You need to set the hostname of the PBS Server.
pbsserver = 'hpccnode0'

conn = pbs.pbs_connect(pbsserver) 
if conn < 0:
    print 'Error connecting to PBS server.' 
    sys.exit(1)

# Returns a batch_status structure.
b = pbs.pbs_statque(conn, '', None, None) 

while b != None:
    print "\n------ Queue: %s ------" % b.name
    attribs = b.attribs 
    # print dir(attribs)  # Uncomment to see what methods are available.
    while attribs != None: 
        if attribs.resource != None: 
            print "    %s.%s = %s" % (attribs.name, attribs.resource, attribs.value)
        else: 
            print "    %s = %s" % (attribs.name, attribs.value)
        attribs = attribs.next

    b = b.next

