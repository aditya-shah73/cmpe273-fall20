import os
import requests
import sys
import schedule
import time
import yaml

from low_code_app.scheduler import Scheduler
from low_code_app.yamlparser import YamlParser

if __name__ == "__main__":

    yaml_file = sys.argv[1]
    if os.path.isfile(yaml_file):
        yaml_parser = YamlParser(sys.argv[1])
        steps = yaml_parser.get_steps()
        scheduler = yaml_parser.get_scheduler()
        scheduler_obj = Scheduler(scheduler, yaml_parser)
        yaml_parser.run_steps(steps)
        # scheduler_obj.testing()

    else:
        print('Please enter a valid file')
