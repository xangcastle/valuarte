# -*- coding: utf-8 -*-
# Generated by Django 1.10 on 2017-04-20 02:49
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('dtracking', '0004_log_gestion'),
    ]

    operations = [
        migrations.AlterField(
            model_name='log_gestion',
            name='estado',
            field=models.CharField(choices=[('RECEPCIONADO', 'RECEPCIONADO'), ('ASIGNADO A EVALUADOR', 'ASIGNADO A EVALUADOR'), ('LEVANTAMIENTO REALIZADO', 'LEVANTAMIENTO REALIZADO'), ('EN REVISION FINAL DE INFORME', 'EN REVISION FINAL DE INFORME'), ('TERMINADO', 'TERMINADO')], max_length=50),
        ),
    ]
