# -*- coding: utf-8 -*-
# Generated by Django 1.10.4 on 2017-02-25 09:55
from __future__ import unicode_literals

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('osbb', '0067_auto_20170225_0918'),
    ]

    operations = [
        migrations.RenameField(
            model_name='accountbalance',
            old_name='deduction',
            new_name='amount',
        ),
    ]