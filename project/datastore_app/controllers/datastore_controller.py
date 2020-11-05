from datastore_app import app
from flask import render_template, request, jsonify, make_response, abort, Response

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/api/entries', methods=['GET', 'POST'])
def entries():
    if request.method == 'GET':
        print('GET')
        return {
            "key": "foo",
            "value": "bar"
        }
    elif request.method== 'POST':
        if not request.json:
            abort(400)
        print(request.json['key'])
        print(request.json['value'])
        return {'value': request.json['value']}, 201

@app.errorhandler(400)
def bad_request(error):
    return make_response(jsonify({'error': '400 Bad Request'}), 400)
