# -*- coding: utf-8 -*-
# Generated by Django 1.10.1 on 2017-09-29 00:03
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('dtracking', '0020_tipogestion_tiempo_ejecucion'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='gestion',
            name='programacion_fin',
        ),
        migrations.RemoveField(
            model_name='gestion',
            name='programacion_incio',
        ),
        migrations.AddField(
            model_name='gestion',
            name='notify',
            field=models.BooleanField(default=False, verbose_name='notificar'),
        ),
        migrations.AlterField(
            model_name='gestion',
            name='status_gestion',
            field=models.CharField(blank=True, choices=[('RECEPCIONADO', 'RECEPCIONADO'), ('ASIGNADO A EVALUADOR', 'ASIGNADO A EVALUADOR'), ('LEVANTAMIENTO REALIZADO', 'LEVANTAMIENTO REALIZADO'), ('EN REVISION FINAL DE INFORME', 'EN REVISION FINAL DE INFORME'), ('TERMINADO', 'TERMINADO')], default='RECEPCIONADO', max_length=60, null=True),
        ),
    ]
