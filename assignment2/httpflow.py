import requests
import sys
import schedule
import time
import yaml

with open(sys.argv[1], 'r') as file:
    document = yaml.full_load(file)


def http_client(config):
    print("Making a HTTP Client Request")
    if config['method'] == 'GET':
        r = requests.get(config['url'])
        return r
    else:
        return 'Enter a valid HTTP Request Method'


def eval_condition(data, condition):
    return True


def run_step(step):
    print("Run the steps from the YAML file")
    if step == 'HTTP_CLIENT':
        config = {
            'method' : 'GET',
            'url': 'https://api.github.com/events'
        }
        response = http_client(config)
        # eval_condition(response, condition)
        return response


def set_scheduler():
    sec = 10
    schedule.every(sec).seconds.do(http_client)


def parse_yaml(document):
    print('Parsing the input YAML file')
    id = document['Step']['id']
    type = document['Step']['type']
    method = document['Step']['method']
    url = document['Step']['outbound_url']
    condition = document['Step']['condition']
    scheduler = document['Scheduler']
    result = run_step(type)
    return result


print(parse_yaml(document))

# set_scheduler()
# while True:
#     schedule.run_pending()
#     time.sleep(1)
