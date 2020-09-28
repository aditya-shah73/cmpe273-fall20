import requests
import sys
import schedule
import time
import yaml

with open(sys.argv[1], 'r') as file:
    document = yaml.full_load(file)


def http_client(config):
    print("Making a HTTP Client Request")
    # import pdb; pdb.set_trace()
    if config['method'] == 'GET':
        print(config['url'])
        if(requests.head(config['url']).status_code == 200):
            response = requests.get(config['url'])
            return response
    else:
        print('Enter a valid HTTP Request Method')
        return None


def evaluate_condition(response, condition):
    print('Evaluating the conditions')
    if(condition['if']['equal']['left'] == 'http.response.code'):
        if(condition['if']['equal']['right'] == response.status_code):
            if(condition['then']['action'] == 'print'):
                if(condition['then']['action'] == 'print'):
                    print(response.content)
                    # print(response.status_code)
    elif(condition['else']['action'] == 'print'):
        print(condition['else']['data'])


def run_step(step):
    print("Run the steps from the YAML file")
    if step['type'] == 'HTTP_CLIENT':
        config = {
            'method' : step['method'],
            'url': step['outbound_url']
        }
        response = http_client(config)
        if response:
            evaluate_condition(response, step['condition'])
        else:
            print("Please enter a valid URL")
        # return response #dont return the response here

def set_scheduler():
    sec = 10
    schedule.every(sec).seconds.do(http_client)


def parse_yaml(document):
    print('Parsing the input YAML file')
    step = document['Step']
    scheduler = document['Scheduler']
    run_step(step)


parse_yaml(document)

# set_scheduler()
# while True:
#     schedule.run_pending()
#     time.sleep(1)
