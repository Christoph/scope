# -*- coding: utf-8 -*-
# Generated by Django 1.10rc1 on 2016-12-04 14:31
from __future__ import unicode_literals

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('scope', '0003_auto_20161202_1900'),
    ]

    operations = [
        migrations.RenameField(
            model_name='article',
            old_name='agent_ID',
            new_name='agent',
        ),
        migrations.RenameField(
            model_name='article',
            old_name='source_ID',
            new_name='source',
        ),
    ]
