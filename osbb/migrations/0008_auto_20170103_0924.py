# -*- coding: utf-8 -*-
# Generated by Django 1.10.4 on 2017-01-03 09:24
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('osbb', '0007_auto_20170103_0722'),
    ]

    operations = [
        migrations.RenameField(
            model_name='apartmentmeterindicator',
            old_name='apartment_meter',
            new_name='meter',
        ),
        migrations.AlterField(
            model_name='meter',
            name='type',
            field=models.CharField(choices=[('HT', 'Heating'), ('EL', 'Electricity'), ('WT', 'Water and wastewater'), ('WH', 'Water heating'), ('GS', 'Gas')], max_length=2),
        ),
        migrations.AlterField(
            model_name='meter',
            name='unit',
            field=models.CharField(choices=[('M2', 'Square meters'), ('MK', 'Square meters per kilocalorie'), ('KW', 'Kilowatt'), ('CM', 'Cubic meter')], max_length=2),
        ),
    ]
