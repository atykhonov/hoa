# -*- coding: utf-8 -*-
# Generated by Django 1.10.4 on 2017-01-26 00:35
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('osbb', '0045_auto_20170126_0032'),
    ]

    operations = [
        migrations.AlterField(
            model_name='servicecharge',
            name='tariff',
            field=models.IntegerField(default=None, null=True),
        ),
    ]