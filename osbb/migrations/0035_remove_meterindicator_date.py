# -*- coding: utf-8 -*-
# Generated by Django 1.10.4 on 2017-01-20 20:24
from __future__ import unicode_literals

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('osbb', '0034_auto_20170120_2014'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='meterindicator',
            name='date',
        ),
    ]
