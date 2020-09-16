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
    if bookmark not in mydict['data'].values():
        mydict_data = mydict.get('data')
        mydict_data[id] = bookmark
        mydict['data'] = mydict_data
        import pdb; pdb.set_trace()
        mydict.close()
        return {'id': id}
    else:
        id = bookmark_obj.find_bookmark_id_from_payload(bookmark)
        # DO we need to tell if duplicate data was added 
        return {'id': id}

@app.route('/api/bookmarks/<int:bookmark_id>')
def get_bookmarks(bookmark_id):
    if not bookmark_id:
        abort(404)
    value = bookmark_obj.find_bookmark_id(bookmark_id)
    if value is not None:
        return value
    abort(404)

@app.route('/api/bookmarks/<int:bookmark_id>/qrcode')
def generate_qrcode(bookmark_id):
    if not bookmark_id:
        abort(404)
    filename = bookmark_obj.build_qrcode(bookmark_id)
    if filename is not None:
        print(filename)
    return render_template('qrcode.html')


#create a html page for 404 error handling
@app.errorhandler(404)
def not_found(error):
    return make_response(jsonify({'error': 'Not found'}), 404)
