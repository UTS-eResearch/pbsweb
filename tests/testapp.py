#!/usr/bin/env python3

from bottle import route, run, request
import bottle
import os, datetime

@route('/')
def foo():
    now = datetime.datetime.now().strftime('%y.%m.%d  %I:%M:%S %P')
    page = '''
    <html><body>
    <h1>Test App</h1>
    <p>This test app is alive and kicking at %s</p>
    <p>Go to here to <a href='/testapp/more'>Show ENV</a></p>
    </body></html>
    ''' % now
    return page

@route('/more')
def show_env(): 
    now = datetime.datetime.now().strftime('%y.%m.%d  %I:%M:%S %P')
    env = request.environ
    html = '''
    <html><body><p>
    App 2 live and kicking at %s. &nbsp; Go to <a href='/app1'>App 1</a> <br><br>
    <a href='/app2'>Hide ENV</a>
    </p>
    ''' % now

    html += "<table>\n"
    for k in env.keys():
        html += "<tr><td>{}</td><td>{}</td></tr>\n".format(k, env[k])
    html += "</table>\n"
    html += "</body></html>"

    return html

if __name__ == '__main__':
    bottle.debug(True)
    bottle.run(reloader=True, port=8080)
else:
    os.chdir(os.path.dirname(__file__))
    app = application = bottle.default_app()

