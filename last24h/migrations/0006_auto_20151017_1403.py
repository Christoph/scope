# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('last24h', '0005_auto_20151014_1921'),
    ]

    operations = [
        migrations.AlterField(
            model_name='suggest',
            name='summary',
            field=models.CharField(max_length=1000),
        ),
    ]
