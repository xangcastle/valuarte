# -*- coding: utf-8 -*-
# Generated by Django 1.10.1 on 2017-10-03 09:49
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('dtracking', '0010_auto_20171003_0849'),
    ]

    operations = [
        migrations.AddField(
            model_name='tipogestion',
            name='dias',
            field=models.IntegerField(default=4, null=True, verbose_name='dias necesarios para el armado'),
        ),
        migrations.AlterField(
            model_name='tipogestion',
            name='tiempo_ejecucion',
            field=models.IntegerField(blank=True, help_text='Tiempo requerido en minutos para el levantamiento de datos de este tipo de avaluo', null=True, verbose_name='tiempo en minutos para el peritaje'),
        ),
    ]