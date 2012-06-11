# -*- coding: utf-8 -*-
"""
    A WSGI/APPLICATION script that can be used to launch the application

    :copyright: (c) 2011 by Openlabs Technologies & Consulting (P) Limited
    :license: BSD, see LICENSE for more details.
"""

# Activate the virutalenv
import os
cwd = os.path.abspath(os.path.dirname(__file__))
app_root_path = os.path.dirname(os.path.join(cwd, '../'))
activate_this = '%s/bin/activate_this.py' % app_root_path
execfile(activate_this, dict(__file__=activate_this))


from nereid import Nereid
from nereid.sessions import Session
from nereid.contrib.locale import Babel
from werkzeug.contrib.sessions import FilesystemSessionStore


os.environ['PYTHON_EGG_CACHE'] = '%s/.egg_cache' % app_root_path

SITE = 'glorifiedcalculators.com'

CONFIG = dict(

    # The name of the website
    SITE = SITE,

    # The name of database
    DATABASE_NAME = 'nereid',

    EMAIL_FROM = 'sales@openlabs.co.in',
    # Static file root. The root location of the static files. The static/ will
    # point to this location. It is recommended to use the web server to serve
    # static content
    #STATIC_FILEROOT = '%s/www/static/' % app_root_path,
    STATIC_FILEROOT = '%s/static/' % cwd,

    # Tryton Config file path
    TRYTON_CONFIG = '%s/etc/trytond.conf' % app_root_path,

    # Cache Memcached Servers
    # (Only if SESSION_STORE_CLASS or CACHE_TYPE is Memcached)
    # eg: ['localhost:11211']
    #CACHE_MEMCACHED_SERVERS = ['localhost:11211'],
    #CACHE_MEMCACHED_SERVERS = ['localhost:11211'],

    # If the application is to be configured in the debug mode
    DEBUG = False,

    TEMPLATE_LOADER_CLASS = 'nereid.templating.FileSystemLoader',
    TEMPLATE_SEARCH_PATH = '%s/templates/' % cwd,
    TRANSLATIONS_PATH = '%s/i18n/' % cwd,
)

# Create a new application
app = Nereid()
app.session_interface.session_store = FilesystemSessionStore(
    '/tmp', session_class=Session
)

# Update the configuration with the above config values
app.config.update(CONFIG)

# Initialise the app, connect to cache and backend
app.initialise()


babelized_app = Babel(app)
application = babelized_app.app.wsgi_app


class NereidHostChangeMiddleware(object):
    """
    A middleware which alters the HTTP_HOST so that you can test
    the site locally. This middleware replaces the HTTP_HOST with
    the value you prove to the :attr: site

    :param app: The application for which the middleware needs to work
    :param site: The value which should replace HTTP_HOST WSGI Environ
    """
    def __init__(self, app, site):
        self.app = app
        self.site = site

    def __call__(self, environ, start_response):
        environ['HTTP_HOST'] = self.site
        return self.app(environ, start_response)


if __name__ == '__main__':
    # If the file is launched from the CLI then launch the app using the debug
    # web server built into werkzeug
    #app.wsgi_app = NereidHostChangeMiddleware(app.wsgi_app, SITE)
    app.debug = True
    app.static_folder = '%s/templates/%s/static' % (cwd, SITE)
    app.run('0.0.0.0')
