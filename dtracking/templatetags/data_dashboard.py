# -*- coding: utf-8 -*-
from ..models import *
from django.db.models import Sum
from datetime import datetime, timedelta
from django.utils import timezone
from django import template

register = template.Library()


class data_Node(template.Node):
    def __init__(self, varname):
        self.varname = varname

    def __repr__(self):
        return "<Data Node>"

    def render(self, context):
        data = []
        # gestiones = Gestion.objects.filter(
        #     fecha__month=datetime.now().month,
        #     fecha__year=datetime.now().year)
        gestiones = Gestion.objects.all()
        tipos = TipoGestion.objects.all()

        def get_total(gestions, tipo):
            gs = gestions.filter(tipo_gestion=tipo)
            if gs.count() > 0:
                return gs.count()
            else:
                return 0

        def por_tipo(gestions):
            data = []
            for t in tipos:
                data.append({'tipo': t.prefijo, 'total': get_total(gestions, t)})
            return data

        for s in ESTADOS_LOG_GESTION:
            p = gestiones.filter(status_gestion=s[0]).order_by('-fecha')
            obj = {}
            obj['status'] = s[0]
            obj['total'] = p.count()
            obj['tipos'] = por_tipo(p)
            data.append(obj)

        context[self.varname] = data
        return ''


@register.tag
def get_data(parser, token):
    """
        uso
            {% get_data as [varname] %}
    """
    tokens = token.contents.split()
    args = len(tokens)

    if not args == 3:
        raise template.TemplateSyntaxError(
            "'get_data' requiere de dos argumentos y se dieron %s"
            % (args))
    if not tokens[1] == 'as':
        raise template.TemplateSyntaxError(
            "'get_data' requiere que el primer argumento sea 'as'")

    return data_Node(varname=tokens[2])


class Totals(template.Node):
    def __init__(self, varname):
        self.varname = varname

    def __repr__(self):
        return "<Data Node>"

    def render(self, context):
        context[self.varname] = Gestion.totalizar_gestiones()
        return ''


@register.tag
def get_totales(parser, token):
    tokens = token.contents.split()
    args = len(tokens)
    if not args == 3:
        raise template.TemplateSyntaxError("'get totales requiere exactamente 3 arumentos y se pasaron %s'" % args)

    if not tokens[1] == 'as':
        raise template.TemplateSyntaxError(
            "'get totales' requiere que el primer argumento sea 'as'")

    return Totals(varname=tokens[2])


class facturacion(template.Node):
    def __init__(self, varname):
        self.varname = varname

    def __repr__(self):
        return "<Data Node>"

    def render(self, context):
        context[self.varname] = Gestion.datos_facturacion()
        return ''


@register.tag
def get_facturacion(parser, token):
    tokens = token.contents.split()
    args = len(tokens)
    if not args == 3:
        raise template.TemplateSyntaxError("'get facturacion requiere exactamente 3 arumentos y se pasaron %s'" % args)

    if not tokens[1] == 'as':
        raise template.TemplateSyntaxError(
            "'get facturacion' requiere que el primer argumento sea 'as'")

    return facturacion(varname=tokens[2])