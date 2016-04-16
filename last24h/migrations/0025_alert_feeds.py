# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('last24h', '0024_alert_feed_type'),
    ]

    operations = [
        migrations.AddField(
            model_name='alert',
            name='feeds',
            field=models.CharField(max_length=600, null=True),
        ),
    ]
