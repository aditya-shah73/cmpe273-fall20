import os
import qrcode

from sqlitedict import SqliteDict

#Raise errors in final iteration
class Bookmark(object):

    cwd = os.getcwd()
    print(cwd)

    def db_open_connection(self):
        bookmark_dict = SqliteDict('bookmark.db', autocommit=True)
        return bookmark_dict

    def find_bookmark_id(self, bookmark_id):
        bookmark_dict = self.db_open_connection()
        for key, value in bookmark_dict.iteritems():
            if(str(bookmark_id) in value.keys()):
                response_dict = value[str(bookmark_id)]
                response_dict['id'] = str(bookmark_id)
                response_dict.pop('counts')
                return value[str(bookmark_id)]
        return None

    def build_qrcode(self, bookmark_id):
        data = self.find_bookmark_id(bookmark_id)
        if data is not None:
            filename = '/static/qrcodes/test_' + str(bookmark_id) + '.png'
            complete_filename = self.cwd + '/bookmark_app/static/qrcodes/test_' + str(bookmark_id) + '.png'
            img = qrcode.make(data['url'])
            img.save(complete_filename)
        return filename

    def find_url(self, url):
        bookmark_dict = self.db_open_connection()
        for key, value in bookmark_dict['data'].items():
            if url == value['url']:
                return True
        return False
