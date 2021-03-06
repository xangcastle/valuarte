# -*- coding: utf-8 -*-
# Generated by Django 1.10 on 2017-12-12 04:03
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('dtracking', '0007_auto_20171212_0318'),
    ]

    operations = [
        migrations.AddField(
            model_name='gestion',
            name='descuento',
            field=models.IntegerField(default=0, verbose_name='% descuento'),
        ),
        migrations.AlterField(
            model_name='gestion',
            name='status_gestion',
            field=models.CharField(blank=True, choices=[('RECEPCIONADO', 'RECEPCIONADO'), ('ASIGNADO A EVALUADOR', 'ASIGNADO A EVALUADOR'), ('LEVANTAMIENTO REALIZADO', 'LEVANTAMIENTO REALIZADO'), ('CONTROL DE CALIDAD', 'CONTROL DE CALIDAD'), ('EN REVISION FINAL DE INFORME', 'EN REVISION FINAL DE INFORME'), ('TERMINADO', 'TERMINADO')], default='RECEPCIONADO', max_length=60, null=True),
        ),
        migrations.AlterField(
            model_name='log_gestion',
            name='estado',
            field=models.CharField(choices=[('RECEPCIONADO', 'RECEPCIONADO'), ('ASIGNADO A EVALUADOR', 'ASIGNADO A EVALUADOR'), ('LEVANTAMIENTO REALIZADO', 'LEVANTAMIENTO REALIZADO'), ('CONTROL DE CALIDAD', 'CONTROL DE CALIDAD'), ('EN REVISION FINAL DE INFORME', 'EN REVISION FINAL DE INFORME'), ('TERMINADO', 'TERMINADO')], max_length=50, null=True),
        ),
    ]
