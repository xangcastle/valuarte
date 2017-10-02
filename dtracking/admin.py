# -*- coding: utf-8 -*-
from django.contrib import admin
from base.admin import entidad_admin
from grappelli.forms import GrappelliSortableHiddenMixin
from django.contrib.admin import widgets
from django import forms
from django.shortcuts import render_to_response
from django.template import RequestContext
from django.http import HttpResponseRedirect
from django.conf.urls import url
from .models import *
from datetime import datetime
from django.contrib.auth.models import User
from django.contrib.admin import site
import adminactions.actions as actions
actions.add_to_site(site)


class detalle_tabular(GrappelliSortableHiddenMixin, admin.TabularInline):
    model = DetalleGestion
    extra = 0
    fields = ('nombreVariable', 'tipo', 'titulo', 'habilitado', 'requerido', 'imprime',
    'orden')
    sortable_field_name = 'orden'


class tipoGestion_admin(entidad_admin):
    change_form_template = "dtracking/tipo_gestion.html"
    inlines = [detalle_tabular, ]
    list_display = ('prefijo', 'name', 'errores')



class gestion_admin(entidad_admin):
    change_list_template = "dtracking/gestiones.html"
    change_form_template = "dtracking/gestion.html"
    date_hierarchy = "fecha"
    list_display = ('barra', 'banco', 'destinatario', 'tipo_gestion', 'valor', 'categoria',
                    'user', '_realizada', 'dias_retrazo')
    list_filter = ('banco', 'tipo_gestion', 'categoria','departamento', 'municipio', 'zona', 'user', 'realizada')
    search_fields = ('destinatario', 'departamento__name',
    'municipio__name', 'barrio__name', 'zona__name')

    # fields = (('fecha', 'barra'),
    #           ('status_gestion','tipo_gestion'),
    #           ('valor', 'categoria'),
    #           ('destinatario',  'identificacion'),
    #           'telefono', ('contacto', 'contacto_telefono'),
    #           ('banco', 'referencia'),'banco_ejecutivo',
    #           'direccion','direccion_envio',
    #           ('departamento', 'municipio'),
    #           ('fin_gestion', 'uso_gestion'),
    #           'observaciones')
    #
    # readonly_fields = ('user',)

    actions = ['action_perito', 'action_cancelar', 'action_asignar']

    class asignacion_form(forms.Form):
        fecha_asignacion = forms.DateTimeField(
            widget=widgets.AdminDateWidget())
        hora_asignacion = forms.DateTimeField(
            widget=widgets.AdminTimeWidget())
        usuario = forms.ModelChoiceField(label="Perito de Campo",
                                         queryset=User.objects.filter(
                                             id__in=Gestor.objects.all().values_list('user', flat=True)
                                         ))

    class valuador_form(forms.Form):
        usuario = forms.ModelChoiceField(label="Perito Evaluador",
                                         queryset=User.objects.exclude(
                                             id__in=Gestor.objects.all().values_list('user', flat=True)
                                         ))

    def action_asignar(self, request, queryset):
        data = {
        'queryset':queryset.filter(user__isnull=True),
        'total':queryset.filter(user__isnull=True).count(),
        'form':self.asignacion_form
        }
        return render_to_response('dtracking/asignacion.html', data)
    action_asignar.short_description = "Asignar Avaluo a Perito de Campo"

    def action_perito(self, request, queryset):
        data = {
        'queryset':queryset.filter(valuador__isnull=True),
        'total':queryset.filter(valuador__isnull=True).count(),
        'form':self.valuador_form
        }
        return render_to_response('dtracking/asignacion.html', data)
    action_perito.short_description = "Asignar Preparación del Reporte Final"

    def action_cancelar(self, request, queryset):
        motivo = "Gestiones canceladas por %s el %s" % (
        request.user.username, str(datetime.now())
        )
        cancelar_gestiones(queryset, motivo)
        self.message_user(request, motivo)
    action_cancelar.short_description = "Cancelar la ejecucion de gestiones seleccionadas"


class barrio_admin(entidad_admin):
    list_display = ('code', 'name', 'municipio')
    list_filter = ('municipio',)
    search_fields = ('code', 'name', 'municipio__name',
    'municipio__departamento__name')

    bh_template = "/admin/dtracking/barrios_huerfanos.html"

    def get_urls(self):
        urls = super(barrio_admin, self).get_urls()
        my_urls = [
            url(r'\d+/barrios_huerfanos/$', self.admin_site.admin_view(self.barrios_huerfanos)),
        ]
        return my_urls + urls

    def barrios_huerfanos(self, request):
        barrios = Barrio.objects.filter(
        id__in=ZonaBarrio.objects.all().values_list('barrio', flat=True))
        return render_to_response(self.bh_template, {
            'barrios': barrios,
            'opts': self.model._meta,
            'root_path': self.admin_site.root_path,
        }, context_instance=RequestContext(request))


class gestor_admin(admin.ModelAdmin):
    list_display = ('user', 'numero', 'image_thumb')


class import_admin(entidad_admin):
    list_display = ('destinatario', 'direccion', 'telefono', 'barrio',
    'municipio', 'departamento')

    actions = ['action_integrar']

    class integrationForm(forms.Form):
        _selected_action = forms.CharField(widget=forms.MultipleHiddenInput)
        fecha_asignacion = forms.DateField(
            widget=widgets.AdminDateWidget())
        fecha_vencimiento = forms.DateField(
            widget=widgets.AdminDateWidget())
        tipo_gestion = forms.ModelChoiceField(
            queryset=TipoGestion.objects.all().order_by('name'))
        eliminar = forms.BooleanField(required=False,
        help_text="eliminar registros despues de integrarlos")

    def action_integrar(self, request, queryset):
        message = ""
        form = None
        if 'apply' in request.POST:
            form = self.integrationForm(request.POST)
            queryset = Import.objects.filter(id__in=request.POST.getlist('primary', ''))
            msj = integrar(queryset)
            if form.is_valid():
                for c in queryset:
                    c.integrar_registro(form.cleaned_data['fecha_asignacion'],
                    form.cleaned_data['fecha_vencimiento'],
                    form.cleaned_data['tipo_gestion'],
                    form.cleaned_data['eliminar'])
                self.message_user(request, msj)
                return HttpResponseRedirect(
                    "/admin/dtracking/import")

        if not form:
            form = self.integrationForm(
                initial={
                    '_selected_action': request.POST.getlist(
                        admin.ACTION_CHECKBOX_NAME)})
        data = {'queryset': queryset, 'form': form,
            'header_tittle': 'Por Favor complete todos los campos',
            'explanation':
                'Los siguientes registros seran procesados:',
                'action': 'action_integrar'}
        self.message_user(request, message)
        return render_to_response('admin/base_action.html', data)


class RegistroAdmin(admin.ModelAdmin):
    list_display = ('tag', 'usuario', 'fecha')

admin.site.register(Gestion, gestion_admin)
admin.site.register(TipoGestion, tipoGestion_admin)
admin.site.register(Gestion_Fin)
admin.site.register(Gestion_Uso)
admin.site.register(Departamento, entidad_admin)
admin.site.register(Municipio, entidad_admin)
admin.site.register(Barrio, barrio_admin)
admin.site.register(Zona, entidad_admin)
admin.site.register(Gestor, gestor_admin)
admin.site.register(Registro, RegistroAdmin)