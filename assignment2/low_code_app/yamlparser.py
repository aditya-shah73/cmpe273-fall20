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
        print('##############THIS IS INVOKE STEP####################')
        # print(step)
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


    def run_steps(self, steps):
        print("Run the steps from the YAML file")
        for i in range(len(steps)):
            step = steps[i][i+1]
            if step['type'] == 'HTTP_CLIENT':
                config = {
                    'method' : step['method'],
                    'url': step['outbound_url']
                    }
            # print(step)
            print('##################################')
            if 'data' not in config['url']:
                response = self.http_client(config)
                if response:
                    self.evaluate_condition(response, step['condition'])


# import yaml
# from cerberus import Validator
#
# schema = {
#     'purpose' : {'type' : 'string', 'required' : True},
#     'urls' : {'type': 'dict', 'schema' : {'files': {'type': 'list', 'schema' : {'type': 'string'}},
#     'total_urls_needed' : {'type': 'dict', 'schema': {'min': {'type': 'integer'}, 'max': {'type': 'integer'}}}}, 'required' :True },
#     'users' : {'type': 'dict', 'schema' : {'files': {'type': 'list', 'schema' : {'type': 'string'}},
#     'total_users_needed' : {'type': 'dict', 'schema':

# class YamlLoader:
#     def __init__(self, file_location):
#         self.yaml_obj = []
#         with open(file_location) as stream:
#             try:
#                 for data in yaml.load_all(stream, Loader=yaml.SafeLoader):
#                     self.yaml_obj.append(data)
#                 # Validate
#                 for config in self.yaml_obj:
#                     v = Validator(schema)
#                     if not v.validate(config, schema):
#                         print(v.errors)
#             except yaml
