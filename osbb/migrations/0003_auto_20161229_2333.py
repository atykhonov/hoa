# -*- coding: utf-8 -*-
# Generated by Django 1.10.4 on 2016-12-29 23:33
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('osbb', '0002_auto_20161229_1508'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='housingcooperative',
            name='manager',
        ),
        migrations.AddField(
            model_name='user',
            name='cooperative',
            field=models.OneToOneField(null=True, on_delete=django.db.models.deletion.CASCADE, to='osbb.HousingCooperative'),
        ),
    ]