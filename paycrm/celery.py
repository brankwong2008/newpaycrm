
#!/usr/bin/env python
# -*- coding:utf-8 -*-

import os
from celery import Celery

# set the default Django settings module for the 'celery' program.
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'paycrm.settings')

app = Celery('celerytask')

# Using a string here means the worker doesn't have to serialize
# the configuration object to child processes.
# - namespace='CELERY' means all celery-related configuration keys
#   should have a `CELERY_` prefix.
app.config_from_object('django.conf:settings', namespace='CELERY')

# 定时任务调度：每天早上 8 点给提醒日期已到的任务发短信
from celery.schedules import crontab
app.conf.beat_schedule = {
    'send-dailyplan-remind-sms': {
        'task': 'dipay.tasks.send_dailyplan_remind_sms',
        'schedule': crontab(hour=8, minute=0),
    },
}
app.conf.timezone = 'Asia/Shanghai'

# Load task modules from all registered Django app configs.  去注册的apps中读取tasks.py
app.autodiscover_tasks()
