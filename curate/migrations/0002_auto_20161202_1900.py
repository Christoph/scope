# -*- coding: utf-8 -*-
# Generated by Django 1.10rc1 on 2016-12-02 19:00
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('scope', '0003_auto_20161202_1900'),
        ('curate', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Article_Curate_Query',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('is_selected', models.BooleanField(default=False)),
                ('rank', models.IntegerField(blank=True, null=True)),
                ('article_ID', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='scope.Article')),
            ],
        ),
        migrations.CreateModel(
            name='Curate_Customer',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('key', models.CharField(max_length=100)),
                ('expires', models.DateField()),
                ('customer_id', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='scope.Customer')),
            ],
        ),
        migrations.CreateModel(
            name='Curate_Query',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('time_stamp', models.DateField(auto_now_add=True)),
                ('processed_words', models.CharField(max_length=200)),
                ('clustering', models.CharField(max_length=200)),
                ('curate_customer_ID', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='curate.Curate_Customer')),
            ],
        ),
        migrations.DeleteModel(
            name='Select',
        ),
        migrations.AddField(
            model_name='article_curate_query',
            name='curate_query_ID',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='curate.Curate_Query'),
        ),
    ]