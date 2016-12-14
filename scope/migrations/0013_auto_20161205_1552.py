# -*- coding: utf-8 -*-
# Generated by Django 1.10rc1 on 2016-12-05 15:52
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('contenttypes', '0002_remove_content_type_name'),
        ('scope', '0012_auto_20161205_1536'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='source',
            name='name',
        ),
        migrations.AddField(
            model_name='source',
            name='product_customer_id',
            field=models.PositiveIntegerField(default=1),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='source',
            name='product_customer_type',
            field=models.ForeignKey(default=1, on_delete=django.db.models.deletion.CASCADE, related_name='product_customer', to='contenttypes.ContentType'),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='source',
            name='agent_type',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='agent_type', to='contenttypes.ContentType'),
        ),
    ]