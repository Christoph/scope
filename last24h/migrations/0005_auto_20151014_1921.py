# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('last24h', '0004_auto_20151014_1123'),
    ]

    operations = [
        migrations.AlterField(
            model_name='suggest',
            name='distance',
            field=models.DecimalField(null=True, max_digits=4, decimal_places=3, blank=True),
        ),
    ]
