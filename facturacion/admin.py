# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.contrib import admin
from .models import *
# Register your models here.

class prefactura_admin(admin.ModelAdmin):
    date_hierarchy = 'fecha_facturacion'
    list_display = ('barra', 'fecha_facturacion', 'destinatario', 'identificacion',
                    'telefonos', 'banco', 'banco_ejecutivo')
    search_fields = ('barra', 'destinatario', 'identificacion')
    list_filter = ('banco', 'banco_ejecutivo')
    actions = ['facturar', ]

    def facturar(self, request, queryset):
        return ""

admin.site.register(Prefactura, prefactura_admin)