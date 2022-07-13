#!/usr/bin/env python
# -*- coding: utf-8 -*-

'''
This small web application provides a nice web interface for the nodes and queues on a 
High Performance Computer Cluster (HPCC) running the PBS batch scheduling system.

This code was developed by Mike Lake <Mike.Lake@uts.edu.au>.

License:

  Copyright 2019 Mike Lake & University of Technology Sydney 

  This program is free software: you can redistribute it and/or modify
  it under the terms of the GNU General Public License as published by
  the Free Software Foundation, either version 3 of the License, or
  (at your option) any later version.
  
  This program is distributed in the hope that it will be useful,
  but WITHOUT ANY WARRANTY; without even the implied warranty of
  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
  GNU General Public License for more details.
  
  You should have received a copy of the GNU General Public License
  along with this program. If not, see <http://www.gnu.org/licenses/>.

Versions: 

2014.12.10: First version.
2014.12.12: Added queues.
2017.10.09: Removed login and auth stuff.
2018.10.24: Changed to work with new PBS queue format.
2018.11.28: Changed to use jinja2 templates.
2018.12.19: Release.
2019.01.21: Release.
! The version data above needs to be manually inserted into template "views/tail.j2".
'''

import pbs 
import os, sys, datetime, time
import re
from pbsutils import get_nodes, get_queues, get_jobs
from pbsutils import node_attributes_reformat, queue_attributes_reformat, job_attributes_reformat

import bottle 
from bottle import route, static_file
from bottle import jinja2_view as view

# This hostname should be set in your /etc/hosts file as an alias to your head node.
pbsserver = 'pbsserver'

# This will be automatically updated by the install script.
version = "VERSION_STRING"

########################
# Functions defined here
########################

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

def shell_test():
    '''
    Function to do some tests/debugging when running in the shell.
    This is only used for debugging.
    '''

    print('Running in the shell only.')
    conn = pbs.pbs_connect(pbsserver) 
    if conn < 0:
        print('Error connecting to PBS server.')
        print('Have you set the PBS server hostname in this code?')
        sys.exit(1)

    # Uncomment one or more of the sections below to print info on the nodes,
    # queues and jobs.

    # Print nodes information
    nodes = get_nodes(conn)
    nodes = node_attributes_reformat(nodes)
    for node in sorted(nodes):
        print('Node Name: %s' % node['node_name'])
        print('  Mem:  ', node['resources_assigned_mem'], '/', node['resources_available_mem'], \
            'GB = ', '%3d' % node['mem_ratio'], '% used')
        print('  Cores:', node['resources_assigned_ncpus'],'/', node['resources_available_ncpus'], \
            '=', '%3d' % node['cpu_ratio'], '% used')

        #for key in node.keys():
        #    print('   ', key, ' = ', node[key])

    print('\nNode Totals: ')
    print(get_node_totals(nodes))

    '''
    # Print queues information
    queues = get_queues(conn)
    queues = queue_attributes_reformat(queues)
    for queue in queues:
        print '------ Queue Name: %s ------' % queue['queue_name']
        for key in queue.keys():
            print '  ', key, ' = ', queue[key]
    '''

    '''
    # Print jobs information
    jobs = get_jobs(conn)
    jobs = job_attributes_reformat(jobs)
    for job in jobs:
        print '\n------ Job ID: %s; Job Name: %s ------' % (job['job_id'], job['job_name'])
        for key in job.keys():
            print '  ', key, ' = ', job[key]
    '''

#####################
# Routes defined here
#####################

# All methods are GET

# Serve main entry point page. 
@route('/')
@route('/nodes')
@view('nodes.j2')
def nodes_page():
    conn = pbs.pbs_connect(pbsserver) 
    nodes = get_nodes(conn)
    pbs.pbs_disconnect(conn)
    nodes = node_attributes_reformat(nodes)
    node_totals = get_node_totals(nodes)
    now = datetime.datetime.now().strftime('%Y.%m.%d at %I:%M:%S %P')
    return {'now':now, 'nodes':nodes, 'node_totals':node_totals, 'version':version}

@route('/queues')
@view('queues.j2')
def queues_page():
    conn = pbs.pbs_connect(pbsserver) 
    queues = get_queues(conn)
    pbs.pbs_disconnect(conn)
    queues = queue_attributes_reformat(queues)
    now = datetime.datetime.now().strftime('%Y.%m.%d at %I:%M:%S %P')
    return {'now':now, 'queues':queues, 'version':version}

@route('/jobs')
@view('jobs.j2')
def jobs_page():
    conn = pbs.pbs_connect(pbsserver) 
    jobs = get_jobs(conn)
    pbs.pbs_disconnect(conn)
    jobs = job_attributes_reformat(jobs)
    now = datetime.datetime.now().strftime('%Y.%m.%d at %I:%M:%S %P')
    return {'now':now, 'jobs':jobs, 'version':version}

@route('/test')
@view('test.j2')
def test_page(): 
    now = datetime.datetime.now().strftime('%Y.%m.%d at %I:%M:%S %P')
    ncpus = [24,36,64]
    return {'now':now, 'ncpus':ncpus, 'version':version}

# Serve static files such as CSS, images and javascript. 
# When running using run(host='localhost') this section will be invoked. 
# When running in production we serve static files via nginx or apache so this 
# section will never be reached. Thus we can leave it in here uncommented. 
@route('/static/<filename>')
def static_page(filename):
    return static_file(filename, root='./static/')

#####################
# Run the application
#####################

if __name__ == '__main__':
    # Use this to run using Bottle's inbuilt web server. 
    # If using run() and debug(True) is uncommented then Exception 
    # and Traceback output will go to the web browser screen.
    #bottle.debug(True)
    #bottle.run(host='localhost', port=8080, reloader=True)
    #
    # Use this to run like a command line app i.e. ./pbsweb.py 
    # You must have run() above commented out.
    shell_test()
else:
    app = application = bottle.default_app()

