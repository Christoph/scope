# -*- coding: utf-8 -*-
# Generated by Django 1.10rc1 on 2017-02-20 11:28


from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('scope', '0022_agentnewspaper'),
    ]

    operations = [
        migrations.CreateModel(
            name='Newsletter',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=200)),
                ('email', models.EmailField(max_length=254)),
            ],
        ),
    ]
