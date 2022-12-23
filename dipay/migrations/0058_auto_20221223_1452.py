# Generated by Django 3.2 on 2022-12-23 06:52

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('dipay', '0057_pay2orders_rate'),
    ]

    operations = [
        migrations.AddField(
            model_name='applyorder',
            name='amount_check',
            field=models.BooleanField(default=False, verbose_name='发票金额确认否'),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='followorder',
            name='container',
            field=models.CharField(default='--', max_length=20, verbose_name='集装箱号'),
        ),
    ]
