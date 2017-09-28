from django.conf.urls import url
from .ajax import *

urlpatterns = [
    url(r'^get_object/', get_object, name="ajax_getObject"),
    url(r'^get_collection/', get_collection, name="ajax_getCollection"),
    url(r'^autocomplete/', autocomplete, name="ajax_autocomplete"),
    url(r'^object_execute/', object_execute, name="ajax_objectExecute"),
    url(r'^get_html_form/', get_html_form, name="ajax_getHtmlForm")
]
