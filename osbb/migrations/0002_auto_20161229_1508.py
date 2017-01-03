# -*- coding: utf-8 -*-
# Generated by Django 1.10.4 on 2016-12-29 15:08
from __future__ import unicode_literals

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('osbb', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='housingcooperative',
            name='manager',
            field=models.OneToOneField(null=True, on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL),
        ),
        migrations.AlterField(
            model_name='housingcooperative',
            name='certificate',
            field=models.CharField(blank=True, max_length=10),
        ),
        migrations.AlterField(
            model_name='housingcooperative',
            name='edrpou',
            field=models.CharField(blank=True, max_length=10),
        ),
        migrations.AlterField(
            model_name='housingcooperative',
            name='individual_tax_number',
            field=models.CharField(blank=True, max_length=10),
        ),
        migrations.AlterField(
            model_name='housingcooperative',
            name='legal_address',
            field=models.CharField(blank=True, max_length=255),
        ),
        migrations.AlterField(
            model_name='housingcooperative',
            name='phone_number',
            field=models.CharField(blank=True, max_length=13),
        ),
        migrations.AlterField(
            model_name='housingcooperative',
            name='physical_address',
            field=models.CharField(blank=True, max_length=255),
        ),
    ]