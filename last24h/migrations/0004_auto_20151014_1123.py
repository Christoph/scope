# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('last24h', '0003_auto_20151014_0930'),
    ]

    operations = [
        migrations.AlterField(
            model_name='suggest',
            name='distance',
            field=models.DecimalField(max_digits=4, decimal_places=3),
        ),
    ]
