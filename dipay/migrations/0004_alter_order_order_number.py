# Generated by Django 3.2 on 2022-04-26 12:10

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('dipay', '0003_auto_20220426_1206'),
    ]

    operations = [
        migrations.AlterField(
            model_name='order',
            name='order_number',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='dipay.applyorder', verbose_name='订单号'),
        ),
    ]
