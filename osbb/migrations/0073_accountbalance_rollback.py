# -*- coding: utf-8 -*-
# Generated by Django 1.10.4 on 2017-02-25 21:47
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('osbb', '0072_auto_20170225_2129'),
    ]

    operations = [
        migrations.AddField(
            model_name='accountbalance',
            name='rollback',
            field=models.BooleanField(default=False),
        ),
    ]
