# -*- coding: utf-8 -*-
# Generated by Django 1.10rc1 on 2016-12-04 19:55


from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('scope', '0006_remove_article_time_written'),
    ]

    operations = [
        migrations.AlterField(
            model_name='article',
            name='description',
            field=models.CharField(blank=True, max_length=500),
        ),
    ]
