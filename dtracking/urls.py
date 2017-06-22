

from django.conf.urls import url
from .views import *


urlpatterns = [
    url(r'^movil/tipos_gestion/$', tipos_gestion,
        name='tipos_gestion'),
    url(r'^movil/gestiones/$', gestiones_pendientes,
        name='gestiones_pendientes'),
    url(r'^movil/login/$', movil_login,
        name='dtracking_login'),
    url(r'^movil/cargar_gestion/$', cargar_gestion,
        name='cargar_gestion'),
    url(r'^movil/cargar_media/$', cargar_media,
        name='cargar_media'),
    url(r'^barrios_huerfanos/', barrios_huerfanos.as_view(),
        name='barrios_huerfanos'),
    url(r'^movil/seguimiento_gps/', seguimiento_gps,
        name='seguimiento_gps'),
    url(r'^movil/mensajeria/', mensajeria,
        name='mensajeria_movil'),
    url(r'^view_details/', view_details,
        name='view_details'),
    url(r'^edicion_elementos/', edicion_elementos,
        name='edicion_elementos'),
    url(r'^guardar_elementos/', guardar_elementos,
        name='guardar_elementos'),
    url(r'^get_log_gestion/', get_log_gestion,
        name='get_log_gestion'),
    url(r'^asignar_gestion/', asignar_gestion,
        name='asignar_gestion'),
    url(r'^examen_previo/', examen_previo,
        name='examen_previo'),
    url(r'^get_municipios/', get_municipios,
        name='get_municipios'),
    url(r'^get_barrios/', get_barrios,
        name='get_barrios'),
    url(r'^get_usos_gestion/', get_usos_gestion,
        name='get_usos_gestion')

]
