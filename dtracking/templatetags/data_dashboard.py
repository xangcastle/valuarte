# -*- coding: utf-8 -*-
from ..models import *
from datetime import datetime
from django import template

register = template.Library()

class data_Node(template.Node):
    def __init__(self, varname):
        self.varname = varname

    def __repr__(self):
        return "<Data Node>"

    def render(self, context):
        data = []
        gestiones = Gestion.objects.filter(
            fecha__month=datetime.now().month,
            fecha__year=datetime.now().year)

        def por_tipo(gestions):
            tipos = TipoGestion.objects.all()
            data = []
            for t in tipos:
                data.append({'tipo': t.prefijo, 'total': gestions.filter(tipo_gestion=t).count()})
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

    if not len(tokens) == 3:
        raise template.TemplateSyntaxError(
            "'get_data' requiere de dos argumentos y se dieron %s"
            % (args))
    if not tokens[1] == 'as':
        raise template.TemplateSyntaxError(
            "'get_data' requiere que el primer argumento sea 'as'")

    return data_Node(varname=tokens[2])
