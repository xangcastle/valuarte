# -*- coding: utf-8 -*-
from django import forms


class DocumentoForm(forms.ModelForm):
    nombre = forms.CharField(label='Nombre del Cliente', max_length=255,
                                required=True,
                             widget=forms.TextInput(attrs={'autocomplete': 'off',
                                                           'class': 'vTextField'}))