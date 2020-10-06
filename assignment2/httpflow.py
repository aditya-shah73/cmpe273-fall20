import os
import sys
import yaml

from low_code_app.scheduler import Scheduler
from low_code_app.yamlparser import YamlParser

if __name__ == "__main__":

    yaml_file = sys.argv[1]
    if os.path.isfile(yaml_file):
        yaml_parser = YamlParser(sys.argv[1])
        scheduler_obj = Scheduler(yaml_parser)
        scheduler_obj.schedule_job()
    else:
        print('Please enter a valid file')
