'''
Module that contains utility functions for the pbsweb application.

This code was developed by Mike Lake <Mike.Lake@uts.edu.au>.

License:

  Copyright 2019 University of Technology Sydney

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

'''

# List of public objects that are imported by import *.
__all__ = ['get_nodes', 'get_queues', 'get_jobs', 'get_node_totals', \
           'node_attributes_reformat', 'queue_attributes_reformat', 'job_attributes_reformat']

import pbs
import os, datetime, time
import re

def _epoch_to_localtime(epoch_time, format_str):
    '''
    Converts an epoch time like 1426133709 into '2015-03-12 at 03:15 PM'.
    '''
    temp = time.localtime(int(epoch_time))
    return time.strftime(format_str, temp)

def _show_attr_name_remapping(conn):
    '''
    This is a debugging function. It displays all the resources_available, 
    resources_assigned and their attributes and values.
    '''
    b = pbs.pbs_statvnode(conn, '', None, None)
    while b != None:
        attributes = {} # Init the dictionary to empty.

        attribs = b.attribs # The parameter attrib is a pointer to an attrl structure.
        attributes['node_name'] = b.name
        while attribs != None:
            if attribs.resource != None:
                print '    ', attribs.name, ':', attribs.resource, '=', attribs.value
                keyname = '%s_%s' % (attribs.name, attribs.resource)
                attributes[keyname] = attribs.value
            else:
                attributes[attribs.name] = attribs.value

            attribs = attribs.next

        b = b.next

def get_nodes (conn):
    '''
    Get information on the PBS nodes. It is the equivalent of "pbsnodes -a".
    This function returns a list of nodes, where each node is a dictionary.

    Uncommenting the print statements in this function will show information like this:

      ------------ hpcnode20 ------------------
      Mom : hpcnode20
      Port : 15002
      pbs_version : 14.2.2.20170505010934
      ntype : PBS
      state : free
      pcpus : 28
      jobs : 100932.hpcnode0/0, 100932.hpcnode0/1, 100932.hpcnode0/2, 100932.hpcnode0/3,
             100967.hpcnode0/1, 100967.hpcnode0/2, 100967.hpcnode0/3
        resources_available : arch = linux
        resources_available : host = hpcnode20
        resources_available : mem = 529331720kb
        resources_available : ncpus = 28
        resources_available : vnode = hpcnode20
        resources_assigned : accelerator_memory = 0kb
        resources_assigned : icpus = 0
        resources_assigned : mem = 524288000kb
        resources_assigned : naccelerators = 0
        resources_assigned : ncpus = 7
        resources_assigned : ngpus = 0
        resources_assigned : vmem = 0kb
      resv_enable : True
      sharing : default_shared

    To make the returned dictionary simpler we rename all the resources_available and
    resources_assigned above to be a key like this:
        ...
        resources_available : mem  => resources_available_mem
        resources_assigned : ncpus => resources_assigned_ncpus
        resources_assigned : ngpus => resources_assigned_ngpus
        ... etc
    This is done in the line below:
        keyname = '%s_%s' % (attribs.name, attribs.resource)

    We then append this dictionary to the list of nodes.

    '''
    nodes = [] # This will contain a list of dictionaries.

    # The function pbs_statvnode (and likewise pbs_statque & pbs_statjob)
    # returns a batch_status structure.
    b = pbs.pbs_statvnode(conn, '', None, None)
    while b != None:
        attributes = {} # Init the dictionary to empty.

        attribs = b.attribs # The parameter attrib is a pointer to an attrl structure.
        #print '------------', b.name, '------------------'
        attributes['node_name'] = b.name
        while attribs != None:
            if attribs.resource != None:
                # The debugging print below here is indented a bit more to distinguish
                # resource attributes from non-resource attributes.
                #print '    ', attribs.name, ':', attribs.resource, '=', attribs.value
                keyname = '%s_%s' % (attribs.name, attribs.resource)
                attributes[keyname] = attribs.value
            else:
                #print '  ', attribs.name, ':', attribs.value
                # e.g. acl_user_enable : True
                attributes[attribs.name] = attribs.value

            # This line must be present or you will loop forever!
            attribs = attribs.next

        nodes.append(attributes)
        b = b.next

    # Sort the nodes by the node's name.
    nodes = sorted(nodes, key=lambda k: k['node_name'])

    return nodes

def get_queues(conn):
    '''
    Get information on the PBS queues.
    This function returns a list of queues, where each queue is a dictionary.

    Example: Queue Name = smallq

    if attribs.resource == None    <== we get the attribs:
       name       : value
       ----         -----
       queue_type : Execution
       total_jobs : 49
       state_count : Transit:0 Queued:18 Held:0 Waiting:0 Running:30 Exiting:0 Begun:1
       max_run : [u:PBS_GENERIC=12]
       enabled : True
       started : True

    if attribs.resource != None    <== we get the attribs:
       name          :      resource = value
       ----                 --------   -----
       resources_max :      mem      = 32gb
       resources_max :      ncpus    = 2
       resources_max :      walltime = 200:00:00
       resources_default :  walltime = 24:00:00
       resources_assigned : mem      = 598gb
       resources_assigned : ncpus    = 57
       resources_assigned : nodect   = 29

    To make the returned dictionary simpler we rename the name:resource above
    to be a key like this:

    resources_max : mem          =>  resources_max_mem
    resources_max : ncpus        =>  resources_max_ncpus
    resources_max : walltime     =>  resources_max_walltime
    resources_default : walltime =>  resources_default_walltime
    resources_assigned : mem     =>  resources_assigned_mem
    resources_assigned : ncpus   =>  resources_assigned_ncpus
    resources_assigned : nodect  =>  resources_assigned_nodect
    '''

    queues = [] # This will contain a list of dictionaries.

    # Some of the attributes are not present for all queues so we list them all
    # here and in the loop below set them to None. For instance, a routing queue
    # does not have some of these attributes.
    attribute_names = ['resources_max_mem','resources_max_ncpus','resources_max_walltime', \
            'resources_assigned_mem','resources_assigned_ncpus', \
            'resources_default_walltime', 'max_run', 'state_count', 'acl_user_enable']

    b = pbs.pbs_statque(conn, '', None, None)
    while b != None:
        attributes = {} # Init the dictionary to empty.
        for name in attribute_names:
            attributes[name] = None

        attribs = b.attribs
        #print 'METHODS: ', dir(attribs)  # Uncomment to see what methods are available.
        #print '------------ Queue %s ------------' % b.name
        attributes['queue_name'] = b.name
        while attribs != None:
            if attribs.resource != None:
                # The print below here is indented a bit more to distinguish
                # resource attributes from non-resource attributes.
                #print '    ', attribs.name, ':', attribs.resource, '=', attribs.value
                keyname = '%s_%s' % (attribs.name, attribs.resource)
                attributes[keyname] = attribs.value
            else:
                #print '  ', attribs.name, ':', attribs.value
                # e.g. acl_user_enable : True
                attributes[attribs.name] = attribs.value

            attribs = attribs.next

        # Don't save the defaultq as this is a routing queue.
        # TODO move this to reformat?
        if attributes['queue_name'] != 'defaultq':
            queues.append(attributes)

        b = b.next

    return queues

def get_jobs(conn):
    '''
    Get information on the PBS jobs.
    This function returns a list of jobs, where each job is a dictionary.

    This is the list of resources requested by the job, e.g.:

      Resource_List : mem = 120gb
      Resource_List : ncpus = 24
      Resource_List : nodect = 1
      Resource_List : place = free
      Resource_List : select = 1:ncpus=24:mem=120GB
      Resource_List : walltime = 200:00:00

      This is a non-resource attribute, e.g.
        Job_Name : AuCuZn
        Job_Owner : 999777@hpcnode0
        job_state : Q
        queue : workq
        server : hpcnode0
      etc ....

    '''

    jobs = [] # This will contain a list of dictionaries.

    # Some jobs don't yet have a particular attribute as the jobs hasn't started yet.
    # We have to create that key and set it to something, otherwise we get errors like:
    #   NameError("name 'resources_used_ncpus' is not defined",)
    attribute_names = ['resources_used_ncpus', 'resources_used_mem', 'resources_used_vmem', \
        'resources_used_walltime', 'exec_vnode', 'stime', 'resources_time_left']

    b = pbs.pbs_statjob(conn, '', None, None)
    while b != None:
        attributes = {} # Init the dictionary to empty.
        for name in attribute_names:
            attributes[name] = ''

        attribs = b.attribs
        #print '----------- %s -------------------' % b.name
        attributes['job_id'] = b.name.split('.')[0] # b.name is a string like '137550.hpcnode0'
        while attribs != None:
            if attribs.resource != None:
                #print '    ', attribs.name, ':', attribs.resource, '=', attribs.value
                keyname = '%s_%s' % (attribs.name, attribs.resource)
                keyname = keyname.lower()
                attributes[keyname] = attribs.value
            else:
                #print '  ', attribs.name, ':', attribs.value
                keyname = attribs.name.lower()
                attributes[keyname] = attribs.value

            attribs = attribs.next

        jobs.append(attributes)
        b = b.next

    return jobs

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

def node_attributes_reformat(nodes):

    for node in nodes:
        #print '---------'
        #for attribute in node.keys():
        #    print '    ', attribute, node[attribute]

        # There are certain keys that we always want to be present.
        # If they are not present create them with zero value.
        for attribute in \
            ['resources_available_mem', 'resources_available_ncpus', 'resources_available_ngpus', \
             'resources_assigned_mem', 'resources_assigned_ncpus', 'resources_assigned_ngpus']:
            if attribute not in node.keys():
                node[attribute] = 0

        if 'comment' not in node.keys():
            node['comment'] = ''
        if 'jobs' not in node.keys():
            node['jobs'] = ''

        # Change jobs from string to a list.
        # jobs is a string like this:
        #   105059.hpcnode0/0, 105059.hpcnode0/1, 105059.hpcnode0/2, 105059.hpcnode0/3,     \ Job 105059
        #   105059.hpcnode0/4, 105059.hpcnode0/5, 105059.hpcnode0/6, 105059.hpcnode0/7,     /
        #   105067.hpcnode0/8, 105067.hpcnode0/9, 105067.hpcnode0/10, 105067.hpcnode0/11,   \ Job 105067
        #   105067.hpcnode0/12, 105067.hpcnode0/13, 105067.hpcnode0/14, 105067.hpcnode0/15, /
        #   105068.hpcnode0/16, 105068.hpcnode0/17, 105068.hpcnode0/18, 105068.hpcnode0/19, \ Job 105068
        #   105068.hpcnode0/20, 105068.hpcnode0/21, 105068.hpcnode0/22, 105068.hpcnode0/23  /
        if node['jobs']:
            # remove whitespace from string
            jobs_string = node['jobs'].replace(' ', '')
            # split on comma, then take first part of split on '.' & turn it into a set.
            jobs_unique = set([j.split('.')[0] for j in jobs_string.split(',')])
            # Turn it back into a list which will now be the unique jobs
            node['jobs'] = list(jobs_unique)
        else:
            node['jobs'] = []

        # Change memory from string with kb (eg '264501336kb') to integer in Gb (eg 264).
        if node['resources_available_mem']:
            m = re.match('^([0-9]+)kb$', node['resources_available_mem'])
            node['resources_available_mem'] = '%d' % (int(m.group(1))/1024/1024)
        if node['resources_assigned_mem']:
            m = re.match('^([0-9]+)kb$', node['resources_assigned_mem'])
            node['resources_assigned_mem'] = '%d' % (int(m.group(1))/1024/1024)

        # Create a new attribute 'state_up' to indicate if the node is up or not as
        # 'state' can be one of busy, free, job-busy, job-exclusive, down, or offline.
        # If busy, free, job-busy, job-exclusive <-- OK node is up.
        # If down, offline                       <-- Problem, node is down.
        node['state_up'] = True
        if 'down' in node['state'] or 'offline' in node['state']:
            node['state_up'] = False

        # Create a new attribute 'cpu_ratio' to use in the web display.
        if node['resources_available_ncpus'] != 0:
            node['cpu_ratio'] = 100 * int(node['resources_assigned_ncpus']) \
                / int(node['resources_available_ncpus'])
        else:
            node['cpu_ratio'] = 0

        # Create a new attribute 'mem_ratio' to use in the web display.
        node['mem_ratio'] = 100 * int(node['resources_assigned_mem']) \
            / int(node['resources_available_mem'])

    return nodes

def queue_attributes_reformat(queues):

    # Here we cover the special case of formatting the state count.
    # It is an attribute like this:
    #   state_count : Transit:0 Queued:11 Held:0 Waiting:0 Running:20 Exiting:0 Begun:0
    # and we want it as a dictionary like this:
    #   state_count { 'Transit':0 'Queued':11 'Held':0 'Waiting':0 'Running':20 'Exiting':0 'Begun':0
    for queue in queues:
        this_state = {}
        for key in queue.keys():
            if key == 'state_count':
                state_count_list = queue['state_count'].split()
                for item in state_count_list:
                    (name,value) = item.split(':')
                    this_state[name] = int(value)
            if key == 'max_run':
                max_run = int(queue['max_run'].split('=')[1].replace(']',''))
        queue['max_run'] = max_run
        queue['state_count'] = this_state

        # Get the jobs queued and running from the state_count and not total_jobs.
        queue['jobs_running'] = queue['state_count']['Running']
        queue['jobs_queued']  = queue['state_count']['Queued']

    return queues

def job_attributes_reformat(jobs):
    '''
    Reformat job attributes like changing epoch time to local time,
    queue codes to more understandable words, memory from bytes to MB or GB.
    '''

    for attributes in jobs:
        # There are some keys that we will never use, remove them.
        attributes.pop('variable_list', None)
        attributes.pop('submit_arguments', None)
        attributes.pop('error_path', None)
        attributes.pop('output_path', None)

        # exec_host = (hpcnode20:mem=8388608kb:ncpus=2)
        # TODO exec_vnode might be split across chunks in which case it will look like this:
        #   exec_vnode is: (vnodeA:ncp us=N:mem=X) + (nodeB:ncpu s=P:mem=Y+ nodeC:mem=Z)
        if attributes['exec_vnode']:
            attributes['exec_vnode'] = attributes['exec_vnode'].split(':')[0]
            attributes['exec_vnode'] = attributes['exec_vnode'][1:]
        if attributes['exec_host']:
            attributes['exec_vnode'] = attributes['exec_host'].split('+')
            attributes['exec_vnode'] = [s.split('/')[0] for s in attributes['exec_vnode']]
            attributes['exec_vnode'] = list(OrderedDict.fromkeys(attributes['exec_vnode']))

        # This splits user_name@hostname to get just the user_name.
        attributes['job_owner'] = attributes['job_owner'].split('@')[0]

        # All times are in seconds since the epoch
        # ctime = time job was created             e.g. ctime = Fri Mar  6 14:36:07 2015
        # qtime = time job entered the queue       e.g. qtime = Fri Mar  6 14:36:07 2015
        # etime = time job became eligible to run  e.g. etime = Fri Mar  6 14:36:07 2015
        # stime = time job started execution       e.g. stime = Fri Mar  6 14:36:07 2015
        # mtime = time job was last modified       e.g. mtime = Tue Mar 17 13:09:19 2015

        # Calculate a wait time = time started - time entered queue. This will be in seconds.
        if attributes['qtime'] and attributes['stime']:
            attributes['wtime'] = int(attributes['stime']) - int(attributes['qtime'])
            attributes['wtime'] = '%.0f' % (attributes['wtime'] / 3600.0) # convert to hours
        else:
            attributes['wtime'] = ''

        # Change time since epoch to localtime.
        # If the job has not yet queued or started then that time will be ''.
        if attributes['qtime']:
            attributes['qtime'] = _epoch_to_localtime(attributes['qtime'], "%Y-%m-%d at %I:%M %p")
        if attributes['stime']:
            attributes['stime'] = _epoch_to_localtime(attributes['stime'], "%Y-%m-%d at %I:%M %p")

        # If the job was queued or started today remove the leading date.
        today = datetime.datetime.now().strftime('%Y-%m-%d')
        if today == attributes['qtime'].split()[0]:
            attributes['qtime'] = attributes['qtime'].replace('%s at' % today, '')
            attributes['stime'] = attributes['stime'].replace('%s at' % today, '')

        # Change queue code to a word. For queue states see man qstat.
        states = {'B':'Array job', 'E':'Exiting','F':'Finished','H':'Held','M':'Moved',\
                  'Q':'Queued','R':'Running','S':'Suspend','T':'Transiting','U':'User,suspend',\
                  'W':'Waiting', 'X':'Finished'}
        attributes['job_state'] = states[attributes['job_state']]

        # Change walltimes from H:M:S to H:M
        if attributes['resource_list_walltime']:
            (H,M,S) = attributes['resource_list_walltime'].split(':')
            attributes['resource_list_walltime'] = '%s:%s' % (H,M)

        if attributes['resources_used_walltime']:
            (H,M,S) = attributes['resources_used_walltime'].split(':')
            attributes['resources_used_walltime'] = '%s:%s' % (H,M)
            hours_used     = attributes['resources_used_walltime'].split(':')[0]
            hours_walltime = attributes['resource_list_walltime'].split(':')[0]
            attributes['resources_time_left'] = int(hours_walltime) - int(hours_used)

        # Change memory from string in kb (eg '264501336kb') to integer Gb (eg 264).
        if 'resource_list_mem' in attributes:
            attributes['resource_list_mem'] = attributes['resource_list_mem'].replace('gb', '')
        if attributes['resources_used_mem']:
            m = re.match('^([0-9]+)kb$', attributes['resources_used_mem'])
            attributes['resources_used_mem'] = '%d' % (int(m.group(1))/1024/1024)
        if attributes['resources_used_vmem']:
            m = re.match('^([0-9]+)kb$', attributes['resources_used_vmem'])
            attributes['resources_used_vmem'] = '%d' % (int(m.group(1))/1024/1024)

    return jobs

