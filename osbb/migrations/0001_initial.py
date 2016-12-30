# -*- coding: utf-8 -*-
# Generated by Django 1.10.4 on 2016-12-29 03:13
from __future__ import unicode_literals

import django.contrib.auth.models
import django.contrib.auth.validators
from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('auth', '0008_alter_user_username_max_length'),
    ]

    operations = [
        migrations.CreateModel(
            name='User',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('password', models.CharField(max_length=128, verbose_name='password')),
                ('last_login', models.DateTimeField(blank=True, null=True, verbose_name='last login')),
                ('is_superuser', models.BooleanField(default=False, help_text='Designates that this user has all permissions without explicitly assigning them.', verbose_name='superuser status')),
                ('username', models.CharField(error_messages={'unique': 'A user with that username already exists.'}, help_text='Required. 150 characters or fewer. Letters, digits and @/./+/-/_ only.', max_length=150, unique=True, validators=[django.contrib.auth.validators.UnicodeUsernameValidator()], verbose_name='username')),
                ('first_name', models.CharField(blank=True, max_length=30, verbose_name='first name')),
                ('last_name', models.CharField(blank=True, max_length=30, verbose_name='last name')),
                ('is_staff', models.BooleanField(default=False, help_text='Designates whether the user can log into this admin site.', verbose_name='staff status')),
                ('is_active', models.BooleanField(default=True, help_text='Designates whether this user should be treated as active. Unselect this instead of deleting accounts.', verbose_name='active')),
                ('date_joined', models.DateTimeField(default=django.utils.timezone.now, verbose_name='date joined')),
                ('email', models.EmailField(max_length=255, unique=True, verbose_name='email address')),
                ('groups', models.ManyToManyField(blank=True, help_text='The groups this user belongs to. A user will get all permissions granted to each of their groups.', related_name='user_set', related_query_name='user', to='auth.Group', verbose_name='groups')),
                ('user_permissions', models.ManyToManyField(blank=True, help_text='Specific permissions for this user.', related_name='user_set', related_query_name='user', to='auth.Permission', verbose_name='user permissions')),
            ],
            options={
                'abstract': False,
                'verbose_name': 'user',
                'verbose_name_plural': 'users',
            },
            managers=[
                ('objects', django.contrib.auth.models.UserManager()),
            ],
        ),
        migrations.CreateModel(
            name='Apartment',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_date', models.DateTimeField(auto_now_add=True)),
                ('modified_date', models.DateTimeField(auto_now=True)),
                ('number', models.IntegerField()),
                ('floor', models.IntegerField(null=True)),
                ('entrance', models.IntegerField(null=True)),
                ('room_number', models.IntegerField(null=True)),
                ('total_area', models.FloatField(null=True)),
                ('dwelling_space', models.FloatField(null=True)),
                ('heating_area', models.FloatField(null=True)),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='ApartmentMeter',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_date', models.DateTimeField(auto_now_add=True)),
                ('modified_date', models.DateTimeField(auto_now=True)),
                ('apartment', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='osbb.Apartment')),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='ApartmentMeterIndicator',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_date', models.DateTimeField(auto_now_add=True)),
                ('modified_date', models.DateTimeField(auto_now=True)),
                ('date', models.DateField()),
                ('value', models.IntegerField()),
                ('apartment_meter', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='osbb.ApartmentMeter')),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='ApartmentTariff',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_date', models.DateTimeField(auto_now_add=True)),
                ('modified_date', models.DateTimeField(auto_now=True)),
                ('date', models.DateField()),
                ('deleted', models.BooleanField()),
                ('value', models.FloatField()),
                ('apartment', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='osbb.Apartment')),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='BaseModelTest',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_date', models.DateTimeField(auto_now_add=True)),
                ('modified_date', models.DateTimeField(auto_now=True)),
                ('name', models.CharField(max_length=50)),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='Charge',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_date', models.DateTimeField(auto_now_add=True)),
                ('modified_date', models.DateTimeField(auto_now=True)),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='House',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_date', models.DateTimeField(auto_now_add=True)),
                ('modified_date', models.DateTimeField(auto_now=True)),
                ('name', models.CharField(max_length=50)),
                ('address', models.CharField(max_length=100)),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='HouseTariff',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_date', models.DateTimeField(auto_now_add=True)),
                ('modified_date', models.DateTimeField(auto_now=True)),
                ('date', models.DateField()),
                ('value', models.FloatField()),
                ('house', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='osbb.House')),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='HousingCooperative',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_date', models.DateTimeField(auto_now_add=True)),
                ('modified_date', models.DateTimeField(auto_now=True)),
                ('name', models.CharField(max_length=255)),
                ('individual_tax_number', models.CharField(max_length=10)),
                ('edrpou', models.CharField(max_length=10)),
                ('certificate', models.CharField(max_length=10)),
                ('legal_address', models.CharField(max_length=255)),
                ('physical_address', models.CharField(max_length=255)),
                ('phone_number', models.CharField(max_length=13)),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='HousingCooperativeService',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_date', models.DateTimeField(auto_now_add=True)),
                ('modified_date', models.DateTimeField(auto_now=True)),
                ('notes', models.CharField(max_length=255)),
                ('housing_cooperative', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='osbb.HousingCooperative')),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='Meter',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_date', models.DateTimeField(auto_now_add=True)),
                ('modified_date', models.DateTimeField(auto_now=True)),
                ('type', models.CharField(max_length=10)),
                ('number', models.CharField(max_length=10)),
                ('unit', models.CharField(max_length=10)),
                ('entry_date', models.DateField(null=True)),
                ('verification_date', models.DateField(null=True)),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='PersonalAccount',
            fields=[
                ('created_date', models.DateTimeField(auto_now_add=True)),
                ('modified_date', models.DateTimeField(auto_now=True)),
                ('uid', models.CharField(max_length=100, primary_key=True, serialize=False)),
                ('prefix', models.CharField(max_length=10)),
                ('receipt_text', models.CharField(max_length=255)),
                ('apartment', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to='osbb.Apartment')),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='Service',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_date', models.DateTimeField(auto_now_add=True)),
                ('modified_date', models.DateTimeField(auto_now=True)),
                ('name', models.CharField(max_length=50)),
                ('unit', models.CharField(max_length=10)),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='Tariff',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_date', models.DateTimeField(auto_now_add=True)),
                ('modified_date', models.DateTimeField(auto_now=True)),
                ('service', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='osbb.Service')),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.AddField(
            model_name='housingcooperativeservice',
            name='service',
            field=models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to='osbb.Service'),
        ),
        migrations.AddField(
            model_name='housetariff',
            name='service',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='osbb.Service'),
        ),
        migrations.AddField(
            model_name='house',
            name='housing_cooperative',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='osbb.HousingCooperative'),
        ),
        migrations.AddField(
            model_name='apartmenttariff',
            name='service',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='osbb.Service'),
        ),
        migrations.AddField(
            model_name='apartmentmeter',
            name='meter',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='osbb.Meter'),
        ),
        migrations.AddField(
            model_name='apartment',
            name='house',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='osbb.House'),
        ),
    ]
