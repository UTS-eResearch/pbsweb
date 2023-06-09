# Notes on PBSWeb

* [Obtaining the Version Number](#obtaining-the-version-number)
* [Note on Linux Distribution and Webserver](#note-on-linux-distribution-and-webserver)
* [The Two Python 3.8 Virtual Environments](#the-two-python-38-virtual-environments)
* [List of Main Files and Directories](#list-of-main-files-and-directories)

This contains miscellaneous notes on PBSWeb.

## Obtaining the Version Number

The version number of the PBSWeb that has been installed can be found two ways.

1. It will be listed near the beginning of the installed program `/var/www/wsgi/apps/pbsweb/pbsweb.py`
   as the value of the variable "version".    
2. It will be displayed at the bottom of the PSWeb pages.

There are two possible formats for the version.

A format like this `v2.0.0` will be shown on tagged release versions.

A format like this `v2.0.0-6-g382c9e0` will be shown for versions later than a
tagged release. There are three parts separated by hyphens. The first part is
the version number of the last tagged release, the middle number is the number
of checkins since, and the last part is the short git repo checkin hash.

## Note on Linux Distribution and Webserver

The install documentation and the install scripts are based on a Red Hat like distribution. 
The application will work on Debian based distributions but you will need to work out 
the slightly different names for some packages. 

Likewise you can also use Apache instead of NGINX but you will need to change 
the Nginx configuration files and some commands.

## The Two Python 3.8 Virtual Environments

There are two Python virtual environments; one for a uWSGI "Emperor"
and the other for the PBS web application. The Emperor master process watches
over the apps (called vassals) to make sure they are running.
If an app/vassal stops, then the Emperor will reload it. 
Even if you’re only running a single app using "Emperor" mode is still worth it. 

They are setup using the following directory structure. 
Where PBSWeb is this application and "other" is some other WSGI application. 
Note you can also have a test PBSWeb app for testing purposes.

    /var/www/wsgi/
     ├─ emperor.ini
     ├─ apps/
     │     ├─ pbsweb        <=== Our PBS web app lives in here.
     │     ├─ pbsweb_test   <=== A test PBS web app in here. 
     │     └─ other
     ├─ confs/
     │     ├─ pbsweb.ini
     │     ├─ pbsweb_test.ini
     │     └─ other.ini
     └── virtualenvs/
           ├─ emperor       <=== The Emperor lives in here.
           ├─ pbsweb        <=== Our PBS web app uses this Python.
           └─ other

You can check the version of the emperor uWSGI with:

    $ source /var/www/wsgi/virtualenvs/emperor/bin/activate
    (emperor) $ uwsgi --version
    2.0.20
    (emperor) $ deactivate

Setting your Python to use specific requirements:

    $ source /var/www/wsgi/virtualenvs/pbsweb/bin/activate
    (pbsweb)$ python -m pip install --upgrade pip
    (pbsweb)$ pip install -r requirements_pbsweb.txt

    (pbsweb)$ deactivate
    $

You can do the same with the emperor virtual environment.

You should regularly check your Python virtualenvs for any updates.
Below is an example for the emperor, do the same for the pbsweb environment.

    virtualenvs/$ source /var/www/wsgi/virtualenvs/pbsweb/bin/activate
    (pbsweb) $ pip-review -i
    Everything up-to-date

    (pbsweb) $ deactivate
    $ 

## List of Main Files and Directories

Files:

    install_dependencies.sh     Installs the dependencies of PBSWeb. Run this first.
    swig_compile_pbs.sh         Run this to create _pbs.so and pbs.py
    install_pbsweb.sh           Installs PBSWeb into production or test.
    clean.sh                    Remove files which are not needed at runtime.
    
    conf/                       Contains configuration files.
    
    src/
      pbsweb.py                 The main PBSWeb application.
      pbsutils.py               Module containing utility functions for the PBSWeb application.
      pbs.i                     Used by swig_compile_pbs.sh
      requirements_emperor.txt  Python requirements file, known versions that work.
      requirements_pbsweb.txt   Python requirements file, known versions that work.
      static/                   Contains static resources like stylesheets.
      views/                    Contains templates for the PBSWeb application.

    tests/
      run_all_tests.sh
      testapp.py              A simple WSGI app for testing.
      test_pbs_minimal.py     Just test if the pbs module can be loaded.
      test_pbs_jobs.py        Prints the current jobs and their attributes.
      test_pbs_nodes.py       Prints all nodes and their attributes.
      test_pbs_queues.py      Prints the queues and their attributes.
      test_pbsutils.py        Test pbsutils.py with nodes or queues or jobs

