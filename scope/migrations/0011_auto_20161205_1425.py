# -*- coding: utf-8 -*-
# Generated by Django 1.10rc1 on 2016-12-05 14:25
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('scope', '0010_auto_20161204_2007'),
    ]

    operations = [
        migrations.AlterField(
            model_name='article',
            name='url',
            field=models.CharField(max_length=500),
        ),
    ]
