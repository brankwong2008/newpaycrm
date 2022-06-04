# Generated by Django 3.2 on 2022-05-09 08:50

import datetime
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('dipay', '0022_auto_20220509_0846'),
    ]

    operations = [
        migrations.AddField(
            model_name='inwardpay',
            name='customer',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='dipay.customer', verbose_name='客户'),
        ),
        migrations.AlterField(
            model_name='inwardpay',
            name='create_date',
            field=models.DateField(default=datetime.datetime(2022, 5, 9, 8, 50, 48, 449458), verbose_name='汇入日期'),
        ),
    ]
