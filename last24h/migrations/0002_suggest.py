# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('last24h', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Suggest',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('title', models.CharField(max_length=200)),
                ('url', models.CharField(max_length=200)),
                ('summary', models.CharField(max_length=200)),
                ('keywords', models.CharField(max_length=200)),
            ],
        ),
    ]
