# Generated by Django 3.2 on 2022-10-23 12:03

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('dipay', '0039_rename_insuance_charge_insurance'),
    ]

    operations = [
        migrations.RenameField(
            model_name='chargepay',
            old_name='frombank',
            new_name='bank',
        ),
        migrations.RenameField(
            model_name='chargepay',
            old_name='charges',
            new_name='charge',
        ),
        migrations.RenameField(
            model_name='chargepay',
            old_name='agent',
            new_name='forwarder',
        ),
    ]
