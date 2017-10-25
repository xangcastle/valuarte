# coding=utf-8
from __future__ import unicode_literals

import sys
from django.core.mail import EmailMessage
from django.utils.html import mark_safe
from base.models import Entidad
from django.contrib.auth.models import User
from django.db import models
from geoposition.fields import GeopositionField
from jsonfield import JSONField
import datetime as datetime_base
from datetime import datetime, timedelta
import json
from django.utils.encoding import smart_str
from colorfield.fields import ColorField


def add_business_days(origin_date, add_days):
    '''
    Función que añade días hábiles a una fecha.
    '''
    while add_days > 0:
        origin_date += timedelta(days=1)
        weekday = origin_date.weekday()  # regresa un entero de 0 - 6
        if weekday >= 4:  # sunday = 6
            continue
        add_days -= 1
    return origin_date


def diff_business_days(origin_date, end_date):
    days = 0
    while not origin_date > end_date:
        weekday = origin_date.weekday()  # regresa un entero de 0 - 6
        origin_date += timedelta(days=1)  # pasar al siguiente dia
        if weekday >= 4:
            continue
        days += 1
    return days

def ifnull(var, val):
    if var is None:
        return val
    return var


def get_gestor(user):
    try:
        return Gestor.objects.get(user=user)
    except:
        return None


CONECTIONS = (
    ('SMS + WIFI', 'SMS + WIFI'),
    ('3G + WIFI', '3G + WIFI'),
    ('WIFI', 'WIFI'),
)

ESTADOS_LOG_GESTION = (('RECEPCIONADO', 'RECEPCIONADO'),  # 0 0
                       ('ASIGNADO A EVALUADOR', 'ASIGNADO A EVALUADOR'),  # 1 0
                       ('LEVANTAMIENTO REALIZADO', 'LEVANTAMIENTO REALIZADO'),  # 2 0
                       ('EN REVISION FINAL DE INFORME', 'EN REVISION FINAL DE INFORME'),  # 3 0
                       ('TERMINADO', 'TERMINADO'))  # 4 0


class Gestor(models.Model):
    user = models.OneToOneField(User)
    numero = models.CharField(max_length=8, help_text="numero de celular")
    server_conection = models.CharField(max_length=25, choices=CONECTIONS,
                                        default='WIFI', null=True, blank=True)
    sms_gateway = models.CharField(max_length=20, null=True)
    foto = models.ImageField(null=True)
    zonas = models.ManyToManyField('Zona',null=True, blank=True)
    tipo_gestion = models.ManyToManyField('TipoGestion', blank=True)
    intervalo = models.PositiveIntegerField(null=True, verbose_name="intervalo de seguimiento",
                                            help_text="esto determina que tan seguido el gestor reportara su posicion gps en segundos")

    def image_thumb(self):
        return '<img src="/media/%s" width="100" height="60" />' % (self.foto)

    image_thumb.allow_tags = True
    image_thumb.short_description = "Imagen"

    def __unicode__(self):
        return str(self.user)

    def to_json(self):
        o = {}
        o['numero'] = self.numero
        o['foto'] = self.foto.url
        o['server_conection'] = self.server_conection
        if self.server_conection == 'SMS + WIFI':
            o['sms_gateway'] = self.sms_gateway
        o['zonas'] = []
        o['tipos_gestion'] = []
        for z in self.zonas.all():
            o['zonas'].append(z.name)
        for t in self.tipo_gestion.all():
            o['tipos_gestion'].append(t.name)
        o['intervalo'] = self.intervalo
        return o

    def full_name(self):
        return "%s %s" % (ifnull(self.user.first_name, self.user.username), ifnull(self.user.last_name, ""))

    class Meta:
        verbose_name = "perito"
        verbose_name_plural = "Peritos"


class Armador(models.Model):
    user = models.OneToOneField(User)
    especialidades = models.ManyToManyField('TipoGestion', blank=True)
    activo = models.BooleanField(default=True)

    def nombres(self):
        return self.user.first_name

    def apellidos(self):
        return self.user.last_name

    def __unicode__(self):
        return self.user.username

    class Meta:
        verbose_name_plural = "armadores"


class Departamento(Entidad):
    pass


class Municipio(Entidad):
    departamento = models.ForeignKey(Departamento)


class Barrio(Entidad):
    municipio = models.ForeignKey(Municipio)

    def referencias(self):
        return Gestion.objects.filter(barrio=self).values_list('direccion', flat=True)[:5]


class Zona(Entidad):
    departamento = models.ForeignKey(Departamento)


class ZonaBarrio(models.Model):
    zona = models.ForeignKey(Zona)
    barrio = models.ForeignKey(Barrio)
    orden = models.IntegerField(null=True, blank=True)


class TipoGestion(Entidad):
    prefijo = models.CharField(max_length=6, null=True, blank=False)
    tiempo_ejecucion = models.IntegerField(null=True, blank=True, verbose_name="tiempo en minutos para el peritaje",
                                           help_text="Tiempo requerido en minutos para el levantamiento de datos de este tipo de avaluo")
    color = ColorField(default="ffffff")
    dias = models.IntegerField(default=4, null=True, verbose_name="dias necesarios para el armado")

    def __unicode__(self):
        return "%s (%s)" % (self.prefijo, self.name)
    def detalles(self):
        return DetalleGestion.objects.filter(tipo_gestion=self)

    def to_json(self):
        obj = {'id': self.id, 'name': self.name}
        obj['campos'] = []
        for d in self.detalles().order_by('orden'):
            obj['campos'].append(d.to_json())
        return obj

    def errores(self):
        errors = ''
        for d in self.detalles():
            if d.error():
                errors += 'El campo %s es de tipo %s, pero no contiene ningun elemento para seleccionar. ' % (
                    d.titulo, d.tipo)
        return errors

    def muestra_color(self):
        return mark_safe('<div style="height: 25px; width: 25px; background-color:%s">' % self.color)
    muestra_color.short_description = "color"

    class Meta:
        verbose_name = "tipo de avaluo"
        verbose_name_plural = "tipos de avaluos"
        ordering = ['prefijo',]


TIPOS = (
    ('input', 'input'),
    ('radio', 'radio'),
    ('textarea', 'textarea'),
    ('combobox', 'combobox'),
    ('checkbox', 'checkbox'),
    ('foto', 'foto'),
    ('multi foto', 'multi foto'),
    ('firma', 'firma'),
)


class DetalleGestion(models.Model):
    tipo_gestion = models.ForeignKey(TipoGestion)
    tipo = models.CharField(max_length=25, choices=TIPOS, verbose_name="tipo de campo")
    requerido = models.BooleanField(default=True)
    titulo = models.CharField(max_length=65, verbose_name="titulo a mostrar")
    nombreVariable = models.CharField(max_length=65, verbose_name="nombre de la variable")
    habilitado = models.BooleanField(default=True)
    orden = models.IntegerField(null=True, blank=True)
    imprime = models.BooleanField(default=False, verbose_name="se imprime")

    def elementos(self):
        return Elemento.objects.filter(combo=self.id)

    def __unicode__(self):
        return "%s - %s" % (self.tipo_gestion.name, self.nombreVariable)

    def to_json(self):
        o = {}
        o['tipo'] = self.tipo
        o['requerido'] = self.requerido
        o['titulo'] = self.titulo
        o['nombreVariable'] = self.nombreVariable
        o['habilitado'] = self.habilitado
        o['imprime'] = self.imprime
        if self.elementos():
            o['elementos'] = []
        for e in self.elementos():
            o['elementos'].append({'id': e.id, 'valor': e.valor})
        return o

    class Meta:
        verbose_name = "campo"
        verbose_name_plural = "campos requeridos por la gestion"
        ordering = ['orden', ]

    def error(self):
        if (self.tipo == 'combobox' or self.tipo == 'radio') and self.elementos().count() == 0:
            return True
        else:
            return False


class especiales(models.Manager):
    def get_queryset(self):
        return super(especiales, self).get_queryset().filter(tipo__in=['combobox', 'radio'])


class EspecialField(DetalleGestion):
    objects = models.Manager()
    objects = especiales()

    class Meta:
        proxy = True


class Elemento(models.Model):
    combo = models.ForeignKey(EspecialField)
    valor = models.CharField(max_length=65)

    def to_json(self):
        return {'combo': self.combo.id, 'valor': self.valor}


BANCOS = (
    ('BANPRO', 'BANPRO'),
    ('BANCENTRO', 'BANCENTRO'),
    ('BAC', 'BAC'),
    ('BDF', 'BDF'),
    ('FICOHSA', 'FICOHSA'),
    ('PROCREDIT', 'PROCREDIT'),
)


class Gestion_Fin(Entidad):
    pass

    class Meta:
        verbose_name_plural = "Fines de Avaluo"
        verbose_name = "Finalidad de avaluo"


class Gestion_Uso(Entidad):
    fin = models.ForeignKey(Gestion_Fin)

    class Meta:
        verbose_name_plural = "Usos de Avaluo"
        verbose_name = "Uso de avaluo"


class Gestion(models.Model):
    fecha = models.DateField(null=True, blank=True, verbose_name="fecha de solicitud")  # fecha en que se recepciona la solicitud del avaluo
    barra = models.CharField(max_length=65, null=True, verbose_name="Código de avaluo")  # el codigo del avaluo
    tipo_gestion = models.ForeignKey(TipoGestion)
    fin_gestion = models.ForeignKey(Gestion_Fin, null=True, blank=True)
    uso_gestion = models.ForeignKey(Gestion_Uso, null=True, blank=True)
    observaciones = models.TextField(max_length=600, null=True, blank=True)
    observaciones_cotizacion = models.TextField(max_length=255, null=True, blank=True, verbose_name="observaciones en la cotización")
    referencia = models.CharField(max_length=35, null=True, blank=True, verbose_name="Referencia bancaria")
    valor = models.FloatField(null=True, blank=True, verbose_name="precio del avaluo ya con iva")
    categoria = models.CharField(max_length=50, null=True, blank=True)
    informe_final = models.FileField(upload_to="fichas", null=True, blank=True)  # informe final
    status_gestion = models.CharField(max_length=60, null=True, choices=ESTADOS_LOG_GESTION,
                                      default=ESTADOS_LOG_GESTION[0][0], blank=True)

    # datos del cliente
    destinatario = models.CharField(max_length=125, null=True, verbose_name="Cliente")
    identificacion = models.CharField(max_length=25, null=True, verbose_name="Itentificación", blank=True)
    contacto = models.CharField(max_length=125, null=True, blank=True, verbose_name="Contacto")
    contacto_telefono = models.CharField(max_length=125, null=True, blank=True, verbose_name="Teléfono del contacto")
    telefono = models.CharField(max_length=65, null=True, blank=True)
    departamento = models.ForeignKey(Departamento, null=True, blank=True)
    municipio = models.ForeignKey(Municipio, null=True, blank=True)
    barrio = models.ForeignKey(Barrio, null=True, blank=True)
    zona = models.ForeignKey(Zona, null=True, blank=True)
    direccion = models.TextField(max_length=255, null=True, verbose_name="Ubicacion del bien a valuar")
    direccion_envio = models.CharField(max_length=255, null=True, blank=True, verbose_name="Dirección de envío")

    # contacto del banco
    banco = models.CharField(max_length=25, choices=BANCOS, verbose_name="Banco", null=True, blank=True,
                             help_text="temporal")
    banco_ejecutivo = models.CharField(max_length=100, null=True, blank=True, verbose_name="Ejecutivo bancario",
                             help_text="temporal")
    new_banco = models.ForeignKey('Banco', null=True, blank=True)
    new_ejecutivo = models.ForeignKey('Ejecutivo', null=True, blank=True)

    # peritaje
    notify = models.BooleanField(default=False, verbose_name="notificar")  # indica si se le notificara via email al perito asignado
    user = models.ForeignKey('Perito', null=True, blank=True, verbose_name="perito")  # perito de campo al que se le asigna el avaluo
    fecha_asignacion = models.DateTimeField(null=True, blank=True)  # fecha de programacion incluye hora
    realizada = models.BooleanField(default=False)  # indica si ya se realizo inspecion fisica
    ficha_inspeccion = models.FileField(upload_to="fichas", null=True, blank=True)  # ficha del levantamiento fisico
    position = GeopositionField(null=True, blank=True, default='12.129239891689053,-86.26631538391109')
    json = JSONField(null=True, blank=True)

    # operaciones
    fecha_recepcion = models.DateField(null=True, blank=True)
    fecha_vence = models.DateField(null=True, blank=True)
    armador = models.ForeignKey('Operaciones', null=True, blank=True, related_name="gestion_armador")  # armador de campo al que se le asigna el avaluo
    revizada = models.BooleanField(default=False)  # indica si ya se realizo inspecion fisica
    fecha_entrega_efectiva = models.DateField(null=True, blank=True)
    dias = models.IntegerField(default=0, null=True, verbose_name="dias extras para el armado")

    def logs(self):
        return Log_Gestion.objects.filter(gestion=self)

    def notificar(self, *args, **kwargs):
        print("asignar_gestion: Llamando Metodo para generar PDF")
        if self.user.email:

            email = EmailMessage("Asignación de Avaluo %s" % self.barra,
                                 "<h3/>Se le ha asignado el avaluo: %s - %s<h3>"
                                 "Datos del cliente:<br>"
                                 "<span>Nombre: %s</span><br>"
                                 "<span>Direccion: %s</span><br>"
                                 "<a href='www.valuarte.com.ni/dtracking/generar_asignacion/?documento=%s'> Imprimir aqui!</a><br>" % (
                                     self.destinatario, self.barra, self.destinatario,
                                     self.direccion, self.id),
                                 to=[self.user.email],
                                 )

            email.content_subtype = "html"
            # print("asignar_gestion: Agregando attachmet al correo")
            # email.attach_file("out.pdf")
            print("asignar_gestion: Iniciando envio de correo electronico")
            email.send()
            print("asignar_gestion: Correo electronico enviado")

        if kwargs.has_key('request'):
            request = kwargs.pop('request')
            self.log(request.user, datetime.now(), ESTADOS_LOG_GESTION[1][1])

    def get_categoria(self):
        try:
            if self.valor <= 100:
                return "Cat. 1"
            elif 100 < self.valor <= 200:
                return "Cat. 2"
            elif 201 < self.valor <= 500:
                return "Cat. 3"
            elif 501 < self.valor <= 1000:
                return "Cat. 4"
            elif self.valor > 1000:
                return "Cat. 5"
        except:
            return None

    def get_fecha_vence(self):
        if self.fecha_recepcion:
            return add_business_days(self.fecha_recepcion, self.tipo_gestion.dias + self.dias)
        else:
            return None

    def get_user_log(self, status):
        if status == ESTADOS_LOG_GESTION[2][0]:
            return self.user
        elif status == ESTADOS_LOG_GESTION[3][0]:
            return self.armador
        else:
            return None

    def log_status_gestion(self, status):
        l, created = Log_Gestion.objects.get_or_create(gestion=self, estado=status)
        l.fecha = datetime.now()
        l.user = self.get_user_log(status)
        l.save()

    def get_status_gestion(self):
        actual = ESTADOS_LOG_GESTION[0][0]
        if not self.user and not self.fecha_asignacion:
            actual = ESTADOS_LOG_GESTION[0][0]
        if self.user and self.fecha_asignacion:
            actual = ESTADOS_LOG_GESTION[1][0]
        if self.user and self.fecha_asignacion and (self.realizada or self.ficha_inspeccion) and self.fecha_recepcion:
            actual = ESTADOS_LOG_GESTION[2][0]
        if self.user and self.fecha_asignacion and (self.realizada or self.ficha_inspeccion) and self.fecha_recepcion \
                and self.armador and self.revizada:
            actual = ESTADOS_LOG_GESTION[3][0]
        if self.user and self.fecha_asignacion and self.fecha_recepcion and (self.realizada or self.ficha_inspeccion) \
                and self.armador and self.revizada and self.informe_final:
            actual = ESTADOS_LOG_GESTION[4][0]

        return actual

    def log(self, usuario, fecha, estado):
        return Log_Gestion(gestion=self, usuario=usuario, fecha=fecha, estado=estado).save()

    def save(self, *args, **kwargs):
        if not self.fecha:
            self.fecha = datetime.now()
        if not self.barra:
            self.barra = self.get_code()
        self.categoria = self.get_categoria()
        self.status_gestion = self.get_status_gestion()
        self.fecha_vence = self.get_fecha_vence()
        super(Gestion, self).save()
        self.log_status_gestion(self.status_gestion)

    def dias_retrazo(self):
        dias = 0
        if self.fecha_recepcion and self.fecha_vence:
            fv = datetime.combine(self.get_fecha_vence(), datetime_base.time(23, 59))
            if datetime.now() > fv:
                dias = diff_business_days(fv, datetime.now())
        return dias

    dias_retrazo.short_description = "dias de retrazo"


    def contacto_envio(self):
        if self.banco and self.banco_ejecutivo:
            return "%s / %s" % (self.banco, self.banco_ejecutivo)
        elif self.contacto and (self.contacto <> self.destinatario):
            return self.contacto
        else:
            return ""

    def iva(self):
        if self.valor:
            return round((self.valor / 1.15) * 0.15, 2)
        else:
            return 0.0

    def subtotal(self):
        if self.valor:
            return round(self.valor / 1.15, 2)
        else:
            return 0.0

    def descripcion(self):
        if self.tipo_gestion and self.observaciones:
            return "%s. %s" % (self.tipo_gestion.name, self.observaciones)
        elif self.tipo_gestion and not self.observaciones:
            return self.tipo_gestion.name
        else:
            return ""

    def get_code(self):
        code = ""
        if self.fecha and self.tipo_gestion:
            numero = ""
            try:
                numero = int(type(self).objects.all().order_by('-barra')[0].barra[0:4]) + 1
            except:
                numero = 1
            code = "%s-%s-%s" % (str(numero).zfill(4), self.tipo_gestion.prefijo, str(self.fecha.year))
        return code

    def __unicode__(self):
        return "%s - %s" % (self.barra, self.destinatario)

    def cargar_archivo(self, archivo, variable):
        a, created = Archivo.objects.get_or_create(gestion=self,
                                                   variable=variable)
        a.archivo = archivo
        a.save()
        return a

    def media(self):
        return Archivo.objects.filter(gestion=self)

    def get_departamento(self):
        if self.departamento:
            return self.departamento.name
        else:
            return ""

    def get_municipio(self):
        if self.municipio:
            return self.municipio.name
        else:
            return ""

    def render_calendar_fin(self):
        if self.status_gestion == ESTADOS_LOG_GESTION[1][0]:
            return self.fecha_asignacion + timedelta(minutes=self.tipo_gestion.tiempo_ejecucion)
        elif self.status_gestion == ESTADOS_LOG_GESTION[2][0]:
            return self.get_fecha_vence()
        else:
            return None

    def render_calendar_inicio(self):
        if self.status_gestion == ESTADOS_LOG_GESTION[1][0]:
            return self.fecha_asignacion
        elif self.status_gestion == ESTADOS_LOG_GESTION[2][0]:
            return self.get_fecha_vence()
        else:
            return None

    def render_user(self):
        if self.armador:
            return self.armador.username
        elif not self.armador and self.user:
            return self.user.username
        else:
            return None

    def to_json(self):
        o = {}
        o['id'] = self.id
        o['status'] = self.status_gestion
        o['destinatario'] = self.destinatario
        o['direccion'] = self.direccion
        o['telefono'] = self.telefono
        o['departamento'] = self.get_departamento()
        o['municipio'] = self.get_municipio()
        o['id_tipo_gestion'] = self.tipo_gestion.id
        o['tipo_gestion'] = self.tipo_gestion.name
        o['barra'] = self.barra
        o['titulo'] = self.destinatario
        o['descripcion'] = self.direccion
        o['inicio'] = str(ifnull(self.render_calendar_inicio(), ''))
        o['fin'] = str(ifnull(self.render_calendar_fin(), ''))
        o['color'] = self.tipo_gestion.color
        o['user'] = ifnull(self.render_user(), '')
        o['dias'] = "%s dias de retrazo" % self.dias_retrazo()

        # if self.position and self.position.latitude:
        #     o['latitude'] = str(self.position.latitude)
        #     o['longitude'] = str(self.position.longitude)
        if self.media():
            o['media'] = []
            for a in self.media():
                o['media'].append(a.to_json())
        if self.status_gestion:
            o['estado'] = str(self.status_gestion)
        if self.json:
            try:
                o['data'] = json.loads(str(smart_str(self.json)).replace("'", "\""))
            except:
                pass

        return o

    def get_fecha_asignacion(self):
        if not self.fecha_asignacion:
            return datetime.now()
        else:
            return self.fecha_asignacion

    def numero_gestor(self):
        return Gestor.objects.get(user=self.user).numero

    def _realizada(self):
        if self.realizada:
            return '<a class="ver-examen" data-des="/dtracking/examen_previo/?gestion=%s" class="detalle">Ver&nbsp;<img src="/static/admin/img/icon-yes.svg" alt="True"></a>' \
                   % self.id
        else:
            return '<img src="/static/admin/img/icon-no.svg" alt="False">'

    _realizada.allow_tags = True
    _realizada.short_description = "Realizada"

    def variables(self):
        reload(sys)
        sys.setdefaultencoding('utf-8')
        variables = []
        o = json.loads(str(smart_str(self.json)).replace("'", "\""))
        campos = o['campos']
        for a, k in campos.items():
            try:
                v = DetalleGestion.objects.get(tipo_gestion=self.tipo_gestion, nombreVariable=a)
                obj = v.to_json()

                if v.tipo == "combobox" or v.tipo == "radio":
                    elementos = v.elementos()
                    if elementos:
                        obj_elementos = []
                        for elemento in v.elementos():
                            selecionado = False
                            if elemento.id == int(k):
                                obj['value'] = elemento.valor
                                selecionado = True
                            obj_elementos.append({'value': elemento.valor, 'selecionado': selecionado})

                        obj['elementos'] = obj_elementos
                    else:
                        obj['value'] = k
                else:
                    obj['value'] = k

                variables.append(obj)
            except Exception as e:
                print "Oops!  That was no valid number.  Try again... %s" % e.message
        return variables

    def variables_plantilla(self):
        reload(sys)
        sys.setdefaultencoding('utf-8')
        arr_variables = []
        try:
            variables = DetalleGestion.objects.filter(tipo_gestion=self.tipo_gestion)
            for v in variables:

                obj = v.to_json()
                if v.tipo == "combobox" or v.tipo == "radio":
                    elementos = v.elementos()
                    if elementos:
                        obj_elementos = []
                        for elemento in v.elementos():
                            selecionado = False
                            obj_elementos.append({'value': elemento.valor, 'selecionado': selecionado})

                        obj['elementos'] = obj_elementos
                    else:
                        obj['value'] = ""
                else:
                    obj['value'] = ""

                arr_variables.append(obj)
        except Exception as e:
            print "Oops!  That was no valid number.  Try again... %s" % e.message
        return arr_variables

    class Meta:
        verbose_name_plural = "Avaluos"
        verbose_name = "Avaluo"


class Archivo(models.Model):
    gestion = models.ForeignKey(Gestion)
    variable = models.CharField(max_length=80)
    archivo = models.FileField(null=True)
    user = models.ForeignKey(User, null=True, blank=True)
    fecha = models.DateTimeField(null=True, blank=True)

    def __unicode__(self):
        return "%s %s" % (self.gestion, self.archivo)

    def to_json(self):
        return {'variable': self.variable,
                'archivo': self.archivo.url}

    class Meta:
        verbose_name_plural = "Archivos Media"


class Position(models.Model):
    user = models.ForeignKey(User)
    position = GeopositionField()
    fecha = models.DateTimeField()

    def to_json(self):
        return {
            'label': self.user.username[0].upper(),
            'usuario': self.user.username,
            'latitude': self.position.latitude,
            'longitude': self.position.longitude,
            'fecha': str(self.fecha),
        }

    class Meta:
        verbose_name = 'posicion'
        verbose_name_plural = "seguimiento gps"


class Import(models.Model):
    destinatario = models.CharField(max_length=150, null=True, blank=True)
    direccion = models.TextField(max_length=250, null=True, blank=True)
    telefono = models.CharField(max_length=65, null=True, blank=True)
    barrio = models.CharField(max_length=150, null=True, blank=True)
    municipio = models.CharField(max_length=150, null=True, blank=True)
    departamento = models.CharField(max_length=150, null=True, blank=True)
    idbarrio = models.ForeignKey('Barrio', null=True, blank=True,
                                 db_column='idbarrio', verbose_name='barrio')
    iddepartamento = models.ForeignKey('Departamento', null=True, blank=True,
                                       db_column='iddepartamento', verbose_name='departamento')
    idmunicipio = models.ForeignKey('Municipio', null=True, blank=True,
                                    db_column='idmunicipio', verbose_name='municipio')

    def __unicode__(self):
        return "%s - %s" % (self.destinatario, self.direccion)

    def get_departamento(self):
        d = None
        if self.departamento:
            try:
                d = Departamento.objects.get(name_alt=self.departamento)
            except:
                d, created = Departamento.objects.get_or_create(
                    name=self.departamento)
        return d

    def get_municipio(self):
        m = None
        try:
            if self.municipio and self.iddepartamento:
                m = Municipio.objects.get(departamento=self.iddepartamento,
                                          name_alt=self.municipio)
        except:
            m, created = Municipio.objects.get_or_create(
                departamento=self.iddepartamento, name=self.municipio)
        return m

    def get_barrio(self):
        b = None
        try:
            if self.barrio and self.idmunicipio and self.iddepartamento:
                b, created = Barrio.objects.get_or_create(
                    municipio=self.idmunicipio, name=self.barrio)
        except:
            b = Barrio.objects.filter(municipio=self.idmunicipio,
                                      name=self.barrio)[0]
        return b

    def integrar_registro(self, fecha_asignacion, fecha_vence, tipo_gestion, eliminar=False):
        g = Gestion()
        g.destinatario = self.destinatario
        g.direccion = self.direccion
        g.telefono = self.telefono
        g.barrio = self.idbarrio
        g.municipio = self.idmunicipio
        g.departamento = self.iddepartamento
        g.zona = get_zona(self.idbarrio)
        g.user = get_user(g.zona)
        g.fecha_asignacion = fecha_asignacion
        g.fecha_vence = fecha_vence
        g.tipo_gestion = tipo_gestion
        g.save()
        if eliminar:
            self.delete()


def get_zona(barrio):
    try:
        return Zona.objects.get(
            id=zona_barrio.objects.filter(barrio=barrio)[0].zona.id)
    except:
        return None


def get_user(zona):
    try:
        user = None
        for g in Gestor.objects.all():
            if zona in g.zonas.all():
                user = g.user
        return user
    except:
        return None


def autoasignacion(gestiones):
    for g in gestiones:
        if not g.zona:
            g.zona = get_zona(g.barrio)
        g.user = get_user(g.zona)
        g.fecha_asignacion = datetime.now()
        g.save()


def integrar(ps):
    message = ""
    ds = ps.order_by('departamento').distinct('departamento')
    for d in ds:
        qs = ps.filter(departamento=d.departamento)
        qs.update(iddepartamento=d.get_departamento().id)
    ms = ps.order_by('departamento', 'municipio').distinct(
        'departamento', 'municipio')
    for m in ms:
        qs = ps.filter(departamento=m.departamento,
                       municipio=m.municipio)
        qs.update(idmunicipio=m.get_municipio().id)
    bs = ps.order_by('departamento', 'municipio', 'barrio').distinct(
        'departamento', 'municipio', 'barrio')
    for b in bs:
        qs = ps.filter(departamento=b.departamento,
                       municipio=b.municipio, barrio=b.barrio)
        qs.update(idbarrio=b.get_barrio().id)
    message += "integrado, total de gestiones = %s end %s departamentos" \
               % (str(ps.count()), str(ds.count()))
    return message


class SMS(models.Model):
    user = models.ForeignKey(User, null=True)
    texto = models.CharField(max_length=540)
    enviado = models.BooleanField(default=False)
    fecha_envio = models.DateTimeField(null=True)

    def __unicode__(self):
        return "%s" % (self.texto)

    def to_json(self):
        return {'texto': self.texto}


def send_sms(texto):
    m = SMS(texto=texto)
    m.save()
    return m


def cancelar_gestiones(gestiones, motivo=""):
    usuarios = gestiones.filter(user__isnull=False).order_by('user').distinct('user')
    for u in usuarios:
        gs = gestiones.filter(user=u.user)
        ids = gs.values_list('id', flat=True)
        ids = '[' + ','.join([str(x) for x in ids]) + ']'
        texto = 'MEN{"g":%s,"c":"%s","m":"%s"}MEN' % (ids, u.user.id,
                                                      ("%s gestiones eliminadas" % gs.count()))
        send_sms(texto, gs[0].numero_gestor())
    gestiones.update(realizada=True, observaciones=motivo)


class Log_Gestion(models.Model):
    gestion = models.ForeignKey(Gestion)
    usuario = models.ForeignKey(User, null=True)
    fecha = models.DateTimeField(null=True)
    estado = models.CharField(max_length=50, choices=ESTADOS_LOG_GESTION, null=True)

    def anexo(self):
        if self.estado == ESTADOS_LOG_GESTION[0][0]:
            return "Inicio del Proceso."
        if self.estado == ESTADOS_LOG_GESTION[1][0]:
            return "Asignado a %s. Visita Programada para el %s a las %s horas." % (
                get_gestor(self.gestion.user).full_name(),
                "{}-{}-{}".format(str(self.gestion.fecha_asignacion.day).zfill(2),
                                  str(self.gestion.fecha_asignacion.month).zfill(2),
                                  self.gestion.fecha_asignacion.year),
                "{:d}:{:02d}".format(
                    self.gestion.fecha_asignacion.hour,
                    self.gestion.fecha_asignacion.minute))
        if self.estado == ESTADOS_LOG_GESTION[2][0]:
            txt = "Inspeccion fisica realizada."
        if self.estado == ESTADOS_LOG_GESTION[3][0]:
            txt = "Inicio del Proceso."
        if self.estado == ESTADOS_LOG_GESTION[4][0]:
            txt = "Inicio del Proceso."
        return txt


class Registro(models.Model):
    tag = models.CharField(max_length=100, null=False, blank=False)
    mensaje = models.TextField(null=False, blank=False)
    fecha = models.DateTimeField(null=False, blank=False)
    usuario = models.CharField(max_length=100, null=True, blank=True)

    def __unicode__(self):
        return "%s %s" % (self.tag, self.usuario)


class PeritoManager(models.Manager):
    def get_queryset(self):
        return super(PeritoManager, self).get_queryset().filter(id__in=Gestor.objects.all().values_list('user', flat=True))


class Perito(User):
    objects = models.Manager()
    objects = PeritoManager()

    class Meta:
        proxy = True


class ArmadorManager(models.Manager):
    def get_queryset(self):
        return super(ArmadorManager, self).get_queryset().filter(id__in=Armador.objects.all().values_list('user', flat=True))


class Operaciones(User):
    objects = models.Manager()
    objects = ArmadorManager()

    class Meta:
        proxy = True


class Banco(Entidad):
    def __unicode__(self):
        return self.name
    class Meta:
        verbose_name_plural = "bancos nacionales"


class Ejecutivo(models.Model):
    banco = models.ForeignKey(Banco)
    nombre = models.CharField(max_length=250)
    telefono = models.CharField(max_length=65, null=True, blank=True)
    email = models.EmailField(max_length=265, null=True, blank=True)

    def __unicode__(self):
        return self.nombre

    class Meta:
        verbose_name_plural = "ejecutivos bancarios"

    def to_json(self):
        return {'nombre': self.nombre,
                'telefono': self.telefono,
                'email': self.email,
                'banco': self.banco.to_json()}
