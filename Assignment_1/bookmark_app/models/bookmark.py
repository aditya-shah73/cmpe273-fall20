import os
import qrcode

from sqlitedict import SqliteDict
#Raise errors in final iteration
class Bookmark(object):

    cwd = os.getcwd()
    print(cwd)

    def show_string(self):
        print("Hello world")

    def db_open_connection(self):
        bookmark_dict = SqliteDict('bookmark.db', autocommit=True)
        return bookmark_dict

    def find_bookmark_id(self, bookmark_id):
        bookmark_dict = self.db_open_connection()
        for key, value in bookmark_dict.iteritems():
            if(str(bookmark_id) in value.keys()):
                return value[str(bookmark_id)]
        return None #change to false

    def build_qrcode(self, bookmark_id):
        data = self.find_bookmark_id(bookmark_id)
        if data is not None:
            filename = self.cwd + '/qrcodes/test_' + str(bookmark_id) + '.png'
            img = qrcode.make(data)
            img.save(filename)
        return filename

    def find_bookmark_id_from_payload(self, payload):
        bookmark_dict = self.db_open_connection()

        for key, value in bookmark_dict['data'].items():
            if payload == value:
                import pdb; pdb.set_trace()
                return key
        return False
