# -*- coding: utf-8 -*-
# Generated by Django 1.10rc1 on 2016-12-04 15:58


from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('scope', '0005_auto_20161204_1511'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='article',
            name='time_written',
        ),
    ]
