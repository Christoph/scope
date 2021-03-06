# -*- coding: utf-8 -*-
# Generated by Django 1.10rc1 on 2016-12-13 22:32


from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('scope', '0016_auto_20161212_2139'),
    ]

    operations = [
        migrations.CreateModel(
            name='AgentEventRegistry',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('user', models.CharField(blank=True, max_length=100)),
                ('pwd', models.CharField(blank=True, max_length=100)),
                ('lang', models.CharField(blank=True, max_length=10)),
                ('concepts', models.CharField(blank=True, max_length=200)),
                ('locations', models.CharField(blank=True, max_length=200)),
            ],
        ),
        migrations.RemoveField(
            model_name='article',
            name='description',
        ),
    ]
