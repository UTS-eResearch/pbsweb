# Testing PBSWeb

* [Command Line Tests](#command-line-tests)
* [Web Application Test with Bottle’s in-built Server](#web-application-test-with-bottles-in-built-server)

This covers tests which can be run to help debug any errors.

## Command Line Tests 

These are a few tests to check `pbs.py` works OK and to demonstrate how to
query PBS data structures.

    $ source /var/www/wsgi/virtualenvs/pbsweb/bin/activate
    (pbsweb)$ 
    $ cd tests

Prints the nodes available and their attributes:

    $ ./test_pbs_nodes.py 

Prints the queues available and their attributes:

    $ ./test_pbs_queues.py       

Prints the list of jobs and their attributes:

    $ ./test_pbs_jobs.py         

Test the `pbsutils.py` code:

    $ ./test_pbsutils.py

## Web Application Test with Bottle’s in-built Server

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

