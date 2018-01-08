# -*- coding: utf-8 -*-
# Generated by Django 1.10 on 2018-01-08 15:08
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('dtracking', '0011_auto_20180104_2025'),
    ]

    operations = [
        migrations.AddField(
            model_name='gestion',
            name='fecha_prearmado',
            field=models.DateTimeField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='gestion',
            name='prearmado',
            field=models.BooleanField(default=False, verbose_name='prearmado'),
        ),
        migrations.AlterField(
            model_name='gestion',
            name='numero',
            field=models.CharField(blank=True, help_text='Numero registro catastro, para el caso de vehiculos el n\xfamero de chasis', max_length=65, null=True, verbose_name='N\xfamero Registro'),
        ),
        migrations.AlterField(
            model_name='gestion',
            name='status_gestion',
            field=models.CharField(blank=True, choices=[('RECEPCIONADO', 'RECEPCIONADO'), ('ASIGNADO A EVALUADOR', 'ASIGNADO A EVALUADOR'), ('LEVANTAMIENTO REALIZADO', 'LEVANTAMIENTO REALIZADO'), ('CONTROL DE CALIDAD', 'CONTROL DE CALIDAD'), ('EN REVISION FINAL DE INFORME', 'EN REVISION FINAL DE INFORME'), ('TERMINADO', 'TERMINADO'), ('CANCELADO', 'CANCELADO')], default='RECEPCIONADO', max_length=60, null=True),
        ),
        migrations.AlterField(
            model_name='log_gestion',
            name='estado',
            field=models.CharField(choices=[('RECEPCIONADO', 'RECEPCIONADO'), ('ASIGNADO A EVALUADOR', 'ASIGNADO A EVALUADOR'), ('LEVANTAMIENTO REALIZADO', 'LEVANTAMIENTO REALIZADO'), ('CONTROL DE CALIDAD', 'CONTROL DE CALIDAD'), ('EN REVISION FINAL DE INFORME', 'EN REVISION FINAL DE INFORME'), ('TERMINADO', 'TERMINADO'), ('CANCELADO', 'CANCELADO')], max_length=50, null=True),
        ),
    ]
