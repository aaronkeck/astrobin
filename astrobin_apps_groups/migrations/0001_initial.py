# -*- coding: utf-8 -*-
# Generated by Django 1.9.13 on 2017-10-17 12:19
from __future__ import unicode_literals

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):
    initial = True

    dependencies = [
        ('astrobin', '0001_initial'),
        ('pybb', '0006_forum_subscriptions'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Group',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('date_created', models.DateTimeField(auto_now_add=True)),
                ('date_updated', models.DateTimeField(auto_now=True)),
                ('name', models.CharField(max_length=512, unique=True, verbose_name='Name')),
                ('description', models.TextField(blank=True, help_text='HTML tags are allowed.', null=True,
                                                 verbose_name='Description')),
                ('category', models.PositiveSmallIntegerField(
                    choices=[(1, 'Professional network'), (11, 'Club or association'), (21, 'Internet community'),
                             (31, 'Friends or partners'), (41, 'Geographical area'), (51, 'Ad-hoc collaboration'),
                             (61, 'Specific to an imaging technique'), (71, 'Specific to an astrophotography target'),
                             (81, 'Specific to certain equipment'), (101, 'Other')], verbose_name='Category')),
                ('public', models.BooleanField(default=False,
                                               help_text='Public groups can be searched by anyone, and all their content is public.',
                                               verbose_name='Public group')),
                ('moderated', models.BooleanField(default=False,
                                                  help_text='Moderated groups have a moderation queue for posted images and join requests.',
                                                  verbose_name='Moderated group')),
                ('autosubmission', models.BooleanField(default=False,
                                                       help_text='Groups with automatic submissions always contain all public images from all members. Groups without automatic submission only contain images that are explicitly submitted to it.',
                                                       verbose_name='Automatic submission')),
                ('creator', models.ForeignKey(editable=False, on_delete=django.db.models.deletion.CASCADE,
                                              related_name='created_group_set', to=settings.AUTH_USER_MODEL)),
                ('forum', models.OneToOneField(blank=True, editable=False, null=True,
                                               on_delete=django.db.models.deletion.CASCADE, related_name='group',
                                               to='pybb.Forum')),
                ('images',
                 models.ManyToManyField(blank=True, null=True, related_name='part_of_group_set', to='astrobin.Image')),
                ('invited_users', models.ManyToManyField(blank=True, null=True, related_name='invited_group_set',
                                                         to=settings.AUTH_USER_MODEL)),
                ('join_requests', models.ManyToManyField(blank=True, null=True, related_name='join_requested_group_set',
                                                         to=settings.AUTH_USER_MODEL)),
                ('members', models.ManyToManyField(blank=True, null=True, related_name='joined_group_set',
                                                   to=settings.AUTH_USER_MODEL)),
                ('moderators', models.ManyToManyField(blank=True, null=True, related_name='moderated_group_set',
                                                      to=settings.AUTH_USER_MODEL)),
                ('owner', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='owned_group_set',
                                            to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'ordering': ['date_updated'],
            },
        ),
    ]
