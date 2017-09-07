# coding=utf-8
from django.views.generic.base import TemplateView
from django.http.response import HttpResponse
import json
from django.views.decorators.csrf import csrf_exempt

from base.html_to_pdf import render_to_pdf
from .models import *
from django.contrib.auth import authenticate
from geoposition import Geoposition
from django.shortcuts import render
from django.core.mail import EmailMessage


class barrios_huerfanos(TemplateView):
    template_name = "dtracking/barrios_huerfanos.html"

    def get_context_data(self, **kwargs):
        context = super(barrios_huerfanos, self).get_context_data(**kwargs)
        context['barrios'] = Barrio.objects.all().exclude(
            id__in=ZonaBarrio.objects.all().values_list('barrio', flat=True))
        return context

class gestion_adjuntos(TemplateView):
    template_name = "dtracking/documentos_adjuntos.html"

    def get(self, request, *args, **kwargs):
        context = super(gestion_adjuntos, self).get_context_data(**kwargs)
        context['archivos'] = Archivo.objects.filter(
            gestion__id=request.GET.get("pk")
        )
        context['pk_gestion'] = request.GET.get("pk")
        return super(gestion_adjuntos, self).render_to_response(context)

    def post(self, request, *args, **kwargs):
        context = super(gestion_adjuntos, self).get_context_data(**kwargs)
        pk_gestion = request.POST.get("pk_gestion", None)
        archivo = request.FILES['archivo']
        if pk_gestion:
            gestion = Gestion.objects.get(pk=pk_gestion)
            a = Archivo.objects.create(gestion=gestion,
                                       variable="Documento Adjunto de Gestion")
            a.archivo = archivo
            a.user = request.user
            a.fecha = datetime.now()
            a.save()
        
        context['archivos'] = Archivo.objects.filter(
            gestion__id=pk_gestion
        )
        context['pk_gestion'] = pk_gestion
        return super(gestion_adjuntos, self).render_to_response(context)



@csrf_exempt
def movil_login(request):
    username = request.POST.get('username', '')
    password = request.POST.get('password', '')
    user = authenticate(username=username, password=password)
    if user:
        o = {'id': user.id, 'username': user.username,
             'name': user.get_full_name()}
        try:
            profile = Gestor.objects.get(user=user)
            o['perfil'] = profile.to_json()
        except:
            o['error'] = "el usuario no tiene perfil o esta inactivo."
        data = json.dumps([o])
    else:
        data = []
    return HttpResponse(data, content_type='application/json')


@csrf_exempt
def tipos_gestion(request):
    tg = TipoGestion.objects.all()
    data = []
    for t in tg:
        data.append(t.to_json())
    data = json.dumps(data)
    return HttpResponse(data, content_type='application/json')


@csrf_exempt
def gestiones_pendientes(request):
    gs = Gestion.objects.filter(user=int(request.POST.get('user', '')),
                                realizada=False)
    data = []
    for g in gs:
        data.append(g.to_json())
    data = json.dumps(data)
    return HttpResponse(data, content_type='application/json')


@csrf_exempt
def cargar_gestion(request):
    data = []
    try:
        g = Gestion.objects.get(id=int(request.POST.get('gestion', '')))
        g.fecha = request.POST.get('fecha', '')
        g.position = Geoposition(request.POST.get('latitude', ''),
                                 request.POST.get('longitude', ''))
        g.json = request.POST.get('json', '')
        g.realizada = True
        g.save()
        g.log(g.user, g.fecha, ESTADOS_LOG_GESTION[2][0])
        obj = g.to_json()
        obj['mensaje'] = "gestion subida con exito"
        data = [obj, ]
        data = json.dumps(data)
    except Exception, e:
        data.append({'error': "esta gestion no existe" + e.message})
    return HttpResponse(data, content_type='application/json')


@csrf_exempt
def cargar_media(request):
    g = Gestion.objects.filter(id=int(request.POST.get('gestion', ''))).first()
    if not g:
        obj= {'mensaje' : "media subida con exito"}
    else:
        variable = request.POST.get('variable', '')
        imagen = request.FILES['imagen']
        g.cargar_archivo(imagen, variable)
        obj = g.to_json()
        obj['mensaje'] = "media subida con exito"
    data = [obj, ]
    data = json.dumps(data)
    return HttpResponse(data, content_type='application/json')


@csrf_exempt
def seguimiento_gps(request):
    data = []
    p = Position(
        user=User.objects.get(id=int(request.POST.get('user', ''))),
        position=Geoposition(request.POST.get('latitude', ''),
                             request.POST.get('longitude', '')),
        fecha=request.POST.get('fecha', None)
    )
    p.save()
    data.append({'mensaje': "posicion registrada con exito"})
    data = json.dumps(data)
    return HttpResponse(data, content_type="application/json")


@csrf_exempt
def mensajeria(request):
    data = []
    smss = SMS.objects.filter(enviado=False)
    for sms in smss:
        data.append(json.loads(sms.texto))
    data = json.dumps(data)
    smss.update(enviado=True, fecha_envio=datetime.now())
    return HttpResponse(data, content_type="application/json")


@csrf_exempt
def view_details(request):
    g = Gestion.objects.get(id=int(request.POST.get('id', '')))
    data = g.to_json()
    data = json.dumps(data)
    return HttpResponse(data, content_type="application/json")


@csrf_exempt
def asignar_gestion(request):
    g = Gestion.objects.get(id=int(request.POST.get('gestion', '')))
    g.user = User.objects.get(id=int(request.POST.get('user', '')))
    g.fecha_asignacion = request.POST.get('fecha', '')

    g.log(request.user, datetime.now(), ESTADOS_LOG_GESTION[1][1])

    render_to_pdf(
        'dtracking/examen_previo.html',
        {
            'pagesize': 'A4',
            'obj': g,
        }
    )
    try:
        email = EmailMessage("Asignación de Avaluo",
                             "<h1/>Se le ha asignado el avaluo: %s - %s<h1>"
                             "Datos del cliente:<br>"
                             "<span>Nombre: %s</span><br>"
                             "<span>Direccion: %s</span><br>"
                             "<span>Telefono: %s</span><br>" % (g.destinatario, g.barra,g.destinatario,g.direccion,g.telefono),
                             to=[g.user.email,
                                 'jwgarcia003@gmail.com'],
                             )

        email.content_subtype = "html"
        email.attach_file("out.pdf")
        email.send()

        g.save()
    except Exception, e:
        print e.message

    return HttpResponse(json.dumps({'mensaje': "Asignacion Exitosa!", 'code': 200}),
                        content_type="application/json")


@csrf_exempt
def edicion_elementos(request):
    data = []
    if request.method == "POST":
        print "post"
    if request.method == "GET":
        id = request.GET.get('combo', None)
        if id:
            elms = DetalleGestion.objects.get(id=id).elementos()
            for e in elms:
                data.append(e.to_json())
    data = json.dumps(data)
    return HttpResponse(data, content_type='application/json')


@csrf_exempt
def guardar_elementos(request):
    jresponse = {}
    elementos = request.POST.getlist('elemento')
    id_tipo = request.POST.get('id_tipo')

    detalle = DetalleGestion.objects.filter(id=id_tipo).first()
    if not detalle:
        jresponse['mensaje'] = "Detalle no encontrado"
        jresponse['code'] = 400
    else:

        Elemento.objects.filter(combo=detalle).delete()
        for elemento in elementos:
            if not elemento == "":
                Elemento.objects.get_or_create(combo=detalle, valor=elemento)

        jresponse['mensaje'] = "Registro exitoso!"
        jresponse['code'] = 200

    data = json.dumps(jresponse)
    return HttpResponse(data, content_type='application/json')


def get_log_gestion(request):
    jresponse = {}
    codigo_gestion = request.GET.get("gestion", None)
    if not codigo_gestion:
        jresponse['mensaje'] = "Gestion no encontrada"
        jresponse['code'] = 400
    else:
        try:
            gestion = Gestion.objects.get(barra=codigo_gestion)
            if not gestion:
                jresponse['mensaje'] = "Gestion no encontrada"
                jresponse['code'] = 400
            else:
                logs = Log_Gestion.objects.filter(gestion=gestion)
                jlogs = []
                for log in logs:
                    jlog = {"fecha": str(log.fecha), "estado": log.estado, "atiende": log.usuario.username,
                            "anexo": log.anexo()}
                    jlogs.append(jlog)

                jresponse['codigo_gestion'] = gestion.barra
                jresponse['cliente_gestion'] = gestion.destinatario
                jresponse['tipo_gestion'] = gestion.tipo_gestion.name
                jresponse['mensaje'] = "OK"
                jresponse['code'] = 200
                jresponse['logs'] = jlogs

        except:
            jresponse['mensaje'] = "Gestion no encontrada"
            jresponse['code'] = 400

    data = json.dumps(jresponse)
    return HttpResponse(data, content_type='application/json')


@csrf_exempt
def examen_previo(request):
    gestion = Gestion.objects.get(id=int(request.GET.get('gestion', '')))
    data = {'obj': gestion}
    # variables = gestion.variables()
    return render(request, "dtracking/examen_previo.html", data)


@csrf_exempt
def get_municipios(request):
    municipios = Municipio.objects.filter(departamento=int(request.POST.get('departamento', None)))
    data = json.dumps([x.to_json() for x in municipios])
    return HttpResponse(data, content_type='application/json')


@csrf_exempt
def get_barrios(request):
    barrios = Barrio.objects.filter(municipio=int(request.POST.get('municipio', None)))
    data = json.dumps([x.to_json() for x in barrios])
    return HttpResponse(data, content_type='application/json')

@csrf_exempt
def get_usos_gestion(request):
    usos = Gestion_Uso.objects.filter(fin=int(request.POST.get('fin', None)))
    data = json.dumps([x.to_json() for x in usos])
    return HttpResponse(data, content_type='application/json')

@csrf_exempt
def agregar_registro(request):
    obj_json = {}
    tag = request.POST.get("tag", None)
    mensaje = request.POST.get("mensaje", None)
    fecha = request.POST.get("fecha", None)
    usuario = request.POST.get("usuario", None)

    if not tag:
        obj_json['code'] = 400
        obj_json['mensaje'] = "TAG no encontrada"
    elif not mensaje:
        obj_json['code'] = 400
        obj_json['mensaje'] = "Mensaje no encontrado"
    elif not fecha:
        obj_json['code'] = 400
        obj_json['mensaje'] = "Fecha no encontrado"
    elif not usuario:
        obj_json['code'] = 400
        obj_json['mensaje'] = "Fecha no encontrado"
    else:
        registro, c = Registro.objects.get_or_create(
            tag=tag,
            mensaje=mensaje,
            fecha=fecha,
            usuario=usuario
        )
        if not registro:
            obj_json['code'] = 500
            obj_json['mensaje'] = "No fue posible crear el registro"
        else:
            obj_json['code'] = 200
            obj_json['mensaje'] = "Registro creado exitosamente"
    data = json.dumps(obj_json)
    return HttpResponse(data, content_type='application/json')

def get_avaluo_mes_posiciones(request):
    anio = request.POST.get("anio", 0)
    mes = request.POST.get("mes", 0)
    gestiones = Gestion.objects.filter(fecha__year=anio, fecha__month=mes).exclude(position__in=[None])
    data = json.dumps([x.to_json() for x in gestiones])
    return HttpResponse(data, content_type='application/json')


