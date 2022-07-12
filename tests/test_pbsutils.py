#!/usr/bin/env python3
# -*- coding: utf-8 -*-

'''
Test pbsutils.py
    
See the end of this script for how to show filtered jobs
based on any string in the job attributes.
'''

import os, sys, datetime, time
import re

# You need to set the hostname of the PBS Server
pbsserver = 'pbsserver'

try:
    # Running from above the tests directory.
    sys.path.append(os.path.abspath("./"))
    import pbs 
    from pbsutils import get_nodes, get_queues, get_jobs, get_node_totals
    from pbsutils import node_attributes_reformat, queue_attributes_reformat, job_attributes_reformat
except:
    # Running from within the tests directory.
    sys.path.append(os.path.abspath("../"))
    import pbs 
    from pbsutils import get_nodes, get_queues, get_jobs, get_node_totals
    from pbsutils import node_attributes_reformat, queue_attributes_reformat, job_attributes_reformat

def print_nodes(conn):
    nodes = get_nodes(conn)
    nodes = node_attributes_reformat(nodes)
    print('=== Showing Attributes of all Nodes ===')
    for node in nodes:
        print('Node Name:  %s' % node['node_name'])
        for key in node.keys():
            print('    ', key, ' = ', node[key])

    print('\nNode Totals: ')
    print(get_node_totals(nodes))

def print_queues(conn):
    queues = get_queues(conn)
    queues = queue_attributes_reformat(queues)
    print('=== Showing Attributes of all Queues ===')
    for queue in queues:
        print('------ Queue Name: %s ------' % queue['queue_name'])
        for key in queue.keys():
            print('  ', key, ' = ', queue[key])

def print_jobs(conn):
    jobs = get_jobs(conn)
    jobs = job_attributes_reformat(jobs)
    print('=== Showing Attributes of all Jobs ===')
    for job in jobs:
        print('\n------ Job ID: %s; Job Name: %s ------' % (job['job_id'], job['job_name']))
        for key in job.keys():
            print('  ', key, ' = ', job[key])

def print_jobs_filtered(conn):
    jobs = get_jobs(conn)
    jobs = job_attributes_reformat(jobs)
    print('=== Showing Attributes of Filtered Jobs ===')
    for job in jobs:
        print('\n------ Job ID: %s; Job Name: %s ------' % (job['job_id'], job['job_name']))
        for key in job.keys():
            if 'time' in key: 
                print('  ', key, ' = ', job[key])

if __name__ == '__main__':

    conn = pbs.pbs_connect(pbsserver) 
    if conn < 0:
        print('Error connecting to PBS server.')
        sys.exit(1)

    # Check user must have supplied one arg, else exit.
    if len(sys.argv) != 2:
        print('Usage: %s nodes|queues|jobs' % sys.argv[0])
        sys.exit()

    if sys.argv[1] == 'nodes':
        print_nodes(conn)
    elif sys.argv[1] == 'queues':
        print_queues(conn)
    elif sys.argv[1] == 'jobs':
        print_jobs(conn)
    else:
        print('Usage: %s nodes|queues|jobs' % sys.argv[0])
        print('You need to enter one of the options above.')

    # Uncomment this and edit the function to filter jobs based on 
    # any string in the job attributes.
    #print_jobs_filtered(conn)

