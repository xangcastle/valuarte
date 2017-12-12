# -*- coding: utf-8 -*-
# Generated by Django 1.10 on 2017-12-12 03:18
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('dtracking', '0006_auto_20171107_0956'),
    ]

    operations = [
        migrations.AddField(
            model_name='gestion',
            name='control',
            field=models.BooleanField(default=False, verbose_name='armado'),
        ),
        migrations.AddField(
            model_name='gestion',
            name='fecha_control',
            field=models.DateField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='gestion',
            name='revizada',
            field=models.BooleanField(default=False, verbose_name='armado'),
        ),
        migrations.AlterField(
            model_name='gestion',
            name='status_gestion',
            field=models.CharField(blank=True, choices=[('RECEPCIONADO', 'RECEPCIONADO'), ('ASIGNADO A EVALUADOR', 'ASIGNADO A EVALUADOR'), ('LEVANTAMIENTO REALIZADO', 'LEVANTAMIENTO REALIZADO'), ('EN REVISION FINAL DE INFORME', 'EN REVISION FINAL DE INFORME'), ('CONTROL DE CALIDAD', 'CONTROL DE CALIDAD'), ('TERMINADO', 'TERMINADO')], default='RECEPCIONADO', max_length=60, null=True),
        ),
        migrations.AlterField(
            model_name='log_gestion',
            name='estado',
            field=models.CharField(choices=[('RECEPCIONADO', 'RECEPCIONADO'), ('ASIGNADO A EVALUADOR', 'ASIGNADO A EVALUADOR'), ('LEVANTAMIENTO REALIZADO', 'LEVANTAMIENTO REALIZADO'), ('EN REVISION FINAL DE INFORME', 'EN REVISION FINAL DE INFORME'), ('CONTROL DE CALIDAD', 'CONTROL DE CALIDAD'), ('TERMINADO', 'TERMINADO')], max_length=50, null=True),
        ),
    ]