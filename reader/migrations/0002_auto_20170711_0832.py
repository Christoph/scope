# -*- coding: utf-8 -*-
# Generated by Django 1.11.1 on 2017-07-11 08:32
from __future__ import unicode_literals

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('reader', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='user_reader',
            name='user',
            field=models.ForeignKey(default=None, on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL),
        ),
    ]
