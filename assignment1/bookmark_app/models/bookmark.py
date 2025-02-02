import os
import qrcode

from bookmark_app import app
from sqlitedict import SqliteDict

class Bookmark(object):

    cwd = os.getcwd()
    print(cwd)

    def db_open_connection(self):
        bookmark_dict = SqliteDict('bookmark.db', autocommit=True)
        return bookmark_dict

    def find_bookmark_id(self, bookmark_id, increment_count = True):
        bookmark_dict = self.db_open_connection()
        mydict_data = bookmark_dict.get('data')
        for key, value in bookmark_dict.iteritems():
            if(str(bookmark_id) in value.keys()):
                response_dict = value[str(bookmark_id)]
                if increment_count:
                    response_dict['count'] += 1
                    # Updating the simple cache
                    app.cache.set(str(bookmark_id), response_dict['count'])
                mydict_data[str(bookmark_id)] = response_dict
                bookmark_dict['data'] = mydict_data
                print(mydict_data)
                bookmark_dict.close()
                response_dict['id'] = str(bookmark_id)
                response_dict.pop('count')
                return value[str(bookmark_id)]
        return None

    def build_qrcode(self, bookmark_id):
        data = self.find_bookmark_id(bookmark_id, increment_count = False)
        if data is not None:
            filename = '/static/qrcodes/' + str(bookmark_id) + '.png'
            complete_filename = self.cwd + '/bookmark_app/static/qrcodes/' + str(bookmark_id) + '.png'
            img = qrcode.make(data['url'])
            img.save(complete_filename)
        return filename

    def find_url(self, url):
        bookmark_dict = self.db_open_connection()
        for key, value in bookmark_dict['data'].items():
            if url == value['url']:
                return True
        return False

    def delete_url(self, bookmark_id):
        bookmark_dict = self.db_open_connection()
        mydict_data = bookmark_dict.get('data')
        mydict_data.pop(str(bookmark_id))
        bookmark_dict['data'] = mydict_data
        bookmark_dict.close()

    def insert_bookmark(self, id, payload):
        bookmark_dict = self.db_open_connection()
        mydict_data = bookmark_dict.get('data')
        mydict_data[id] = payload
        bookmark_dict['data'] = mydict_data
        bookmark_dict.close()

    def get_counts_for_bookmark(self, bookmark_id):
        bookmark_dict = self.db_open_connection()
        for key, value in bookmark_dict.iteritems():
            if(str(bookmark_id) in value.keys()):
                return value[str(bookmark_id)]['count']
        return False
