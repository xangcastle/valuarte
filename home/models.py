from __future__ import unicode_literals

from django.db import models

# Create your models here.
from dtracking.models import *


class nicaragua_import(models.Model):
    departamento = models.CharField(max_length=300, null=True, blank=True)
    municipio = models.CharField(max_length=300, null=True, blank=True)
    barrio = models.CharField(max_length=300, null=True, blank=True)

    def save(self, *args, **kwargs):
        super(nicaragua_import, self).save()

        _departamento = Departamento.objects.filter(name=self.departamento).first()
        if not _departamento:
            _departamento, c = Departamento.objects.get_or_create(name=self.departamento)

        _municipio = Municipio.objects.filter(name=self.municipio, departamento=_departamento).first()
        if not _municipio:
            _municipio, c = Municipio.objects.get_or_create(name=self.municipio,
                                                            departamento=_departamento)

        _barrio = Barrio.objects.filter(name=self.barrio, municipio = _municipio).first()
        if not _barrio:
            _barrio, c = Barrio.objects.get_or_create(name=self.barrio,
                                                      municipio=_municipio)

        self.delete()
