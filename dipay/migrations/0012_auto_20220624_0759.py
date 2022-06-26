# Generated by Django 3.2 on 2022-06-24 07:59

import datetime
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('dipay', '0011_auto_20220624_0725'),
    ]

    operations = [
        migrations.AddField(
            model_name='customer',
            name='remark',
            field=models.TextField(default='--', verbose_name='客户详情'),
        ),
        migrations.AlterField(
            model_name='inwardpay',
            name='create_date',
            field=models.DateField(default=datetime.datetime(2022, 6, 24, 7, 59, 44, 100761), verbose_name='汇入日期'),
        ),
    ]
