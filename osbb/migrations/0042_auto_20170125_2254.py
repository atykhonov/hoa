# -*- coding: utf-8 -*-
# Generated by Django 1.10.4 on 2017-01-25 22:54
from __future__ import unicode_literals

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('osbb', '0041_auto_20170125_2254'),
    ]

    operations = [
        migrations.RenameField(
            model_name='charge',
            old_name='value',
            new_name='total',
        ),
    ]
