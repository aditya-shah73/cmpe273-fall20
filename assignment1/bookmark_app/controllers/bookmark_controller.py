import uuid

from bookmark_app import app
from flask import render_template, request, jsonify, make_response, abort, Response
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
        'count' : 0
    }
    if not bookmark_obj.find_url(bookmark['url']):
        bookmark_obj.insert_bookmark(id, bookmark)
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
    return render_template('qrcode.html', value = filename)


@app.route('/api/bookmarks/<int:bookmark_id>/stats')
def get_bookmarks_count(bookmark_id):
    if not bookmark_id:
        abort(400)
    value = bookmark_obj.find_bookmark_id(bookmark_id, increment_count = False)
    if value is None:
        abort(404)
    bookmark_in_cache = app.cache.get(str(bookmark_id))

    current_count = None
    if bookmark_in_cache:
        print("Found in cache!!")
        current_count = bookmark_in_cache
    else:
        print("Found in DB!!")
        current_count = bookmark_obj.get_counts_for_bookmark(bookmark_id)
        if not current_count:
            print("Not Found in cache and DB")
            abort(404)
        else:
            app.cache.set(str(bookmark_id), current_count)
    e_tag = request.headers.get('ETag')
    if e_tag:
        etag_list = [tag.strip() for tag in e_tag.split(',')]
        if str(current_count) in etag_list:
            r = Response(content_type = None, status=304)
            r.headers.add('ETag', current_count)
            return r
        else:
            response = jsonify({'count': current_count})
            response.headers.set('ETag', str(current_count))
            return response
    else:
        response = jsonify({'count': current_count})
        response.headers.set('ETag', str(current_count))
        return response


@app.errorhandler(404)
def not_found(error):
    return make_response(jsonify({'error': '404 Not found'}), 404)


@app.errorhandler(400)
def bad_request(error):
    return make_response(jsonify({'error': '400 Bad Request'}), 400)
