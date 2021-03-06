# -*- coding: utf-8 -*-
# Generated by Django 1.10rc1 on 2016-12-04 15:11


from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('scope', '0004_auto_20161204_1431'),
    ]

    operations = [
        migrations.AlterField(
            model_name='article',
            name='description',
            field=models.CharField(blank=True, max_length=200),
        ),
        migrations.AlterField(
            model_name='article',
            name='images',
            field=models.CharField(blank=True, max_length=200),
        ),
        migrations.AlterField(
            model_name='article',
            name='keywords',
            field=models.CharField(blank=True, max_length=200),
        ),
        migrations.AlterField(
            model_name='article',
            name='time_written',
            field=models.DateTimeField(blank=True),
        ),
    ]
