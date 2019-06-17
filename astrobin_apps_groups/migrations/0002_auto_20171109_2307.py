# -*- coding: utf-8 -*-
# Generated by Django 1.9.13 on 2017-11-09 23:07
from __future__ import unicode_literals

from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ('astrobin_apps_groups', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='group',
            name='images',
            field=models.ManyToManyField(blank=True, related_name='part_of_group_set', to='astrobin.Image'),
        ),
        migrations.AlterField(
            model_name='group',
            name='invited_users',
            field=models.ManyToManyField(blank=True, related_name='invited_group_set', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AlterField(
            model_name='group',
            name='join_requests',
            field=models.ManyToManyField(blank=True, related_name='join_requested_group_set',
                                         to=settings.AUTH_USER_MODEL),
        ),
        migrations.AlterField(
            model_name='group',
            name='members',
            field=models.ManyToManyField(blank=True, related_name='joined_group_set', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AlterField(
            model_name='group',
            name='moderators',
            field=models.ManyToManyField(blank=True, related_name='moderated_group_set', to=settings.AUTH_USER_MODEL),
        ),
    ]
