from django.test import TestCase

# Create your tests here.
import os

def get_exchange_rate():
    """每天定时获取常用汇率"""
    from apscheduler.schedulers.background import BackgroundScheduler
    from apscheduler.schedulers.blocking import BlockingScheduler

    from datetime import datetime
    # 输出时间
    def job():

        # os.mkdir('/Users/wongbrank/Desktop/make_pdf/test')
        print(datetime.now().strftime("%Y-%m-%d %H:%M:%S"), '获取汇率成功')

    # BlockingScheduler 阻塞式进程
    # scheduler = BlockingScheduler()

    # BackgroundScheduler 非阻塞式进程
    # scheduler = BlockingScheduler()
    scheduler = BackgroundScheduler()


    # 定时执行任务  cron方式
    print("设定exchange rate定时任务")
    # scheduler.add_job(job, 'cron', hour=12, minute=35)
    scheduler.add_job(job, 'interval', seconds=3)
    print("任务开始。。。。")
    scheduler.start()

get_exchange_rate()
import time

while True:
    time.sleep(2)


# import schedule
#
# def job():
#     print("I'm working...")
#
# schedule.every(3).seconds.do(job)  # 每隔10分钟执行一次任务
# schedule.every().hour.do(job)
# schedule.every().day.at("10:30").do(job)
# schedule.every().monday.do(job)
# schedule.every().wednesday.at("13:15").do(job)
#
# while True:
#     schedule.run_pending()
#
