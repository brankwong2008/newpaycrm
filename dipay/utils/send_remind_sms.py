# -*- coding: utf-8 -*-
"""
任务提醒短信独立脚本（配合系统 crontab 使用，无需 celery worker 常驻）
用法（crontab 示例，每天早上 8 点执行）:
    0 8 * * * /path/to/venv/bin/python /path/to/newpaycrm/dipay/utils/send_remind_sms.py >> /path/to/newpaycrm/logs/remind_sms.log 2>&1
逻辑与 dipay/tasks.py 里的 send_dailyplan_remind_sms 完全一致：
找出提醒日期已到、未发过短信、未完成的任务，给任务所有人发短信，
然后把 is_sms_sent 置 True、状态从'提醒'改为'进行'。
"""
import os
import sys
from pathlib import Path

import django

base_dir = Path(__file__).resolve().parent.parent.parent
sys.path.append(str(base_dir))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'paycrm.settings')

django.setup()

from dipay.tasks import send_dailyplan_remind_sms


if __name__ == '__main__':
    # .apply() 表示在当前进程内同步执行（不经过 redis 队列），
    # 与 celery worker 执行的是同一个函数，行为完全一致
    result = send_dailyplan_remind_sms.apply()
    print('执行结果:', result.get() if result.successful() else result)
