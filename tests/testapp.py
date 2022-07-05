#!/usr/bin/env python3

from bottle import route, run
import bottle
import os, datetime

@route('/')
def foo():
    now = datetime.datetime.now().strftime('%y.%m.%d  %I:%M:%S %P')
    page = '''
    <html><body>
    <h1>Test App</h1>
    <p>This test app is alive and kicking at %s</p>
    </body></html>
    ''' % now
    return page

if __name__ == '__main__':
    bottle.debug(True)
    bottle.run(reloader=True, port=8080)
else:
    os.chdir(os.path.dirname(__file__))
    app = application = bottle.default_app()

