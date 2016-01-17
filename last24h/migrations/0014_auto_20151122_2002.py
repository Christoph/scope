# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import datetime
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('last24h', '0013_auto_20151121_1112'),
    ]

    operations = [
        migrations.RenameField(
            model_name='query',
            old_name='query_text',
            new_name='query',
        ),
        migrations.RemoveField(
            model_name='query',
            name='pub_date',
        ),
        migrations.AddField(
            model_name='alert',
            name='latest_url',
            field=models.CharField(max_length=200, null=True),
        ),
        migrations.AddField(
            model_name='query',
            name='string',
            field=models.CharField(default='', max_length=200),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='query',
            name='time',
            field=models.DateTimeField(default=datetime.datetime(2015, 11, 22, 20, 1, 22, 700284)),
        ),
        migrations.AddField(
            model_name='query',
            name='url',
            field=models.CharField(default='', max_length=200),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='query',
            name='user',
            field=models.ForeignKey(default=None, to=settings.AUTH_USER_MODEL, null=True),
        ),
    ]
