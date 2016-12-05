# -*- coding: utf-8 -*-
# Generated by Django 1.10rc1 on 2016-12-04 14:31
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('curate', '0002_auto_20161202_1900'),
    ]

    operations = [
        migrations.RenameField(
            model_name='article_curate_query',
            old_name='article_ID',
            new_name='article',
        ),
        migrations.RenameField(
            model_name='article_curate_query',
            old_name='curate_query_ID',
            new_name='curate_query',
        ),
        migrations.RenameField(
            model_name='curate_customer',
            old_name='customer_id',
            new_name='customer',
        ),
        migrations.RenameField(
            model_name='curate_query',
            old_name='curate_customer_ID',
            new_name='curate_customer',
        ),
        migrations.AddField(
            model_name='curate_query',
            name='no_clusters',
            field=models.IntegerField(blank=True, null=True),
        ),
    ]