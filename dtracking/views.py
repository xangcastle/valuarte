from django.views.generic.base import TemplateView
from django.http.response import HttpResponse
import json
from django.views.decorators.csrf import csrf_exempt
from .models import *
from django.contrib.auth import authenticate
from geoposition import Geoposition


class barrios_huerfanos(TemplateView):
    template_name = "dtracking/barrios_huerfanos.html"

    def get_context_data(self, **kwargs):
        context = super(barrios_huerfanos, self).get_context_data(**kwargs)
        context['barrios'] = Barrio.objects.all().exclude(
            id__in=ZonaBarrio.objects.all().values_list('barrio', flat=True))
        return context


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
        obj = g.to_json()
        obj['mensaje'] = "gestion subida con exito"
        data = [obj, ]
        data = json.dumps(data)
    except:
        data.append({'error': "esta gestion no existe"})
    return HttpResponse(data, content_type='application/json')


@csrf_exempt
def cargar_media(request):
    g = Gestion.objects.get(id=int(request.POST.get('gestion', '')))
    variable = request.POST.get('variable', '')
    imagen = request.FILES['imagen']
    g.cargar_archivo(imagen, variable)
    data = [g.to_json(), ]
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
    codigo_gestion = request.GET.get("gestion")
    if not  codigo_gestion:
        jresponse['mensaje'] = "Gestion no encontrada"
        jresponse['code'] = 400
    else:
        try:
            gestion = Gestion.objects.get(id=int(codigo_gestion))
            if not gestion:
                jresponse['mensaje'] = "Gestion no encontrada"
                jresponse['code'] = 400
            else:
                logs=Log_Gestion.objects.filter(gestion=gestion)
                jlogs=[]
                for log in logs:
                    jlog={"fecha": str(log.fecha), "estado":log.estado, "atiende":log.usuario.username}
                    jlogs.append(jlog)

                jresponse['codigo_gestion'] = gestion.id
                jresponse['cliente_gestion'] = gestion.destinatario
                jresponse['mensaje'] = "OK"
                jresponse['code'] = 200
                jresponse['logs'] = jlogs

        except:
            jresponse['mensaje'] = "Gestion no encontrada"
            jresponse['code'] = 400

    data = json.dumps(jresponse)
    return HttpResponse(data, content_type='application/json')