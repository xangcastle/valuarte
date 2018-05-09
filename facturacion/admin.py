# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.contrib import admin
from .models import *
from import_export.admin import ImportExportModelAdmin
from .forms import DocumentoForm


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


class base_tabular(admin.TabularInline):
    extra = 0
    printed_readonly_fields = []
    def get_readonly_fields(self, request, obj=None):
        if not request.user.is_superuser and obj:
            if obj.impreso:
                return self.printed_readonly_fields
        return self.readonly_fields

class DetalleFactura(base_tabular):
    model = dFactura
    printed_readonly_fields = ['cantidad', 'descripcion', 'precio', 'diva', 'total']


class DocumentoAdmin(admin.ModelAdmin):
    ordering = ('-numero',)
    form = DocumentoForm
    date_hierarchy = 'fecha'
    change_form_template = "caja/documento.html"
    only_superuserfields = ('fecha', 'numero')
    printed_readonly_fields = ()

    def get_readonly_fields(self, request, obj=None):
        if request.user.is_superuser:
            return []
        if obj and obj.impreso:
            return self.printed_readonly_fields
        elif obj and obj.cliente:
            return self.only_superuserfields + ('nombre', 'telefono', 'ruc', 'direccion')
        else:
            return self.only_superuserfields

    def save_model(self, request, obj, form, change):
        if not obj.impreso:
            try:
                obj.saldo = obj.grantotal
            except:
                pass
        super(DocumentoAdmin, self).save_model(request, obj, form, change)


class FacturaAdmin(DocumentoAdmin):
    save_as = True
    change_form_template = "caja/factura.html"
    fields = (('fecha', 'numero', 'moneda'), 'nombre', ('ruc', 'telefono'), 'direccion',('pago', 'referencia'),
             ('subtotal', 'iva', 'grantotal'), ('saldo', 'ir', 'al'))
    inlines = [DetalleFactura, ]
    list_display = ('cliente', 'referencia', 'subtotal', 'iva', 'grantotal', 'saldo', 'pago', 'impreso', 'cancelada')
    list_filter = ('pago', 'cliente')
    readonly_fields = ('saldo', )
    printed_readonly_fields = ('fecha', 'numero', 'nombre', 'ruc', 'telefono', 'direccion',
                               'subtotal', 'iva', 'grantotal', 'pago', 'referencia', 'saldo')
    search_fields = ('numero', 'referencia', 'cliente__nombre', 'cliente__ruc')


class RetencionAdmin(admin.ModelAdmin):
    date_hierarchy = 'fecha'
    fields = (('fecha', 'numero', 'moneda'),
              ('retenido', 'telefono'),
              ('ruc', 'cedula'),
              'concepto',
              'factura',
              ('base', 'aplicado', 'monto'),
              ('banco', 'cheque'))
    list_display = ('retenido', 'monto', 'aplicado', 'impreso')
    list_filter = ('aplicado', 'impreso')
    search_fields = ('retenido', 'numero')
    change_form_template = "caja/retencion.html"


class RocAdmin(DocumentoAdmin):
    change_form_template = "caja/roc.html"
    fields = (('fecha', 'numero', 'monto'), ('banco', 'moneda', 'tc'), 'referencia', 'nombre', 'concepto')
    printed_readonly_fields = ('nombre', 'monto', 'efectivo', 'referencia', 'banco', 'tc')
    list_display = ('cliente', 'moneda', 'monto', 'monto_aplicado', 'concepto')
    list_filter = ('cliente',)
    search_fields = ('cliente__nombre', 'cliente__ruc', 'numero')

    def save_model(self, request, obj, form, change):
        obj.cliente = Cliente.objects.get(id=int(request.POST.get('cliente_id', None)))
        super(RocAdmin, self).save_model(request, obj, form, change)
        for i, o in enumerate(request.POST.getlist('factura_numero')):
            print(o)
            t = o.split(' - ')[0]
            n = o.split(' - ')[1]
            f = None
            if t == 'F':
                model = 'factura'
                f = Factura.objects.get(numero=int(n))
            print request.POST.getlist('factura_ir')[i]
            if float(request.POST.getlist('factura_ir', '0.0')[i]) > 0.0:
                n = request.POST.getlist('factura_numero_ir', None)[i]
                m = float(request.POST.getlist('factura_ir', '0.0')[i])
                f.numero_ir = n
                f.aplicar_ir(n, m)
            if float(request.POST.getlist('factura_al', '0.0')[i]) > 0.0:
                n = request.POST.getlist('factura_numero_al', None)[i]
                m = float(request.POST.getlist('factura_al')[i])
                f.numero_al = n
                f.aplicar_al(n, m)
            a, created = Abono.objects.get_or_create(roc=obj, tipo_doc=ContentType.objects.get(
                app_label='caja', model=model), nodoc=f.id)
            a.monto = float(request.POST.getlist('factura_abono')[i])
            a.moneda = f.moneda
            a.saldo = float(request.POST.getlist('saldo')[i])
            a.save()
            a.aplicar()


class ClienteAdmin(admin.ModelAdmin):
    change_form_template = "caja/cliente.html"
    list_display = ('nombre', 'ruc', 'telefono', 'direccion', 'limite_credito', 'saldo', 'disponible')

admin.site.register(Factura, FacturaAdmin)
admin.site.register(Retencion, RetencionAdmin)
admin.site.register(Roc, RocAdmin)
admin.site.register(Cliente, ClienteAdmin)


class tc_admin(ImportExportModelAdmin):
    date_hierarchy = 'fecha'
    list_display = ('fecha', 'oficial', 'compra', 'venta')
    ordering = ('fecha',)
    actions = []
admin.site.register(TC, tc_admin)