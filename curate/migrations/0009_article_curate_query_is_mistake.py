# -*- coding: utf-8 -*-
# Generated by Django 1.10rc1 on 2016-12-07 09:00
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('curate', '0008_remove_curate_customer_sources'),
    ]

    operations = [
        migrations.AddField(
            model_name='article_curate_query',
            name='is_mistake',
            field=models.BooleanField(default=False),
        ),
    ]