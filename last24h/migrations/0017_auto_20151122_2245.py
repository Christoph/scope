# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('last24h', '0016_auto_20151122_2220'),
    ]

    operations = [
        migrations.AlterField(
            model_name='alert',
            name='copies',
            field=models.NullBooleanField(),
        ),
    ]
