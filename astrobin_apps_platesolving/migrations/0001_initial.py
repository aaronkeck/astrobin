# -*- coding: utf-8 -*-
# Generated by Django 1.9.13 on 2017-10-17 12:19
from __future__ import unicode_literals

import django.core.validators
import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):
    initial = True

    dependencies = [
        ('contenttypes', '0002_remove_content_type_name'),
    ]

    operations = [
        migrations.CreateModel(
            name='PlateSolvingSettings',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('blind', models.BooleanField(default=True,
                                              help_text='Attempt to solve with no hints. In most cases this will work, but it will take longer.',
                                              verbose_name='Perform a blind solve')),
                ('scale_units', models.CharField(blank=True, choices=[(b'degwidth', 'Width of the field in degrees'), (
                    b'arcminwidth', 'Width of the field in arcminutes'), (b'arcsecperpix',
                                                                          'Resolution of the field in arcseconds/pixel')],
                                                 help_text=b'The units for the min/max field size settings below.',
                                                 max_length=16, null=True, verbose_name='Field size units')),
                ('scale_min', models.DecimalField(blank=True, decimal_places=3,
                                                  help_text='Estimate the lower bound for the width of this field.',
                                                  max_digits=8, null=True, verbose_name='Min field size')),
                ('scale_max', models.DecimalField(blank=True, decimal_places=3,
                                                  help_text='Estimate the upper bound for the width of this field.',
                                                  max_digits=8, null=True, verbose_name='Max field size')),
                ('center_ra', models.DecimalField(blank=True, decimal_places=3,
                                                  help_text='Center RA of the field in degrees, 0.000 to 360.000',
                                                  max_digits=7, null=True,
                                                  validators=[django.core.validators.MinValueValidator(0),
                                                              django.core.validators.MaxValueValidator(360)],
                                                  verbose_name='Center RA')),
                ('center_dec', models.DecimalField(blank=True, decimal_places=3,
                                                   help_text='Center dec of the field in degrees, -90.000 to +90.000',
                                                   max_digits=7, null=True,
                                                   validators=[django.core.validators.MinValueValidator(-90),
                                                               django.core.validators.MaxValueValidator(90)],
                                                   verbose_name='Center dec')),
                ('radius', models.DecimalField(blank=True, decimal_places=3,
                                               help_text='Tells the plate-solving engine to look within these many degrees of the given center RA and dec position.',
                                               max_digits=7, null=True,
                                               validators=[django.core.validators.MinValueValidator(0),
                                                           django.core.validators.MaxValueValidator(360)],
                                               verbose_name='Radius')),
            ],
        ),
        migrations.CreateModel(
            name='Solution',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('status', models.PositiveIntegerField(
                    choices=[(0, b'Missing'), (1, b'Pending'), (2, b'Failed'), (3, b'Success')], default=0)),
                ('submission_id', models.PositiveIntegerField(blank=True, null=True)),
                ('object_id', models.TextField()),
                ('image_file', models.ImageField(blank=True, null=True, upload_to=b'solutions')),
                ('skyplot_zoom1', models.ImageField(blank=True, null=True, upload_to=b'skyplots')),
                ('objects_in_field', models.TextField(blank=True, null=True)),
                ('ra', models.DecimalField(blank=True, decimal_places=3, max_digits=6, null=True)),
                ('dec', models.DecimalField(blank=True, decimal_places=3, max_digits=6, null=True)),
                ('pixscale', models.DecimalField(blank=True, decimal_places=3, max_digits=6, null=True)),
                ('orientation', models.DecimalField(blank=True, decimal_places=3, max_digits=6, null=True)),
                ('radius', models.DecimalField(blank=True, decimal_places=3, max_digits=6, null=True)),
                ('annotations', models.TextField(blank=True, null=True)),
                ('content_type',
                 models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='contenttypes.ContentType')),
                ('settings',
                 models.OneToOneField(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='solution',
                                      to='astrobin_apps_platesolving.PlateSolvingSettings')),
            ],
            options={
                'verbose_name': 'Solution',
            },
        ),
        migrations.AlterUniqueTogether(
            name='solution',
            unique_together=set([('content_type', 'object_id')]),
        ),
    ]
