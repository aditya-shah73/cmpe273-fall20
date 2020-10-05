import requests
import schedule
import time


class Scheduler:

    def __init__(self, yaml_parser):
        self.yaml_parser = yaml_parser

    def parse_cron(self):
        schedule = self.yaml_parser.get_scheduler()
        print(schedule)
        cron = schedule['when']
        x = cron.split(" ")
        print(x)


    def testing(self):
        print('=====================================================================================================================')
        steps = self.yaml_parser.get_steps()
        self.yaml_parser.run_steps(steps)


    def set_scheduler(self):
        schedule.every(5).seconds.do(self.testing)
        while True:
            schedule.run_pending()
            time.sleep(1)
