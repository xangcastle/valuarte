# -*- coding: utf-8 -*-
# Generated by Django 1.10 on 2017-04-17 22:25
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('dtracking', '0002_auto_20170417_2157'),
    ]

    operations = [
        migrations.AddField(
            model_name='gestion',
            name='referencia',
            field=models.CharField(max_length=35, null=True, verbose_name='Referencia Bancaria'),
        ),
    ]
