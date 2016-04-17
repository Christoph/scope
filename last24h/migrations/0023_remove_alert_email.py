# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('last24h', '0022_auto_20160327_2313'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='alert',
            name='email',
        ),
    ]
