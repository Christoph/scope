# -*- coding: utf-8 -*-
# Generated by Django 1.9 on 2016-05-24 21:52
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('last24h', '0027_remove_send_email'),
    ]

    operations = [
        migrations.AddField(
            model_name='suggest',
            name='source',
            field=models.CharField(default='', max_length=200),
            preserve_default=False,
        ),
    ]
