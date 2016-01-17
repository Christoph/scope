# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('last24h', '0006_auto_20151017_1403'),
    ]

    operations = [
        migrations.AlterField(
            model_name='suggest',
            name='distance',
            field=models.IntegerField(null=True, blank=True),
        ),
    ]
