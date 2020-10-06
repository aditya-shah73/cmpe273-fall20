import schedule
import time

class Scheduler:

    def __init__(self, yaml_parser):
        self.yaml_parser = yaml_parser

    def run(self):
        print('=====================================================================================================================')
        steps = self.yaml_parser.get_steps()
        self.yaml_parser.run_steps(steps)


    def cron_scheduler(self, cron_list):
        min = cron_list[0]
        hour = cron_list[1]
        day = cron_list[2]
        if hour == day == '*':
            if min == '*':
                print('Running every minute')
                schedule.every().minute.do(self.run)
            elif int(min) >= 0 and int(min) < 10:
                print('Running every ' + min + ' minutes')
                schedule.every(int(min)).minutes.do(self.run)
            else:
                print('Enter a valid time')
                return
        else:
            if min == '*':
                min = '00'
            elif int(min) >= 0 and int(min) < 10:
                min = '0' + min
            else:
                print('Enter a valid time')
                return

            if hour == '*':
                hour = '00'
            elif int(hour) >= 0 and int(hour) < 10:
                hour = '0' + hour
            else:
                print('Enter a valid time')
                return

            time_of_day = hour + ':' + min

            if day == '*':
                print('Running every day at: ' + time_of_day)
                schedule.every().day.at(time_of_day).do(self.run)
            elif day == '0':
                print('Running every Sunday at: ' + time_of_day)
                schedule.every().sunday.at(time_of_day).do(self.run)
            elif day == '1':
                print('Running every Monday at: ' + time_of_day)
                schedule.every().monday.at(time_of_day).do(self.run)
            elif day == '2':
                print('Running every Tuesday at: ' + time_of_day)
                schedule.every().tuesday.at(time_of_day).do(self.run)
            elif day == '3':
                print('Running every Wednesday at: ' + time_of_day)
                schedule.every().wednesday.at(time_of_day).do(self.run)
            elif day == '4':
                print('Running every Thursday at: ' + time_of_day)
                schedule.every().thursday.at(time_of_day).do(self.run)
            elif day == '5':
                print('Running every Friday at: ' + time_of_day)
                schedule.every().friday.at(time_of_day).do(self.run)
            elif day == '6':
                print('Running every Saturday at: ' + time_of_day)
                schedule.every().saturday.at(time_of_day).do(self.run)
            else:
                print('Enter a valid time')
                return

        while True:
            schedule.run_pending()
            time.sleep(1)


    def schedule_job(self):
        schedule = self.yaml_parser.get_scheduler()
        print(schedule)
        cron = schedule['when']
        cron_list = cron.split(" ")
        self.cron_scheduler(cron_list)
