# Generated by Django 3.2 on 2022-10-20 05:03

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('dipay', '0030_auto_20221015_2110'),
    ]

    operations = [

        # migrations.CreateModel(
        #     name='Forwarder',
        #     fields=[
        #         ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
        #         ('title', models.CharField(max_length=128, unique=True, verbose_name='货代名')),
        #         ('shortname', models.CharField(max_length=20, verbose_name='货代简称')),
        #         ('contact', models.CharField(default='-', max_length=20, verbose_name='货代联系人')),
        #         ('phone', models.CharField(default='-', max_length=11, verbose_name='电话')),
        #         ('email', models.CharField(default='-', max_length=128, verbose_name='邮件地址')),
        #         ('bank_account', models.TextField(default='--', verbose_name='银行信息')),
        #         ('remark', models.TextField(default='--', verbose_name='货代详情')),
        #     ],
        # ),
        # migrations.AddField(
        #     model_name='followorder',
        #     name='container',
        #     field=models.CharField(default='--', max_length=20, verbose_name='生产情况'),
        # ),
        migrations.AlterField(
            model_name='chance',
            name='channel',
            field=models.SmallIntegerField(choices=[(0, '阿里询盘'), (1, '阿里RFQ'), (2, '1688'), (3, '广交会'), (4, '其他')], default=0, verbose_name='渠道'),
        ),

        migrations.AddField(
            model_name='charge',
            name='agent',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='dipay.forwarder', verbose_name='货代'),
        ),
        migrations.AddField(
            model_name='charge',
            name='followorder',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='dipay.followorder', verbose_name='跟单号'),
        ),
    ]