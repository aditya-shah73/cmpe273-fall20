import uuid

from bookmark_app import app
from flask import render_template, request, jsonify, make_response, abort
from bookmark_app.models.bookmark import Bookmark

bookmark_obj = Bookmark()

@app.route('/')
def home():
    return render_template('index.html')


@app.route('/api/bookmarks', methods=['POST'])
def add_bookmarks():
    if not request.json:
        abort(400)
    mydict = bookmark_obj.db_open_connection()
    id = str(uuid.uuid1().int)
    bookmark = {
        'name' : request.json['name'],
        'url' : request.json['url'],
        'description' : request.json['description'],
        'counts' : 0
    }
    if not bookmark_obj.find_url(bookmark['url']):
        print('URL not found in db')
        mydict_data = mydict.get('data')
        mydict_data[id] = bookmark
        mydict['data'] = mydict_data
        mydict.close()
        return {'id': id}
    else:
        abort(400)


@app.route('/api/bookmarks/<int:bookmark_id>', methods=['GET', 'DELETE'])
def get_bookmarks(bookmark_id):
    if request.method == 'GET':
        if not bookmark_id:
            abort(404)
        value = bookmark_obj.find_bookmark_id(bookmark_id)
        if value is not None:
            return value
        abort(404)
    elif request.method == 'DELETE':
        if not bookmark_id:
            abort(404)
        mydict = bookmark_obj.db_open_connection()
        if str(bookmark_id) not in mydict['data'].keys():
            abort(404)
        else:
            delete_value = bookmark_obj.find_bookmark_id(bookmark_id)
            bookmark_obj.delete_url(bookmark_id)
            return {'deleted_key': bookmark_id}, 204


@app.route('/api/bookmarks/<int:bookmark_id>/qrcode')
def generate_qrcode(bookmark_id):
    if not bookmark_id:
        abort(404)
    filename = bookmark_obj.build_qrcode(bookmark_id)
    if filename is not None:
        print(filename)
    return render_template('qrcode.html', value = filename)


#To be implemented
@app.route('/api/bookmarks/<int:bookmark_id>/stats')
def get_bookmarks_count(bookmark_id):
    if not bookmark_id:
        abort(404)
    return {'id': bookmark_id}


#create a html page for 404 error handling
@app.errorhandler(404)
def not_found(error):
    return make_response(jsonify({'error': '404 Not found'}), 404)

@app.errorhandler(400)
def bad_request(error):
    return make_response(jsonify({'error': '400 Bad Request'}), 400)
