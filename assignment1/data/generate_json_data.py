import json
import uuid
import random
import os

from faker import Faker
from random import randint
from sqlitedict import SqliteDict
from collections import defaultdict

cwd = os.getcwd()

def move_up_directory(cwd):
    os.chdir(os.path.dirname(os.getcwd()))
    return os.getcwd()

def generate_data():
    fake = Faker('en_US')
    data = defaultdict(dict)
    with open(cwd + "/data.json", 'w') as outfile:
        for _ in range(20):
            id = str(uuid.uuid1().int)
            data[id] = {'name': fake.user_name(),
                        'url': fake.url(),
                        'description' : fake.sentence(),
                        'count': 0}
        json.dump(data, outfile)

def generate_sqlite_data(json_path):
    print(json_path)
    root_dir = move_up_directory(cwd)
    with open(json_path) as fp:
        json_data = json.load(fp)

    with SqliteDict(root_dir + '/bookmark.db', autocommit=True) as sqlite_data_obj:
        sqlite_data_obj["data"] = json_data

    print("A JSON data file was created")

if __name__ == "__main__":
    generate_data()
    generate_sqlite_data(cwd + "/data.json")
