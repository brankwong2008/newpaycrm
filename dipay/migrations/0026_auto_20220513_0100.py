# Generated by Django 3.2 on 2022-05-13 01:00

import datetime
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('dipay', '0025_auto_20220509_1307'),
    ]

    operations = [
        migrations.CreateModel(
            name='Book',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=30, verbose_name='AuthorName')),
            ],
        ),
        migrations.AlterField(
            model_name='applyorder',
            name='sequence',
            field=models.IntegerField(blank=True, null=True, unique=True, verbose_name='订单序号'),
        ),
        migrations.AlterField(
            model_name='applyorder',
            name='status',
            field=models.SmallIntegerField(choices=[(0, '待审批'), (1, '已配单号'), (2, '已下单'), (3, '完结'), (4, '固定账户'), (5, '无效')], default=0, verbose_name='订单状态'),
        ),
        migrations.AlterField(
            model_name='inwardpay',
            name='amount',
            field=models.DecimalField(decimal_places=2, default=0, max_digits=9, verbose_name='水单金额'),
        ),
        migrations.AlterField(
            model_name='inwardpay',
            name='create_date',
            field=models.DateField(default=datetime.datetime(2022, 5, 13, 1, 0, 30, 861337), verbose_name='汇入日期'),
        ),
        migrations.AlterField(
            model_name='userinfo',
            name='department',
            field=models.SmallIntegerField(choices=[(1, '业务部'), (2, '跟单部'), (4, '财务部'), (8, '管理部')], default=1, verbose_name='部门'),
        ),
    ]
