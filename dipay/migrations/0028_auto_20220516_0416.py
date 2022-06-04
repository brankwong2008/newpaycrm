# Generated by Django 3.2 on 2022-05-16 04:16

import datetime
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('dipay', '0027_auto_20220513_1252'),
    ]

    operations = [
        migrations.AlterField(
            model_name='applyorder',
            name='customer',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='dipay.customer', verbose_name='客户'),
        ),
        migrations.AlterField(
            model_name='applyorder',
            name='status',
            field=models.SmallIntegerField(choices=[(0, '申请中'), (1, '已配单号'), (2, '已下单'), (3, '完结'), (4, '固定账户'), (5, '无效')], default=0, verbose_name='订单状态'),
        ),
        migrations.AlterField(
            model_name='inwardpay',
            name='create_date',
            field=models.DateField(default=datetime.datetime(2022, 5, 16, 4, 16, 19, 129660), verbose_name='汇入日期'),
        ),
    ]
