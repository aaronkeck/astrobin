# -*- coding: utf-8 -*-
# Generated by Django 1.9.13 on 2017-11-09 23:07
from __future__ import unicode_literals

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ('astrobin_apps_iotd', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='iotd',
            name='image',
            field=models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to='astrobin.Image'),
        ),
    ]
