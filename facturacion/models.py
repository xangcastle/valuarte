# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models
from dtracking.models import Gestion


class prefacturaManager(models.Manager):
    def get_queryset(self):
        return super(prefacturaManager, self).get_queryset().filter(factura=True)


class Prefactura(Gestion):

    objects = models.Manager()
    objects = prefacturaManager()

    class Meta:
        proxy = True
