__version__ = '0.1'
from flask import Flask
from flask_caching import Cache

import flask_monitoringdashboard as dashboard

app = Flask('bookmark_app')
app.config['CACHE_TYPE'] = 'simple'
app.config['CACHE_THRESHOLD'] = 100
app.config['CACHE_DEFAULT_TIMEOUT'] = 0
app.cache = Cache(app)
app.debug = True
dashboard.bind(app)

from bookmark_app.controllers import *
