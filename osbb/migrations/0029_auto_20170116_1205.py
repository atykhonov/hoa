# -*- coding: utf-8 -*-
# Generated by Django 1.10.4 on 2017-01-16 12:05
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('osbb', '0028_auto_20170114_0026'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='house',
            options={'ordering': ['street', 'number']},
        ),
        migrations.AddField(
            model_name='service',
            name='meter',
            field=models.BooleanField(default=False),
        ),
    ]
