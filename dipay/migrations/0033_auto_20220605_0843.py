# Generated by Django 3.2 on 2022-06-05 08:43

import datetime
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('dipay', '0032_auto_20220522_1327'),
    ]

    operations = [
        migrations.AlterField(
            model_name='inwardpay',
            name='create_date',
            field=models.DateField(default=datetime.datetime(2022, 6, 5, 8, 43, 15, 178189), verbose_name='汇入日期'),
        ),
        migrations.AlterField(
            model_name='inwardpay',
            name='payer',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='dipay.payer', verbose_name='付款人'),
        ),
    ]
