# -*- coding: utf-8 -*-
# Generated by Django 1.10 on 2017-12-11 20:11
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('dtracking', '0006_auto_20171107_0956'),
    ]

    operations = [
        migrations.AlterField(
            model_name='gestion',
            name='revizada',
            field=models.BooleanField(default=False, verbose_name='armado'),
        ),
    ]