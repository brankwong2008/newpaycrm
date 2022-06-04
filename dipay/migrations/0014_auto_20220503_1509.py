# Generated by Django 3.2 on 2022-05-03 15:09

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('dipay', '0013_auto_20220502_1056'),
    ]

    operations = [
        migrations.AddField(
            model_name='applyorder',
            name='rcvd_amount',
            field=models.DecimalField(decimal_places=2, max_digits=15, null=True, verbose_name='到账金额'),
        ),
        migrations.AlterField(
            model_name='applyorder',
            name='amount',
            field=models.DecimalField(decimal_places=2, max_digits=15, null=True, verbose_name='发票金额'),
        ),
        migrations.AlterField(
            model_name='applyorder',
            name='status',
            field=models.SmallIntegerField(choices=[(0, '待确认'), (1, '已下单'), (2, '完结'), (3, '无效')], default=0, verbose_name='下单状态'),
        ),
    ]
