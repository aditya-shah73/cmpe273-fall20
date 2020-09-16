__version__ = '0.1'
from flask import Flask
import flask_monitoringdashboard as dashboard

app = Flask('bookmark_app')
app.debug = True
dashboard.bind(app)

from bookmark_app.controllers import *
