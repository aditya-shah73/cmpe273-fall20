import sys
import yaml
import requests

class YamlParser:

    def __init__(self, filepath):
        with open(filepath, 'r') as file:
            self.document = yaml.full_load(file)


    def get_steps(self):
        return self.document['Steps']


    def get_scheduler(self):
        return self.document['Scheduler']


    def print_action(self, data, response):
        print('Printing the actions')
        if data != 'Error' and 'header' in data:
            header_field = data.split('.')[-1]
            print(data + ' for the request is: ' + response.headers[header_field])
        else:
            print('Error')
        print('##################################')


    def http_client(self, config):
        try:
            print("Making a HTTP Client Request")
            print(config)
            print('##################################')
            if config['method'] == 'GET':
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
            print('Error making the API request')
            print('##################################')
            return None


    def invoke_step(self, step_number, data):
        print('Invoking a particular step')
        steps = self.get_steps()
        step = steps[step_number - 1][step_number]
        if (step['type'] == 'HTTP_CLIENT' and 'data' not in step['outbound_url']):
            config = {
                'method' : step['method'],
                'url': step['outbound_url']
                }
        else:
            config = {
                'method' : step['method'],
                'url' : data
            }
        print('##################################')
        if 'data' not in config['url']:
            response = self.http_client(config)
            if response:
                self.evaluate_condition(response, step['condition'])


    def evaluate_condition(self, response, condition):
        print('Evaluating the conditions')
        if(condition['if']['equal']['left'] == 'http.response.code' and condition['if']['equal']['right'] == response.status_code):
            if('print' in condition['then']['action']):
                self.print_action(condition['then']['data'], response)
            elif('invoke' in condition['then']['action']):
                step_number = condition['then']['action'].split(':')[-1]
                data = condition['then']['data']
                self.invoke_step(int(step_number), data)
        elif(condition['else']['action'] == '::print'):
            self.print_action(condition['else']['data'], response)


    def run_steps(self, steps, steps_to_execute):
        print("Run the steps from the YAML file")
        for i in steps_to_execute:
            step = steps[i - 1][i]
            self.invoke_step(i, step['outbound_url'])
