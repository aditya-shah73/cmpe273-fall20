from flask import Flask, request, render_template, jsonify, make_response, abort
from sqlitedict import SqliteDict
import flask_monitoringdashboard as dashboard
import json
import uuid
import qrcode

app = Flask(__name__)
dashboard.bind(app)

id = uuid.uuid1()

#create a singleton instance for db
def db_open_connection():
    mydict = SqliteDict('bookmark.db', autocommit=True)
    a = dict(mydict)
    return mydict

@app.route('/')
def home():
    return render_template('index.html')

# Fix write to db issue and return 200ok
@app.route('/api/bookmarks', methods=['POST'])
def add_bookmarks():
    if not request.json:
        abort(400)
    mydict = db_open_connection()
    bookmark = {
        'id' : str(id.int),
        'name' : request.json['name'],
        'url' : request.json['url'],
        'description' : request.json['description']
    }
    mydict[''] = bookmark
    x = dict(mydict)
    print(x)
    mydict.close()
    return {'id': bookmark['id']}

#return 200ok
@app.route('/api/bookmarks/<int:bookmark_id>')
def get_bookmarks(bookmark_id):
    if not bookmark_id:
        abort(404)
    mydict = db_open_connection()
    for key, value in mydict.iteritems():
        if('id' in value.keys()):
            if(value['id'] == str(bookmark_id)):
                return value
    abort(404)

#When code is generated return a html page with the image
@app.route('/api/bookmarks/<int:bookmark_id>/qrcode')
def generate_qrcode(bookmark_id):
    if not bookmark_id:
        abort(404)
    mydict = db_open_connection()
    for key, value in mydict.iteritems():
        if('id' in value.keys()):
            if(value['id'] == str(bookmark_id)):
                data = value['url']
                filename = 'qrcodes/test_' + str(bookmark_id) + '.png'
                img = qrcode.make(data)
                img.save(filename)
    return "Code generated"

#create a html page for 404 error handling
@app.errorhandler(404)
def not_found(error):
    return make_response(jsonify({'error': 'Not found'}), 404)
