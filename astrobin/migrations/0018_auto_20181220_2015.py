# -*- coding: utf-8 -*-
# Generated by Django 1.9.13 on 2018-12-20 20:15
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ('astrobin', '0017_auto_20181204_1930'),
    ]

    operations = [
        migrations.AlterField(
            model_name='image',
            name='remote_source',
            field=models.CharField(blank=True,
                                   choices=[(None, b'---------'), (b'OWN', 'Non-commercial independent facility'),
                                            (None, b'---------'), (b'AC', b'AstroCamp'),
                                            (b'AHK', b'Astro Hostel Krasnodar'), (b'CS', b'ChileScope'),
                                            (b'DSP', b'Dark Sky Portal'), (b'DSC', b'DeepSkyChile'),
                                            (b'DSW', b'DeepSkyWest'), (b'eEyE', b'e-EyE Extremadura'),
                                            (b'GMO', b'Grand Mesa Observatory'),
                                            (b'HMO', b"Heaven's Mirror Observatory"),
                                            (b'IC', b'IC Astronomy Observatories'), (b'ITU', b'Image The Universe'),
                                            (b'iT', b'iTelescope'), (b'NMS', b'New Mexico Skies'),
                                            (b'OES', b'Observatorio El Sauce'),
                                            (b'RLD', b'Riverland Dingo Observatory'), (b'SLO', b'Slooh'),
                                            (b'SS', b'Sahara Sky'), (b'SPVO', b'San Pedro Valley Observatory'),
                                            (b'SRO', b'Sierra Remote Observatories'),
                                            (b'SRO2', b'Sky Ranch Observatory'), (b'SPOO', b'SkyPi Online Observatory'),
                                            (b'OTHER', 'None of the above')],
                                   help_text='Which remote hosting facility did you use to acquire data for this image?',
                                   max_length=8, null=True, verbose_name='Remote data source'),
        ),
    ]
