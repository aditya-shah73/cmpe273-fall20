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

    def test(self):
        print('$$$$$$$$$$$$$$$$$$$$$$$$$$')
        print("This is from the scheduler")
        print('$$$$$$$$$$$$$$$$$$$$$$$$$$')

    def print_action(self, data, response):
        print('Printing the actions')
        if data != 'Error':
            print(data)
        else:
            print('Error')
        print('##################################')

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
            print('##################################')
        except:
            print('Error')
            print('##################################')
            return None


    def evaluate_condition(self, response, condition):
        print('Evaluating the conditions')
        if(condition['if']['equal']['left'] == 'http.response.code' and condition['if']['equal']['right'] == response.status_code):
            if('print' in condition['then']['action']):
                self.print_action(condition['then']['data'], response)
            elif('invoke' in condition['then']['action']):
                print('Invoke something else') #Need to implement this
        elif(condition['else']['action'] == '::print'):
            print(condition['else']['action'])
            self.print_action(condition['else']['data'], response)
        print('##################################')


    def run_steps(self, steps):
        print("Run the steps from the YAML file")
        for i in range(len(steps)):
            step = steps[i][i+1]
            if step['type'] == 'HTTP_CLIENT':
                config = {
                    'method' : step['method'],
                    'url': step['outbound_url']
                    }
            print(step)
            print('##################################')
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
