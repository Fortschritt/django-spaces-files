# -*- coding: utf-8 -*-
# Generated by Django 1.9b1 on 2015-11-21 17:27
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('spaces_files', '0003_auto_20151121_1821'),
    ]

    operations = [
        migrations.AlterField(
            model_name='file',
            name='name',
            field=models.CharField(blank=True, max_length=255, null=True),
        ),
    ]
