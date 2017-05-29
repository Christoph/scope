# -*- coding: utf-8 -*-
# Generated by Django 1.10rc1 on 2016-12-20 08:27


from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('curate', '0011_auto_20161219_2000'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='article_curate_query_selection',
            name='article_curate_query',
        ),
        migrations.RemoveField(
            model_name='article_curate_query_selection',
            name='curate_cutomer_seletion',
        ),
        migrations.RemoveField(
            model_name='article_curate_query',
            name='is_mistake',
        ),
        migrations.RemoveField(
            model_name='article_curate_query',
            name='is_selected',
        ),
        migrations.AddField(
            model_name='article_curate_query',
            name='selection_options',
            field=models.ManyToManyField(to='curate.Curate_Customer_Selection'),
        ),
        migrations.AddField(
            model_name='curate_customer_selection',
            name='color',
            field=models.CharField(default=b'#fff', max_length=100),
        ),
        migrations.DeleteModel(
            name='Article_Curate_Query_Selection',
        ),
    ]
