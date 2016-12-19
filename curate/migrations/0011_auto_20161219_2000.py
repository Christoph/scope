# -*- coding: utf-8 -*-
# Generated by Django 1.10rc1 on 2016-12-19 20:00
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('curate', '0010_article_curate_query_agent'),
    ]

    operations = [
        migrations.CreateModel(
            name='Article_Curate_Query_Selection',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('is_true', models.BooleanField(default=False)),
                ('article_curate_query', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='curate.Article_Curate_Query')),
            ],
        ),
        migrations.CreateModel(
            name='Curate_Customer_Selection',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100)),
                ('curate_customer', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='curate.Curate_Customer')),
            ],
        ),
        migrations.AddField(
            model_name='article_curate_query_selection',
            name='curate_cutomer_seletion',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='curate.Curate_Customer_Selection'),
        ),
    ]