import sys
import yaml

class YamlParser:

    def __init__(self, filepath):
        with open(filepath, 'r') as file:
            self.document = yaml.full_load(file)

    def get_step(self):
        return self.document['Step']

    def get_scheduler(self):
        return self.document['Scheduler']


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
