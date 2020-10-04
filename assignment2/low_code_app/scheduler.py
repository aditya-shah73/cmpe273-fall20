import requests
import time


class Scheduler:

    def __init__(self, scheduler, yaml_parser):
        self.scheduler = scheduler
        # self.yaml_parser = yaml_parser
        yaml_parser.test()

    # def testing(self):
    #     yaml_parser.test()

    # def set_scheduler():
    #     sec = 10
    #     schedule.every(sec).seconds.do(http_client)
    #
    # set_scheduler()
    # while True:
    #     schedule.run_pending()
    #     time.sleep(1)
