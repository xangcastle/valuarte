# -*- coding: utf-8 -*-
# Generated by Django 1.10 on 2017-11-06 17:37
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('dtracking', '0003_auto_20171026_0701'),
    ]

    operations = [
        migrations.AddField(
            model_name='gestion',
            name='priority',
            field=models.BooleanField(default=False, verbose_name='prioridad'),
        ),
    ]
