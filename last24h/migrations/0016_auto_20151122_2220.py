# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('last24h', '0015_auto_20151122_2004'),
    ]

    operations = [
        migrations.AlterField(
            model_name='alert',
            name='frequency',
            field=models.SmallIntegerField(choices=[(10400, b'4 hours'), (31200, b'12 hours'), (62400, b'24 hours'), (172800, b'2 days'), (345600, b'4 days'), (604800, b'1 week')]),
        ),
    ]
