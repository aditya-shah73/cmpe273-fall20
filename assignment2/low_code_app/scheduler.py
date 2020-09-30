import requests
import time


class Scheduler:

    def __init__(self, scheduler):
        self.scheduler = scheduler

    def http_client(self, config):
        try:
            print("Making a HTTP Client Request")
            print(config)
            if config['method'] == 'GET':
                print(config['url'])
                response = requests.get(config['url'])
                return response
            elif config['method'] == 'POST':
                response = requests.post(config['url'], data={'key':'value'})
                return response
            elif config['method'] == 'PUT':
                requests.put(config['url'], data={'key':'value'})
                return response
            elif config['method'] == 'DELETE':
                requests.delete(config['url'])
                return response
            elif config['method'] == 'HEAD':
                response = requests.head(config['url'])
                return response
        except:
            print('Error')
            return None


    def evaluate_condition(self, response, condition):
        print('Evaluating the conditions')
        if(condition['if']['equal']['left'] == 'http.response.code'):
            if(condition['if']['equal']['right'] == response.status_code):
                if(condition['then']['action'] == 'print'):
                    if(condition['then']['data'] == 'http.response.body'):
                        # print(response.content)
                        print(response.status_code)
        elif(condition['else']['action'] == 'print'):
            print(condition['else']['data'])


    def run_step(self, step):
        print("Run the steps from the YAML file")
        print(step)
        if step['type'] == 'HTTP_CLIENT':
            config = {
                'method' : step['method'],
                'url': step['outbound_url']
            }
            response = self.http_client(config)
            if response:
                self.evaluate_condition(response, step['condition'])
            else:
                print("Please enter a valid URL")
            # return response #dont return the response here
