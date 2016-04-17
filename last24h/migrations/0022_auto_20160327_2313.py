# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('last24h', '0021_sources'),
    ]

    operations = [
        migrations.AddField(
            model_name='query',
            name='articlenumber',
            field=models.IntegerField(null=True, blank=True),
        ),
        migrations.AddField(
            model_name='query',
            name='words',
            field=models.IntegerField(null=True, blank=True),
        ),
    ]
