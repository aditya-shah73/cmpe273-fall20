__version__ = '0.1'
from flask import Flask
import flask_monitoringdashboard as dashboard

app = Flask('datastore_app')
app.debug = True
dashboard.bind(app)

from datastore_app.controllers import *
