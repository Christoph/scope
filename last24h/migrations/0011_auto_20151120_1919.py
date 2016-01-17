# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        ('last24h', '0010_auto_20151120_1917'),
    ]

    operations = [
        migrations.AlterField(
            model_name='alert',
            name='user',
            field=models.ForeignKey(default=None, blank=True, to=settings.AUTH_USER_MODEL),
        ),
    ]
