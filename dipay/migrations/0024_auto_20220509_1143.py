# Generated by Django 3.2 on 2022-05-09 11:43

import datetime
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('dipay', '0023_auto_20220509_0850'),
    ]

    operations = [
        migrations.AddField(
            model_name='inwardpay',
            name='remark',
            field=models.TextField(default='-', verbose_name='备注'),
        ),
        migrations.AlterField(
            model_name='inwardpay',
            name='create_date',
            field=models.DateField(default=datetime.datetime(2022, 5, 9, 11, 43, 27, 465826), verbose_name='汇入日期'),
        ),
    ]
