# Generated by Django 3.2 on 2022-10-23 12:05

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('dipay', '0040_auto_20221023_2003'),
    ]

    operations = [
        migrations.RenameField(
            model_name='charge',
            old_name='agent',
            new_name='forwarder',
        ),
    ]
