# -*- coding: utf-8 -*-
# Generated by Django 1.10rc1 on 2017-03-01 11:05


from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('scope', '0023_newsletter'),
        ('curate', '0021_article_curate_query_bad_article'),
    ]

    operations = [
        migrations.AddField(
            model_name='article_curate_query',
            name='newsletter',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='scope.Newsletter'),
        ),
        migrations.AddField(
            model_name='curate_query',
            name='articles_before_filtering',
            field=models.IntegerField(blank=True, null=True),
        ),
    ]
