# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ('last24h', '0014_auto_20151122_2002'),
    ]

    operations = [
        migrations.AlterField(
            model_name='query',
            name='time',
            field=models.DateTimeField(default=django.utils.timezone.now),
        ),
    ]
