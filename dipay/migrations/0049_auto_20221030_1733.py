# Generated by Django 3.2 on 2022-10-30 09:33

import datetime
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('dipay', '0048_auto_20221030_1731'),
    ]

    operations = [
        migrations.AddField(
            model_name='userinfo',
            name='forwarder',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='dipay.forwarder', verbose_name='绑定货代'),
        ),
        migrations.AlterField(
            model_name='chargepay',
            name='create_date',
            field=models.DateField(default=datetime.datetime(2022, 10, 30, 17, 33, 5, 61673), verbose_name='支付日期'),
        ),
    ]