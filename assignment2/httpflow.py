import requests
import sys
import schedule
import time
import yaml

with open(sys.argv[1], 'r') as file:
    document = yaml.full_load(file)
    print(document)

def http_client():
    r = requests.get('https://api.github.com/events')
    print("This is the HTTP Client")
    return r

schedule.every(10).seconds.do(http_client)

while True:
    schedule.run_pending()
