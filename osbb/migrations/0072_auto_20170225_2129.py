# -*- coding: utf-8 -*-
# Generated by Django 1.10.4 on 2017-02-25 21:29
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('osbb', '0071_auto_20170225_2111'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='accountbalance',
            name='charge',
        ),
        migrations.RemoveField(
            model_name='accountbalance',
            name='service',
        ),
        migrations.AddField(
            model_name='accountbalance',
            name='service_charge',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='balances', to='osbb.ServiceCharge'),
        ),
    ]
