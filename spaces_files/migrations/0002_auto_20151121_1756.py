# -*- coding: utf-8 -*-
# Generated by Django 1.9b1 on 2015-11-21 16:56
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion
import django.db.models.manager
import mptt.fields


class Migration(migrations.Migration):

    dependencies = [
        ('spaces_files', '0001_initial'),
    ]

    operations = [
        migrations.AlterModelManagers(
            name='folder',
            managers=[
                ('_default_manager', django.db.models.manager.Manager()),
            ],
        ),
        migrations.AddField(
            model_name='folder',
            name='level',
            field=models.PositiveIntegerField(db_index=True, default=None, editable=False),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='folder',
            name='lft',
            field=models.PositiveIntegerField(db_index=True, default=None, editable=False),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='folder',
            name='rght',
            field=models.PositiveIntegerField(db_index=True, default=None, editable=False),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='folder',
            name='tree_id',
            field=models.PositiveIntegerField(db_index=True, default=None, editable=False),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='folder',
            name='parent',
            field=mptt.fields.TreeForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='children', to='spaces_files.Folder'),
        ),
    ]
