# -*- coding: utf-8 -*-
# Generated by Django 1.10 on 2017-09-04 19:11
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('dtracking', '0015_registro'),
    ]

    operations = [
        migrations.AddField(
            model_name='gestion',
            name='categoria',
            field=models.CharField(blank=True, max_length=50, null=True),
        ),
        migrations.AddField(
            model_name='gestion',
            name='valor',
            field=models.FloatField(blank=True, null=True),
        ),
    ]
