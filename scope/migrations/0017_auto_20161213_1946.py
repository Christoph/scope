# -*- coding: utf-8 -*-
# Generated by Django 1.10rc1 on 2016-12-13 19:46


from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('scope', '0016_auto_20161212_2139'),
    ]

    operations = [
        migrations.AlterField(
            model_name='article',
            name='title',
            field=models.CharField(max_length=500),
        ),
        migrations.AlterField(
            model_name='article',
            name='url',
            field=models.CharField(max_length=1000),
        ),
    ]
