# -*- coding: utf-8 -*-
# Generated by Django 1.10 on 2017-10-03 22:13
from __future__ import unicode_literals

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('dtracking', '0014_auto_20171003_2042'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='banco',
            options={'verbose_name_plural': 'bancos nacionales'},
        ),
        migrations.AlterModelOptions(
            name='ejecutivo',
            options={'verbose_name_plural': 'ejecutivos bancarios'},
        ),
    ]