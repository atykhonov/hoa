# -*- coding: utf-8 -*-
# Generated by Django 1.10.4 on 2017-01-25 22:54
from __future__ import unicode_literals

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('osbb', '0040_auto_20170125_2203'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='charge',
            name='date',
        ),
        migrations.RemoveField(
            model_name='charge',
            name='end_date',
        ),
        migrations.RemoveField(
            model_name='charge',
            name='indicator_beginning',
        ),
        migrations.RemoveField(
            model_name='charge',
            name='indicator_end',
        ),
        migrations.RemoveField(
            model_name='charge',
            name='start_date',
        ),
        migrations.RemoveField(
            model_name='charge',
            name='tariff',
        ),
    ]
