# -*- coding: utf-8 -*-
# Generated by Django 1.10.4 on 2017-02-02 16:46
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('address', '0001_initial'),
        ('osbb', '0048_delete_basemodeltest'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='house',
            options={},
        ),
        migrations.RemoveField(
            model_name='apartment',
            name='number',
        ),
        migrations.RemoveField(
            model_name='house',
            name='number',
        ),
        migrations.RemoveField(
            model_name='house',
            name='street',
        ),
        migrations.AddField(
            model_name='apartment',
            name='address',
            field=models.OneToOneField(default=None, on_delete=django.db.models.deletion.CASCADE, related_name='apartment_address', to='address.Address'),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='house',
            name='address',
            field=models.OneToOneField(default=None, on_delete=django.db.models.deletion.CASCADE, related_name='house_address', to='address.Address'),
            preserve_default=False,
        ),
    ]
