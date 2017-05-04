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
        types = TipoGestion.objects.all()
        context[self.varname] = types
        return ''


@register.tag
def get_tipos_gestion(parser, token):
    """
        uso
            {% get_tipos_gestion as [varname] %}
    """
    tokens = token.contents.split()
    args = len(tokens)

    if not len(tokens) == 3:
        raise template.TemplateSyntaxError(
            "'get_tipos_gestion' requiere de dos argumentos y se dieron %s"
            % (args))
    if not tokens[1] == 'as':
        raise template.TemplateSyntaxError(
            "'get_tipos_gestion' requiere que el primer argumento sea 'as'")

    return data_Node(varname=tokens[2])
