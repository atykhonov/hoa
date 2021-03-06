# -*- coding: utf-8 -*-
# Generated by Django 1.10.4 on 2017-01-10 16:39
from __future__ import unicode_literals

from django.db import migrations


def make_default_service_required(apps, schema_editor):
    Service = apps.get_model('osbb', 'Service')
    service = Service.objects.get(name='Квартплата')
    service.required = True
    service.save()


class Migration(migrations.Migration):

    dependencies = [
        ('osbb', '0018_auto_20170110_1637'),
    ]

    operations = [
        migrations.RunPython(make_default_service_required),
    ]
