# -*- coding: utf-8 -*-
# Generated by Django 1.10 on 2017-04-18 04:14
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='nicaragua_import',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('codigo_departamento', models.CharField(blank=True, max_length=300, null=True)),
                ('departamento', models.CharField(blank=True, max_length=300, null=True)),
                ('codigo_municipio', models.CharField(blank=True, max_length=300, null=True)),
                ('municipio', models.CharField(blank=True, max_length=300, null=True)),
                ('codigo_barrio', models.CharField(blank=True, max_length=300, null=True)),
                ('barrio', models.CharField(blank=True, max_length=300, null=True)),
            ],
        ),
    ]
