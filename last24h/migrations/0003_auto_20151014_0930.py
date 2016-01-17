# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('last24h', '0002_suggest'),
    ]

    operations = [
        migrations.AddField(
            model_name='suggest',
            name='custom',
            field=models.CharField(default='None', max_length=200),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='suggest',
            name='distance',
            field=models.FloatField(default=1.0),
            preserve_default=False,
        ),
    ]
