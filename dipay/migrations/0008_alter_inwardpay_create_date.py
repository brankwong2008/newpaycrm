# Generated by Django 3.2 on 2022-06-19 06:44

import datetime
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('dipay', '0007_auto_20220619_0603'),
    ]

    operations = [
        migrations.AlterField(
            model_name='inwardpay',
            name='create_date',
            field=models.DateField(default=datetime.datetime(2022, 6, 19, 6, 44, 49, 74626), verbose_name='汇入日期'),
        ),
    ]