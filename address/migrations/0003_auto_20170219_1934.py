# -*- coding: utf-8 -*-
# Generated by Django 1.10.4 on 2017-02-19 19:34
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('address', '0002_auto_20170202_2133'),
    ]

    operations = [
        migrations.AlterField(
            model_name='apartment',
            name='number',
            field=models.IntegerField(),
        ),
        migrations.AlterField(
            model_name='house',
            name='number',
            field=models.IntegerField(),
        ),
    ]
