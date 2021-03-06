# -*- coding: utf-8 -*-
# Generated by Django 1.10.4 on 2017-01-10 16:21
from __future__ import unicode_literals

from django.db import migrations
from osbb.models import UNITS


def create_default_service(apps, schema_editor):
    Service = apps.get_model('osbb', 'Service')
    service = Service(name='Квартплата', unit=UNITS[0][0])
    service.save()


class Migration(migrations.Migration):

    dependencies = [
        ('osbb', '0016_auto_20170110_0145'),
    ]

    operations = [
        migrations.RunPython(create_default_service),
    ]
