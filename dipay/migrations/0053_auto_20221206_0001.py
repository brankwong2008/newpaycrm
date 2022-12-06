# Generated by Django 3.2 on 2022-12-05 16:01

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('dipay', '0052_auto_20221203_1529'),
    ]

    operations = [
        migrations.AddField(
            model_name='dailyplan',
            name='cc',
            field=models.ManyToManyField(related_name='cc', to='dipay.UserInfo', verbose_name='抄送'),
        ),
        migrations.AlterField(
            model_name='product',
            name='quote',
            field=models.ManyToManyField(blank=True, null=True, through='dipay.Quote', to='dipay.Supplier', verbose_name='报价单'),
        ),
    ]
