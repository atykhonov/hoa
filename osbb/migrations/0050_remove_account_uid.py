# -*- coding: utf-8 -*-
# Generated by Django 1.10.4 on 2017-02-06 16:05
from __future__ import unicode_literals

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('osbb', '0049_auto_20170202_1646'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='account',
            name='uid',
        ),
    ]
