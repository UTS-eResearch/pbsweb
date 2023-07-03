# Installing PBSWeb

* [Software Required](#software-required)
* [Installation Procedure](#installation-procedure)
    * [1. Checkout the PBSWeb Repository](#1-checkout-the-pbsweb-repository)
    * [2. Select a Version to Install](#2-select-a-version-to-install)
    * [3. Ensure Host "pbsserver" can be Found](#3-ensure-host-pbsserver-can-be-found)
    * [4. Install the PBS pbs_ifl.h File](#4-install-the-pbs-pbs_iflh-file)
    * [5. Configure PBS](#5-configure-pbs)
    * [6. Run the Dependencies Install Script](#6-run-the-dependencies-install-script)
    * [7. Run the SWIG Script](#7-run-the-swig-script)
    * [8. Run the PBSWeb Install Script](#8-run-the-pbsweb-install-script)
    * [9. Start the Emperor](#9-start-the-emperor)
    * [10. Check PBSWeb is Working](#10-check-pbsweb-is-working)
* [Updating the Python Virtual Environments](#updating-the-python-virtual-environments)
* [Updating PBSWeb](#updating-pbsweb)
* [Removing PBSWeb](#removing-pbsweb)

This covers installing, updating and removing PBSWeb.

## Software Required

* A Linux distrubution, either Centos 8, Rocky Linux 8 or recent Fedora.
  [(See Note)](#note-on-linux-distribution-and-webserver)
* This software "PBSWeb" downloaded from either <https://github.com/UTS-eResearch/pbsweb>  
or <https://github.com/speleolinux/pbsweb>.
* PBS Professional from <https://www.pbsworks.com> or OpenPBS from <https://www.pbspro.org>.     
  We are using PBS Pro version 2021.1.0.
* The file `pbs_ifl.h` from your PBS installation.
* GCC - the GNU Compiler.
* Openssl-devel
* SWIG - Software Wrapper and Interface Generator.
* Python 3.8 development packages.
* Python 3.8 virtual environment with:
    - Bottle micro web framework,
    - Jinja2 templating engine,
    - uWSGI server to run the web app.
* NGINX webserver.
  [(See Note)](#note-on-linux-distribution-and-webserver)

There are two install scripts which aid the installation
(`install_dependencies.sh` & `install_pbsweb.sh`) but there are still quite a
few procedures to do manually. They are not difficult, but they are not included in 
the install script because some of those steps should be done manually by you.

Follow the procedure below to perform the installation. 

## Installation Procedure

On our HPC I have the web server and this software installed on the login node.
You could also install this on a small virtual machine which has the PBSPro
client installed. It should not be installed on the head node as that should 
be dedicated to solely running the cluster.
 
### 1. Checkout the PBSWeb Repository

    $ cd
    $ mkdir git
    $ cd git
    $ git clone https://github.com/speleolinux/pbsweb.git    

This will have downloaded the code into the directory `~/git/pbsweb/`.

### 2. Select a Version to Install

You can install a tagged release or a later version that is still in development.
The development versions may have more functionality, small bug fixes or better 
documentation. They should still work OK as I try to not checkin changes that 
would break things.

To install the latest version skip the rest of this step and proceed to the next step.

To install a tagged release first list the tagged releases available:

List the tagged releases:

    $ cd pbsweb
    $ git tag
    v1.0.0
    v1.1.0
    v2.0.0  <== The last one is the latest tagged release.

    $ git checkout v2.0.0

When this version is checked out there will be a reminder; "You are in 'detached HEAD' state.".
All it means is that the "HEAD" of this repository is now at a previous stage and not 
at the latest version. You can see this by running `git branch`.

    $ git branch
    * (HEAD detached at v2.0.0)
      master

Just remember that after the install you should switch back to the latest
version by checking out the "master" branch with this command:

    $ git checkout master

And you can check your now at the up-to-date master branch:

    $ git branch
    * master

Now proceed to the next step.

### 3. Ensure Host "pbsserver" can be Found

The PBSWeb application expects to communicate with the PBS server via the 
hostname "pbsserver". The PBS server is usuallly the same as the head node.
The easiest way to set this up is to ensure that "pbsserver" is an alias for 
your head node in your `/etc/hosts` file. 

The hosts file to edit needs to be the one that your installing this software onto.

Edit `/etc/hosts` and add pbsserver as an alias for the head node.
It will probably look like this:

    xxx.xx.xx.100  hpcnode0   hpcnode0.your_domain   pbsserver
    xxx.xx.xx.101  hpcnode01  hpcnode01.your_domain
    xxx.xx.xx.102  hpcnode02  hpcnode02.your_domain

The hostname "pbsserver" is set in `pbsweb.py`. Its better to do the above
rather than edit `pbsweb.py`.
 
### 4. Copy your PBS `pbs_ifl.h` File

You will need a copy of the file `pbs_ifl.h` from your PBS installation. 
Where do I find `pbs_ifl.h`? 

For PBS Professional its in the development package.
It's not in the client, execution or server packages. So you will need to install
this package. In my case its named similarly to this `pbspro-devel-2021.1.0.x86_64.rpm`
The `pbs_ifl.h` is not included in this code as you should use the version that
came with your PBS installation. 

    $ rpm -i pbspro-devel-2021.1.0.x86_64.rpm
    $

    $ rpmquery -ql pbspro-devel | grep pbs_ifl
    /opt/pbs/include/pbs_ifl.h

For OpenPBS it's to be found on Github here: 
<https://github.com/PBSPro/pbspro/tree/master/src/include>  

Once you have found this file copy it to the "src" directory.
The  `swig_compile_pbs.sh` script will look for it there.

    $ cd ~/git/pbsweb/
    $ cp /opt/pbs/include/pbs_ifl.h  src/

### 5. Configure PBS

Now we need to add NGINX to the list of PBS server operators.

The app runs as `nginx` so this needs permission to query qstat. Otherwise 
`pbs.pbs_statjob()` will return an empty list.
You will find that it works OK when you run `pbsweb.py` from the command line, as
your probably in the PBS server operators list. 

Check the list of current operators:

    $ qmgr -c 'print server' | grep operators

Add `nginx` to the list of operators. Note the use of `+=` and the `@*` at the end!

    $ qmgr
    Qmgr: set server operators += nginx@*

Check the list of current operators again:
    
    $ qmgr -c 'print server' | grep operators

### 6. Run the Dependencies Install Script

This script will install some system packages, create directories and services for
the UWSGI service, copy PBSWeb configuration files for the Nginx web server,
and create two python virtual environments. When you run this script it will display
details of what will be installed. 

This script will not run if you try to run it as root. Run it as a user that
has sudo privileges. It will ask for your password to use sudo.

    $ ./install_dependencies.sh

*You can run this script again at any time.*

### 7. Run the SWIG Script

The SWIG package (swig) will have been installed by the `install_dependencies.sh` 
script above. SWIG stands for Software Wrapper and Interface Generator and allows 
us to create a python module that allows python scripts to run PBS commands.
You will also need the PBS `pbs_ifl.h` file that comes with your PBS. 

Edit the shell script `swig_compile.sh` and ensure that the variables at the
top (especially `PYTHON_INCL`) are appropriate for your installation, then run the script. 

    $ ./swig_compile_pbs.sh

There will be no output if all goes well.

The above script runs `swig` which uses the SWIG interface file `pbs.i` to
create `pbs.py` and `pbs_wrap.c`. Then it uses `gcc` to compile `pbs_wrap.c` 
to create `_pbs.so`. The swig generated `pbs.py` imports `_pbs.so` at run time.

### 8. Run the PBSWeb Install Script

Like the script to install the dependencies, this script
will not run if you try to run it as root. 
The `install_dependencies.sh` script will have setup the permissions so that
you can run this script without sudo.

    $ ./install_pbsweb.sh test

or 

    $ ./install_pbsweb.sh prod

Your nearly finished :-) 

This install script has now setup the uWSGI applications so we can now start the
uWSGI processes. 

*You can run this script again to install a later PBSWeb version.*

### 9. Start the Emperor

Now we can start the uWSGI emperor service. This will start its "vassals" i.e. 
the PBSWeb application.
    
    $ sudo systemctl start emperor.uwsgi.service

Checks its status with:

    $ sudo systemctl status emperor.uwsgi.service

If there are no errors you can now "enable" it so that it will load
automatically at system startup time.

    $ sudo systemctl enable emperor.uwsgi.service

Note: Emperor will restart any application that stops if the application has an INI file
under the `confs` directory. If you don't want an application to start rename its 
INI file to, for instance, `pbsweb_test.ini_OFF`.

### 10. Check PBSWeb is Working

At this stage you can test the web application by going to `http://your-server/statuspbs/`

Click the links for the Nodes, Queues and Jobs. All should work OK.

## Updating the Python Virtual Environments 

Occasionally you can check if there are updates to the Python packages in the
two virtual environments.

    $ source /var/www/wsgi/virtualenvs/pbsweb/bin/activate
    (pbsweb)$ pip freeze > requirements_pbsweb_before.txt
    (pbsweb)$ pip-review -i

Using `pip-review -i` will do an interactive check for updates.

Similarly check for updates for the emperor environment.

## Updating PBSWeb

Update your repo with the latest PBSWeb code.

    $ git pull

Update your test application.

    $ ./install_pbsweb.sh test

View the app at http://your-server/statuspbs_test/

If this test application still works OK then you can update the production application.

    $ ./install_pbsweb.sh prod

## Removing PBSWeb

Read the `install_dependencies.sh` script to see what it installed and where. 
Remove what you no longer need.

The `install_pbsweb.sh` script only installs files under `/var/www/wsgi/`.
Remove what you no longer need.

