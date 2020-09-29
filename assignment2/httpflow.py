import requests
import sys
import schedule
import time
import yaml

from low_code_app.scheduler import Scheduler
from low_code_app.yamlparser import YamlParser

# def set_scheduler():
#     sec = 10
#     schedule.every(sec).seconds.do(http_client)
#
# set_scheduler()
# while True:
#     schedule.run_pending()
#     time.sleep(1)

if __name__ == "__main__":

    yaml_file = sys.argv[1]
    yaml_parser = YamlParser(sys.argv[1])
    step = yaml_parser.get_step()
    scheduler = yaml_parser.get_scheduler()
    scheduler_obj = Scheduler(scheduler)
    scheduler_obj.run_step(step)
