# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('last24h', '0017_auto_20151122_2245'),
    ]

    operations = [
        migrations.CreateModel(
            name='Send',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('email', models.EmailField(max_length=254)),
                ('query', models.CharField(max_length=200)),
                ('string', models.CharField(max_length=200)),
                ('user', models.ForeignKey(default=None, to=settings.AUTH_USER_MODEL, null=True)),
            ],
        ),
    ]
