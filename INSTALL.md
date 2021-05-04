# Installation 

## Software Required

* PBS Professional commercial or open source. We are using PBS Pro version 2020.1.2.
  You will need the file `pbs_ifl.h` from your PBS installation.
* gcc + its dependencies 
* openssl-devel + its dependencies
* SWIG - Software Wrapper and Interface Generator
* Python development packages (python2-devel)
* Python 2.7 virtual environment with:
  - bottle==0.12.19         Bottle micro web framework
  - Jinja2==2.11.12         Jinja2 templating engine 
  - MarkupSafe==1.1.1       Dependency of Jinja2
  - uWSGI==2.0.19.1         To run the web app
* apache or nginx

## Configure and Install Dependencies

### PBS Professional

You will already have a PBS installation; either PBS Professional from <https://www.pbsworks.com> 
or PBS Professional open source from <https://www.pbspro.org>. 
You will need the file `pbs_ifl.h` from this PBS installation.
Where do I find pbs_ifl.h? You can find it in the PBS Professional packages for the 
execution or server hosts. It's not in the client host package (pbspro-client).

PBS Professional for a *server* host:
 
    head_node$ rpmquery -ql pbspro-server | grep pbs_ifl
    /opt/pbs/include/pbs_ifl.h

or PBS Professional for *execution* hosts: 
    
    exec_node$ rpmquery -ql pbspro-execution | grep pbs_ifl
    /opt/pbs/include/pbs_ifl.h

It's also to be found on Github here: 
<https://github.com/PBSPro/pbspro/tree/master/src/include>  

The `pbs_ifl.h` is not included in this code as you should use the version that
came with your PBS installation. 
Once you have found this file copy it to the location on the login
node where you will later run `swig_compile_pbs.sh` from.

### Install Python 2.7 Virtual Environments

Here we will setup two Python virtual environments; one for a uWSGI "Emperor"
and the other for the PBS web application. The Emperor master process watches
over the apps (called vassals) to make sure they are running.
If an app/vassal crashes, then the Emperor will reload it. 
Even if you’re only running a single app using "Emperor" mode is still worth it. 

I place the uWSGI apps under `/var/www/wsgi/`. If you have multiple apps under
`/var/www/wsgi/` then the structure could be setup like below, where pbsweb is
this application and "other" is some other application. 

    /var/www/wsgi/
     ├─ emperor.ini
     ├─ apps/
     │     ├─ pbsweb.py
     │     └─ other.py
     ├─ confs/
     │     ├─ pbsweb.ini
     │     └─ other.ini
     └── virtualenvs/
           ├─ emperor       <=== The "Emperor" will live in here.
           ├─ pbsweb        <=== Our PBS web app lives in here.
           └─ other

You need Python 2.7 to run this app so enable a Python 2.7 environment first. 
Note: I use scl (Software Collection Library) to provide the Python 2.7 environment. 
You may not need this.

    $ mkdir -p /var/www/wsgi/virtualenvs
    $ cd /var/www/wsgi/virtualenvs
    $ scl enable python27 bash  <-- See note above.

### Install a virtualenv for the emperor

Install a virtualenv for the emperor to run all the apps.
Only uwsgi needs to be installed in this environment.

    $ virtualenv emperor
    $ source emperor/bin/activate
    (emperor)$ pip install --upgrade pip

    (emperor)$ pip install uwsgi                   

You can check its been installed and its version like this:

    (emperor) $ uwsgi --version
    2.0.19.1

Before we move onto installing a virtualenv for the pbsweb application we need
to deactivate this one.

    (emperor)$ deactivate
    $ 

### Install a virtualenv for the pbsweb application 

This is the web app so we need to install its dependencies, or you can just
`pip install -r requirements.txt` 

    $ virtualenv pbsweb    
    $ source pbsweb/bin/activate
    (pbsweb)$ pip install --upgrade pip

    $ pip install bottle
    $ pip install Jinja2
    $ deactivate
   
To activate the pbsweb virtual environment in future do this:;

    $ source ~/virtualenvs/pbsweb/bin/activate
    (pbsweb)$
 
### Install Openssl Development

The openssl-devel package provides the libs to link with in the swig compile script 
i.e. "`.. -lcrypto -lssl`".

    $ sudo yum install openssl-devel

### Install and Run SWIG 

The SWIG package (swig) needs to be installed. 
SWIG stands for Software Wrapper and Interface Generator and allows us to 
create a python module that allows python scripts to run PBS commands.
You will also need the PBS `pbs_ifl.h` file that comes with your PBS. 

    $ sudo yum install swig

Now make sure that you have activated the Python virtual environment that you
have created above, but be in the directory where the `swig_compile.sh` script is.

    $ source ~/virtualenvs/pbsweb/bin/activate

Edit the shell script `swig_compile.sh` and ensure that the variables at the
top (especially `PYTHON_INCL`) are appropriate for your installation, then run the script. 

    $ ./swig_compile_pbs.sh

There will be no output if all goes well.

The above script runs `swig` which uses the SWIG interface file `pbs.i` to
create `pbs.py` and `pbs_wrap.c`. Then it uses `gcc` to compile `pbs_wrap.c` 
to create `_pbs.so` 
The swig generated `pbs.py` imports `_pbs.so` at run time.

### Configure and Start the Emperor

There are two uWSGI INI files of importance; `emperor.ini` and `pbsweb.ini`.
The `emperor.ini` needs to be manually created and started. The `pbsweb.ini` 
will be installed later by the application install script `install.sh`.

The Emperor's uWSGI file is `/var/www/wsgi/apps/emperor.ini` is:

    [uwsgi]
    master = True
    uid = nginx
    gid = nginx
    vassal-set = chmod-socket=640
    vaccum = true
    virtualenv = /var/www/wsgi/virtualenvs/emperor/
    emperor = /var/www/wsgi/confs
    logto = /var/log/uwsgi.log

Create this `/var/www/wsgi/apps/emperor.ini`. 

After that has been created start the emperor like this:

    $ sudo /var/www/wsgi/virtualenvs/emperor/bin/uwsgi --ini emperor.ini

The last step is to make it load automatically at system startup time.
Edit `/etc/rc.local` and add:

    # Start a uwsgi to act as emperor for vassals.
    /var/www/wsgi/virtualenvs/emperor/bin/uwsgi --ini /var/www/wsgi/emperor.ini

This will also set the correct ownership and permissions for the socket:

    $ ls -l /var/run/uwsgi/
    srw-r-----   nginx nginx   /var/run/uwsgi/pbsweb.sock

Note: Emperor will restart any application that stops if the application has an INI file
under the `confs` directory. If you don't want an application to start rename its 
INI file to, for instance, `other.ini_STOPPED`.

### Configure Nginx 

The `/etc/nginx/conf.d/default.conf` file should be similar to this:

    server {
        listen       80 default_server;
        listen       [::]:80 default_server;
        server_name  localhost;
        root         /var/www/html;
    
        location / {
            autoindex off;
        }
    
        # PBS web app.
        location /statuspbs/ {
            include uwsgi_params;
            uwsgi_pass unix://var/run/uwsgi/pbsweb.sock;
        }
    
        # Let nginx serve your static files so that requests 
        # for these never have to invoke python. 
        location /statuspbs/static/ {
            alias /var/www/wsgi/apps/pbsweb/static/;
        }
    }

Restart nginx:

    $ sudo service nginx restart

### Add nginx to PBS server operators

The app runs as `nginx` so this needs permission to query qstat. Otherwise 
`pbs.pbs_statjob()` will return an empty list.
You will find that it works OK when you run `pbsweb.py` from the command line, as
your probably in the PBS server operators list. 

    $ qmgr -c 'print server'
    set server operators += nginx@*

## Configure and Install PBSWeb

### Configure pbsweb.py

Edit `pbsweb.py` and look for the line `pbsserver = 'hpcnode0'`. You need to
enter here the hostname of your PBS server.
Also ensure that this PBS server hostname is correctly set in the test programs
under `tests/`.

You might also need to ensure that the PBS server hostname is listed in `/etc/hosts`.

### Configure PBSWeb's uWSGI 

The app's uWSGI file is `/var/www/wsgi/confs/pbsweb.ini`:

    [uwsgi]
    processes = 1
    socket = /var/run/uwsgi/pbsweb.sock
    chmod-socket = 640
    vaccum = true
    
    virtualenv   = /var/www/wsgi/virtualenvs/pbsweb/
    wsgi-file    = /var/www/wsgi/apps/pbsweb/pbsweb.py
    touch-reload = /var/www/wsgi/apps/pbsweb/pbsweb.py
    chdir        = /var/www/wsgi/apps/pbsweb/
    
    mount = /statuspbs=pbsweb:app
    manage-script-name = true

This does not need to be created as its supplied. Edit this if you wish to make any changes.
It will be installed by `install.sh`.

### Run ./install.sh 

Now check the install script and make any changes required and then run it to install 
the various files.

    $ ./install.sh

At this stage you can test the web application using your production server
by going to `http://your-server/statuspbs/`

<a name="Tests">

## Tests

### Test the Application with Bottle’s in-built Server

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

