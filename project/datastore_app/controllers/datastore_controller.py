from datastore_app import app
from flask import render_template, request, jsonify, make_response, abort, Response

@app.route('/')
def home():
    return render_template('index.html')
