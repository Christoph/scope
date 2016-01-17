# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('last24h', '0007_auto_20151029_2117'),
    ]

    operations = [
        migrations.AddField(
            model_name='suggest',
            name='images',
            field=models.CharField(default='', max_length=200),
            preserve_default=False,
        ),
    ]
