# -*- coding: utf-8 -*-
# Generated by Django 1.10.4 on 2017-02-20 20:40
from __future__ import unicode_literals

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('osbb', '0063_auto_20170220_0208'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='house',
            name='apartments_count',
        ),
    ]
