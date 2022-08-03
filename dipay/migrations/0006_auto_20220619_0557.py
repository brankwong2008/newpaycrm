# Generated by Django 3.2 on 2022-06-19 05:57

import datetime
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('dipay', '0005_auto_20220619_0422'),
    ]

    operations = [
        migrations.AddField(
            model_name='pay2orders',
            name='record_num',
            field=models.IntegerField(default=10000, verbose_name='分配编号'),
        ),
        migrations.AlterField(
            model_name='inwardpay',
            name='create_date',
            field=models.DateField(default=datetime.datetime(2022, 6, 19, 5, 57, 7, 48553), verbose_name='汇入日期'),
        ),
    ]
