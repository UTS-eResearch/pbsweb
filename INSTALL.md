# Installation 

SEARCH FOR UPTO   Back to [Mikes Notes](/pbsweb_mikes_notes/)

## Software Required

* A Linux distrubution, either Centos 8, Rocky Linux 8 or recent Fedora.
* Apache or Nginx webserver
* This software "pbsweb" downloaded from <https://github.com/UTS-eResearch/pbsweb>  {{ todo }} 
* PBS Professional from <https://www.pbsworks.com> or OpenPBS from <https://www.pbspro.org>.     
  We are using PBS Pro version 2021.1.0.
* GCC
* Openssl-devel
* SWIG - Software Wrapper and Interface Generator
* Python development packages (python38-devel)
* Python 3.8 virtual environment with:
    - Bottle micro web framework
    - Jinja2 templating engine
    - UWSGI server to run the web app

There are two install scripts which aid the installation
(`install_dependencies.sh` & `install_pbsweb.sh`) but there are still quite a
few procedures to do manually. They are not difficult, but they are not included in 
the install script because some of those steps are risky to automate in a script.

Follow the procedure below to perform the installation. 

## Note on Linux Distribution and Webserver

The install documentation and the install scripts are based on a Red Hat like distribution. 
The application will work on Debian based distributions but you will need to work out 
the slightly different names for some packages. 

Likewise you can also use Apache instead of ngix but you will need to change some commands.
 
## 1. Checkout the pbsweb Repo

    $ cd
    $ mkdir git
    $ cd git
    $ git clone https://github.com/speleolinux/pbsweb.git    

This will have downloaded the code into the directory `~/git/pbsweb/`.

## 2. Ensure Host "pbsserver" can be Found

The pbsweb application expects to communicate with the PBS server via the 
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
 
## 3. Install the PBS `pbs_ifl.h` File

You will need the file `pbs_ifl.h` from your PBS installation. 

Where do I find pbs_ifl.h? For PBS Professional its in the development package.
It's not in the client, execution or server packages.

    $ rpmquery -ql pbspro-devel | grep pbs_ifl
    /opt/pbs/include/pbs_ifl.h

For OpenPBS it's to be found on Github here: 
<https://github.com/PBSPro/pbspro/tree/master/src/include>  

The `pbs_ifl.h` is not included in this code as you should use the version that
came with your PBS installation. 
Once you have found this file copy it to the location on the login
node where you will later run `swig_compile_pbs.sh` from.

    $ cd ~/git/pbsweb/
    $ cp /opt/pbs/include/pbs_ifl.h .

## 4. Configure PBS

Now we need to add or nginx to the list of PBS server operators.

The app runs as `nginx` so this needs permission to query qstat. Otherwise 
`pbs.pbs_statjob()` will return an empty list.
You will find that it works OK when you run `pbsweb.py` from the command line, as
your probably in the PBS server operators list. 

Check the list of current operators:

    $ qmgr -c 'print server' | grep operators

Add nginx to the list of operators. Note the use of `+=` and the `@*` at the end!

    $ qmgr
    Qmgr: set server operators += nginx@*

Check the list of current operators again:
    
    $ qmgr -c 'print server' | grep operators

## 5. Configure Nginx 

There is an example Nginx configuration file in the directory `confs/`. 
Note that this configuration example is for a non-TLS site. 
It's up to you to configure this for a TLS site with a valid certificate.

Edit `conf/nginx_default.conf` to suit and copy it to `conf/default.conf`.

Nginx expects this to be named `default.conf` and also by doing this any upgrades 
to pbsweb will not overwrite your custom `default.conf`. Then copy it to your nginx 
web server.

    $ sudo cp confs/default.conf /etc/nginx/conf.d/default.conf

Restart nginx and check its status to make sure its running OK:

    $ sudo systemctl restart nginx.service
    $ sudo systemctl status  nginx.service

## 6. Run the Dependencies Install Script

This script will some system packages, system file and two python virtual environments.

This script will not run if you try to run it as root. Run it as a user that has sudo privileges.
It will ask for your password for sudo.

    $ ./install_dependencies.sh

You can run this script again at any time. It will not overwrite existing files or directories.

## 7. Run the SWIG Script

The SWIG package (swig) will have been installed by the `install_dependencies.sh` 
script above.

SWIG stands for Software Wrapper and Interface Generator and allows us to 
create a python module that allows python scripts to run PBS commands.
You will also need the PBS `pbs_ifl.h` file that comes with your PBS. 

Edit the shell script `swig_compile.sh` and ensure that the variables at the
top (especially `PYTHON_INCL`) are appropriate for your installation, then run the script. 

    $ ./swig_compile_pbs.sh

There will be no output if all goes well.

The above script runs `swig` which uses the SWIG interface file `pbs.i` to
create `pbs.py` and `pbs_wrap.c`. Then it uses `gcc` to compile `pbs_wrap.c` 
to create `_pbs.so`. The swig generated `pbs.py` imports `_pbs.so` at run time.

## 8. Run the PBSWeb Install Script

Like the script to install the dependencies, this script
will not run if you try to run it as root. 
The `install_dependencies.sh` script will have setup the permissions so that
you can run this script without sudo.

    $ ./install_pbsweb.sh

Your nearly finished :-) 

This install script has now setup the uWSGI applications so we can now start the 

## 9. Start the Emperor

Now we can start the uWSGI emperor service. This will start its "vassals" i.e. 
the pbsweb application.
    
    # systemctl start emperor.uwsgi.service

Checks its status with:

    # systemctl status emperor.uwsgi.service

If there are no errors you can now "enable" it so that it will load
automatically at system startup time.

    # systemctl enable emperor.uwsgi.service

Note: Emperor will restart any application that stops if the application has an INI file
under the `confs` directory. If you don't want an application to start rename its 
INI file to, for instance, `other.ini_STOPPED`.

## 10. Check pbsweb is Working !

At this stage you can test the web application by going to `http://your-server/statuspbs/`

Click the links for the Nodes, Queues and Jobs. All should work mOK.

## Removing pbsweb

{{ todo }}

## Tests

### Command Line Tests 

These are a few tests to check `pbs.py` works OK and to demonstrate how to
query PBS data structures.

    $ source ~/virtualenvs/pbsweb/bin/activate
    (pbsweb)$ 

    $ cd tests

Prints the nodes available and their attributes:

    $ ./test_pbs_nodes.py 

Prints the queues available and their attributes:

    $ ./test_pbs_queues.py       

Prints the list of jobs and their attributes:

    $ ./test_pbs_jobs.py         

### Web Application Test with Bottle’s in-built Server

If the production site does not work test the web application using bottle's in-built local server. 

In the git directory, edit `pbsweb.py` and ensure `bottle.run` is uncommented:

    if __name__ == '__main__':
        bottle.debug(True)
        bottle.run(host='localhost', port=8080, reloader=True)
    else:
        app = application = bottle.default_app()

Run `pbsweb.py` in the foreground in one terminal i.e. 

    $ source ~/virtualenvs/pbsweb/bin/activate
    (pbsweb)$

    (pbsweb)$ ./pbsweb.py
    Bottle v0.12.19 server starting up (using WSGIRefServer())...
    Listening on http://localhost:8080/
    Hit Ctrl-C to quit.
    
Go to <http://localhost:8080> in a web browser. You should see a table of your clusters
nodes, queues and jobs. The nodes table should show CPU usage and memory usage 
as in the screenshot in the Introduction. 

Any errors will be visible in the terminal.

## Notes

### The Two Python 3.8 Virtual Environments

There are two Python virtual environments; one for a uWSGI "Emperor"
and the other for the PBS web application. The Emperor master process watches
over the apps (called vassals) to make sure they are running.
If an app/vassal stops, then the Emperor will reload it. 
Even if you’re only running a single app using "Emperor" mode is still worth it. 

They are setup using the following directory structure. 
Where pbsweb is this application and "other" is some other WSGI application. 
Note you can also have a test pbsweb app for testing purposes.

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

