# -*- coding: utf-8 -*-
# Generated by Django 1.11.1 on 2017-07-22 15:29
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('reader', '0002_auto_20170711_0832'),
    ]

    operations = [
        migrations.AlterField(
            model_name='article_reader_query',
            name='feed',
            field=models.ForeignKey(blank=True, on_delete=django.db.models.deletion.CASCADE, to='scope.RSSFeed'),
        ),
    ]
