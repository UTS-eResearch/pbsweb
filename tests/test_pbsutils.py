#!/usr/bin/env python3
# -*- coding: utf-8 -*-

'''
Test pbsutils.py
'''

import os, sys, datetime, time
import re

# You need to set the hostname of the PBS Server
pbsserver = 'pbsserver'

try:
    # Running from above the tests directory.
    sys.path.append(os.path.abspath("./"))
    import pbs 
    from pbsutils import get_nodes, get_queues, get_jobs
    from pbsutils import node_attributes_reformat, queue_attributes_reformat, job_attributes_reformat
except:
    # Running from within the tests directory.
    sys.path.append(os.path.abspath("../"))
    import pbs 
    from pbsutils import get_nodes, get_queues, get_jobs
    from pbsutils import node_attributes_reformat, queue_attributes_reformat, job_attributes_reformat

def get_node_totals(nodes):
    '''
    Get totals of some attributes for all the nodes.
    '''
    totals = {}
    totals['jobs_total'] = 0     # Total of all jobs across the cluster.
    totals['cpus_available'] = 0 # Total of all available cpus across the cluster.
    totals['cpus_assigned'] = 0  # Total of all assigned cpus across the cluster.
    totals['mem_available'] = 0  # Total of all available memory across the cluster.
    totals['mem_assigned'] = 0   # Total of all assigned memory across the cluster.

    for n in nodes:
        totals['jobs_total'] = totals['jobs_total'] + len(n['jobs'])
        totals['cpus_available'] = totals['cpus_available'] + int(n['resources_available_ncpus'])
        totals['cpus_assigned'] = totals['cpus_assigned'] + int(n['resources_assigned_ncpus'])
        totals['mem_available'] = totals['mem_available'] + int(n['resources_available_mem'])
        totals['mem_assigned'] = totals['mem_assigned'] + int(n['resources_assigned_mem'])
    
    totals['cpus_ratio'] = int(100 * float(totals['cpus_assigned']) / float(totals['cpus_available']) )
    totals['mem_ratio']  = int(100 * float(totals['mem_assigned'])  / float(totals['mem_available']) )

    return totals

def print_nodes(conn):
    nodes = get_nodes(conn)
    nodes = node_attributes_reformat(nodes)
    for node in nodes:
        print('Node Name:  %s' % node['node_name'])
        print('     Mem:  ', node['resources_assigned_mem'], '/', node['resources_available_mem'], \
            'GB = ', '%3d' % node['mem_ratio'], '% used')
        print('     Cores:', node['resources_assigned_ncpus'],'/', node['resources_available_ncpus'], \
            '=', '%3d' % node['cpu_ratio'], '% used')
        
        # Lots more keys can be shown.
        #for key in node.keys():
        #    print('    ', key, ' = ', node[key])

    print('\nNode Totals: ')
    print(get_node_totals(nodes))

def print_queues(conn):
    queues = get_queues(conn)
    queues = queue_attributes_reformat(queues)
    for queue in queues:
        print('------ Queue Name: %s ------' % queue['queue_name'])
        for key in queue.keys():
            print('  ', key, ' = ', queue[key])

def print_jobs(conn):
    jobs = get_jobs(conn)
    jobs = job_attributes_reformat(jobs)
    for job in jobs:
        print('\n------ Job ID: %s; Job Name: %s ------' % (job['job_id'], job['job_name']))
        for key in job.keys():
            print('  ', key, ' = ', job[key])

def print_jobs_filtered(conn):
    jobs = get_jobs(conn)
    jobs = job_attributes_reformat(jobs)
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
        print('Nodes')
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

