# Generated by Django 3.2 on 2022-07-07 13:24

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('dipay', '0016_auto_20220706_2318'),
    ]

    operations = [
        migrations.AlterField(
            model_name='inwardpay',
            name='ttcopy',
            field=models.ImageField(null=True, upload_to='ttcopy', verbose_name='电汇水单'),
        ),
    ]
