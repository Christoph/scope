# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('last24h', '0023_remove_alert_email'),
    ]

    operations = [
        migrations.AddField(
            model_name='alert',
            name='feed_type',
            field=models.BooleanField(default=False),
        ),
    ]
