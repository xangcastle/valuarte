# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models
from dtracking.models import Gestion
from base.models import base as Base
from django.utils import timezone
from datetime import timedelta
from django.db.models import Sum
from django.utils.safestring import mark_safe
from django.contrib.contenttypes.models import ContentType


class prefacturaManager(models.Manager):
    def get_queryset(self):
        return super(prefacturaManager, self).get_queryset().filter(factura=True, fiscal=False)


class Prefactura(Gestion):

    objects = models.Manager()
    objects = prefacturaManager()

    class Meta:
        proxy = True


MESES = ['ENERO',
        'FEBRERO',
        'MARZO',
        'ABRIL',
        'MAYO',
        'JUNIO',
        'JULIO',
        'AGOSTO',
        'SEPTIEMBRE',
        'OCTUBRE',
        'NOVIEMBRE',
        'DICIEMBRE',
        ]

BANCOS = (('EFECTIVO', 'EFECTIVO'), ('BANPRO', 'BANPRO'), ('BDF', 'BDF'), ('LAFISE', 'LAFISE'), ('FICOHSA', 'FICOHSA'), ('BAC', 'BAC'))

MONEDAS = (('CORDOBAS', 'CORDOBAS'), ('DOLARES', 'DOLARES'))


class TC(models.Model):
    fecha = models.DateField()
    oficial = models.FloatField()
    venta = models.FloatField(null=True)
    compra = models.FloatField(null=True)

    def __unicode__(self):
        return str(self.fecha)


def dolarizar(cordobas=1, fecha=timezone.now(), digitos=2):
    tc = TC.objects.get(fecha__year=fecha.year, fecha__month=fecha.month,
        fecha__day=fecha.day)
    if tc.venta and tc.venta > tc.oficial:
        tc = tc.venta
    else:
        tc = tc.oficial
    return round(cordobas / tc, digitos)


def cordobizar(dolares=1, fecha=timezone.now(), digitos=2):
    tc = TC.objects.get(fecha__year=fecha.year, fecha__month=fecha.month,
        fecha__day=fecha.day)
    if tc.compra and tc.compra < tc.oficial:
        tc = tc.compra
    else:
        tc = tc.oficial
    return round(dolares * tc, digitos)


class Cliente(Base):
    nombre = models.CharField(max_length=255, null=True, verbose_name="nombre del cliente")
    ruc = models.CharField(max_length=14, null=True)
    telefono = models.CharField(max_length=255, null=True)
    direccion = models.TextField(max_length=255, null=True)
    limite_credito = models.FloatField(default=0.0)
    saldo = models.FloatField(default=0.0)
    disponible = models.FloatField(default=0.0)
    short_name = models.CharField(max_length=8, null=True, blank=True)
    plazo = models.IntegerField(default=0, help_text="dias de credito")

    def __unicode__(self):
        return '{} - {}'.format(self.nombre, self.ruc)

    def short(self):
        if self.short_name:
            return self.short_name
        else:
            return self.nombre[:8]

    def facturas(self):
        return Factura.objects.filter(cliente=self)

    def recibos(self):
        return Roc.objects.filter(cliente=self)

    def saldo_flotante_dolares(self):
        saldo = 0.0
        if self.recibos().filter(moneda='DOLARES'):
            for r in self.recibos().filter(moneda='DOLARES'):
                saldo += (r.monto - r.monto_aplicado())
        return round(saldo, 2)

    def saldo_flotante_cordobas(self):
        saldo = 0.0
        if self.recibos().filter(moneda='CORDOBAS'):
            for r in self.recibos().filter(moneda='CORDOBAS'):
                saldo += (r.monto - r.monto_aplicado())
        return round(saldo, 2)

    def vencida_cordobas(self):
        amount = 0.0
        fs = self.facturas().filter(moneda='CORDOBAS', fecha_vence__lte=timezone.now())
        if fs:
            amount += fs.aggregate(Sum('saldo'))['saldo__sum']
        return round(amount, 2)

    def corriente_cordobas(self):
        amount = 0.0
        fs = self.facturas().filter(moneda='CORDOBAS', fecha_vence__gt=timezone.now())
        if fs:
            amount += fs.aggregate(Sum('saldo'))['saldo__sum']
        return round(amount, 2)

    def saldo_cordobas(self):
        return round(self.vencida_cordobas() + self.corriente_cordobas(), 2)

    def vencida_dolares(self):
        amount = 0.0
        fs = self.facturas().filter(moneda='DOLARES', fecha_vence__lte=timezone.now())
        if fs:
            amount += fs.aggregate(Sum('saldo'))['saldo__sum']
        return round(amount * cordobizar(), 2)

    def corriente_dolares(self):
        amount = 0.0
        fs = self.facturas().filter(moneda='DOLARES', fecha_vence__gt=timezone.now())
        if fs:
            amount += fs.aggregate(Sum('saldo'))['saldo__sum']
        return round(amount * cordobizar(), 2)

    def saldo_dolares(self):
        return round((self.vencida_dolares() + self.corriente_dolares()) / cordobizar(), 2)

    def calcular_saldo(self):
        self.saldo = self.saldo_cordobas() + cordobizar(self.saldo_dolares())
        self.save()
        return self.saldo

    def ecuenta(self):
        data = []
        if self.facturas():
            for f in self.facturas():
                data.append({'fecha': f.fecha, 'numero_doc': f.numero_doc(),
                             'concepto': f.concepto(), 'monto': f.grantotal, 'moneda': f.moneda,
                             'class': 'green ' + f.moneda, 'saldo': f.saldo})
                if f.ir and f.numero_ir:
                    data.append({'fecha': f.fecha, 'numero_doc': f.numero_ir,
                                 'concepto': 'Retencion en la Fuente', 'monto': -f.ir, 'moneda': f.moneda,
                                 'class': 'red ' + f.moneda, 'saldo': 0.0})
                if f.al and f.numero_al:
                    data.append({'fecha': f.fecha, 'numero_doc': f.numero_al,
                                 'concepto': 'Retencion Alcaldia Municipal', 'monto': -f.al, 'moneda': f.moneda,
                                 'class': 'red ' + f.moneda, 'saldo': 0.0})
        if self.notasdebito():
            for f in self.notasdebito():
                data.append({'fecha': f.fecha, 'numero_doc': f.numero_doc(),
                             'concepto': f.concepto(), 'monto': f.grantotal, 'moneda': f.moneda,
                             'class': 'green ' + f.moneda, 'saldo': f.saldo})
                if f.ir and f.numero_ir:
                    data.append({'fecha': f.fecha, 'numero_doc': f.numero_ir,
                                 'concepto': 'Retencion en la Fuente', 'monto': -f.ir, 'moneda': f.moneda,
                                 'class': 'red ' + f.moneda, 'saldo': 0.0})
                if f.al and f.numero_al:
                    data.append({'fecha': f.fecha, 'numero_doc': f.numero_al,
                                 'concepto': 'Retencion Alcaldia Municipal', 'monto': -f.al, 'moneda': f.moneda,
                                 'class': 'red ' + f.moneda, 'saldo': 0.0})
        if self.recibos():
            for f in self.recibos():
                data.append({'fecha': f.fecha, 'numero_doc': f.numero_doc(),
                             'concepto': f.concepto, 'monto': -f.monto, 'moneda': f.moneda,
                             'class': 'red ' + f.moneda})
        return sorted(data, key=lambda x: x['fecha'])


class Factura(Base):
    primer_estatus = "Factura"
    fecha = models.DateField(null=True, blank=True)
    fecha_vence = models.DateField(null=True, blank=True)
    moneda = models.CharField(max_length=65, null=True, choices=MONEDAS, default="CORDOBAS", blank=True)
    tc = models.FloatField(default=1.0, blank=True)
    numero = models.PositiveIntegerField(null=True, blank=True)
    blog = models.TextField(max_length=5000, verbose_name="Correos e Información Relacionada",
                            null=True, blank=True)
    impreso = models.BooleanField(default=False)
    vencido = models.BooleanField(default=False)
    saldo = models.FloatField(default=0.0, blank=True)

    cliente = models.ForeignKey(Cliente, null=True)

    cancelada = models.BooleanField(default=False)
    referencia = models.CharField(max_length=14, null=True)
    pago = models.CharField(max_length=100, null=True, verbose_name="condicion de pago")
    subtotal = models.FloatField(default=0.0)
    iva = models.FloatField(default=0.0)
    grantotal = models.FloatField(default=0.0, verbose_name="total")
    ir = models.FloatField(default=0.0)
    numero_ir = models.CharField(max_length=25, null=True, blank=True)
    retencion_ir = models.FileField(null=True, blank=True)
    al = models.FloatField(default=0.0)
    numero_al = models.CharField(max_length=25, null=True, blank=True)
    retencion_al = models.FileField(null=True, blank=True)

    def detalle(self):
        return dFactura.objects.filter(factura=self)

    def numero_doc(self):
        return 'F - ' + self.numero_impreso()

    def to_json(self):
        return {'id': self.id,
                'numero': self.numero_doc(),
                'fecha': self.fecha,
                'fecha_vence': self.get_fecha_vence(),
                'cliente': self.cliente.id,
                'nombre': self.cliente.nombre,
                'ruc': self.cliente.ruc,
                'telefono': self.cliente.telefono,
                'direccion': self.cliente.direccion,
                'subtotal': self.subtotal,
                'iva': self.iva,
                'grantotal': self.grantotal,
                'cal_ir': self.cal_ir(),
                'cal_al': self.cal_al(),
                'saldo': self.saldo,
                'moneda': self.moneda,
                'url': self.edit_url(),
                'tipcontent': self.tipcontent()}

    def tipcontent(self):
        return "{0}. {4} con fecha {5} por {1} {2} Vencida!. Telf: {3}".format(
            self.nombre, self.saldo, self.moneda, self.telefono, self.nombre_doc(), self.fecha)

    def cal_ir(self):
        base = self.subtotal
        if self.moneda == 'CORDOBAS':
            if base > 1000:
                return round(base * 0.02, 2)
            else:
                return 0.0
        if self.moneda == 'DOLARES':
            if (base * self.tc) > 1000:
                return round(base * 0.02, 2)
            else:
                return 0.0

    def aplicar_ir(self, numero, monto):
        self.numero_ir = numero
        self.ir = monto
        self.saldo = self.saldo - monto
        self.save()

    def cal_al(self):
        base = self.subtotal
        if self.moneda == 'CORDOBAS':
            if base > 1000:
                return round(base * 0.01, 2)
            else:
                return 0.0
        if self.moneda == 'DOLARES':
            if (base * self.tc) > 1000:
                return round(base * 0.01, 2)
            else:
                return 0.0

    def aplicar_al(self, numero, monto):
        self.numero_al = numero
        self.al = monto
        self.saldo = self.saldo - monto
        self.save()

    def concepto(self):
        return '%s' % (str(self))

    def get_fecha_vence(self):
        if self.cliente:
            return self.fecha + timedelta(days=self.cliente.plazo)
        else:
            return None


    def revertir_saldo(self, saldo):
        self.saldo = self.saldo + saldo
        self.save()

    def numero_impreso(self, ceros=4):
        return str(self.numero).zfill(ceros)

    def simbolo_moneda(self):
        if self.moneda == MONEDAS[0][0]:
            return "C$"
        if self.moneda == MONEDAS[1][0]:
            return "U$"

    def nombre_doc(self):
        if not self.numero and not self.fecha:
            return self.primer_estatus
        else:
            return "%s # %s" % (self._meta.verbose_name, self.numero_impreso())

    nombre_doc.short_description = "Documento"

    def get_tc(self):
        return cordobizar(1, self.fecha, 4)

    def __unicode__(self):
        return self.nombre_doc()

    def save(self, *args, **kwargs):
        if not self.fecha:
            self.fecha = timezone.now()
        self.tc = self.get_tc()
        self.fecha_vence = self.get_fecha_vence()
        super(Factura, self).save(*args, **kwargs)


class dFactura(Base):
    factura = models.ForeignKey(Factura)
    cantidad = models.FloatField(default=1)
    descripcion = models.CharField(max_length=255, default="")
    precio = models.FloatField(default=0.0)
    diva = models.PositiveIntegerField(default=15)
    total = models.FloatField(default=0.0)

    class Meta:
        ordering = ['id', ]

    def __unicode__(self):
        return "%s - %s" % (str(self.cantidad), self.descripcion)

    def print_descripcion(self):
        text = ""
        lineas = self.descripcion.split("/n")
        for l in lineas:
            text += l + "<br>"
        return mark_safe(text)


class Retencion(Base):
    primer_estatus = "Borrador"
    fecha = models.DateField(null=True, blank=True)
    fecha_vence = models.DateField(null=True, blank=True)
    moneda = models.CharField(max_length=65, null=True, choices=MONEDAS, default="CORDOBAS", blank=True)
    tc = models.FloatField(default=1.0, blank=True)
    numero = models.PositiveIntegerField(null=True, blank=True)
    blog = models.TextField(max_length=5000, verbose_name="Correos e Información Relacionada",
                            null=True, blank=True)
    impreso = models.BooleanField(default=False)
    vencido = models.BooleanField(default=False)
    saldo = models.FloatField(default=0.0, blank=True)
    retenido = models.CharField(max_length=255, default="")
    ruc = models.CharField(max_length=14, null=True)
    cedula = models.CharField(max_length=14, null=True)
    concepto = models.CharField(max_length=255, null=True)
    base = models.FloatField(default=0.0)
    aplicado = models.FloatField(default=2.0, verbose_name="% de retension aplicado")
    monto = models.FloatField(default=0.0)
    cheque = models.CharField(max_length=14, null=True)
    banco = models.CharField(max_length=35, null=True, choices=BANCOS)
    telefono = models.CharField(max_length=14, null=True)
    factura = models.CharField(max_length=14, null=True, verbose_name='facturas')

    class Meta:
        verbose_name_plural = "Retenciones"

    def print_mes(self):
        return MESES[self.fecha.month   - 1]

    def print_anno(self):
        return str(self.fecha.year)[3]


class Roc(Base):
    primer_estatus = "Borrador"
    fecha = models.DateField(null=True, blank=True)
    fecha_vence = models.DateField(null=True, blank=True)
    moneda = models.CharField(max_length=65, null=True, choices=MONEDAS, default="CORDOBAS", blank=True)
    tc = models.FloatField(default=1.0, blank=True)
    numero = models.PositiveIntegerField(null=True, blank=True)
    blog = models.TextField(max_length=5000, verbose_name="Correos e Información Relacionada",
                            null=True, blank=True)
    impreso = models.BooleanField(default=False)
    vencido = models.BooleanField(default=False)
    saldo = models.FloatField(default=0.0, blank=True)
    numero = models.PositiveIntegerField(null=True, blank=True)
    nombre = models.CharField(max_length=165, null=True)
    cliente = models.ForeignKey(Cliente, null=True)
    monto = models.FloatField(default=0.0)
    concepto = models.TextField(max_length=600, null=True)
    referencia = models.CharField(max_length=125, null=True, blank=True)
    banco = models.CharField(max_length=65, choices=BANCOS, default='BANPRO')

    def get_tc(self):
        return self.tc

    def abonos(self):
        return Abono.objects.filter(roc=self)

    def has_abonos(self):
        if self.abonos().count() > 0:
            return True
        else:
            return False

    def monto_aplicado(self):
        monto = 0.0
        if self.moneda == 'CORDOBAS':
            ac = self.abonos().filter(moneda='CORDOBAS')
            if ac:
                monto += ac.aggregate(Sum('monto'))['monto__sum']
            ad = self.abonos().filter(moneda='DOLARES')
            if ad:
                monto += ad.aggregate(Sum('monto'))['monto__sum'] * self.tc
        if self.moneda == 'DOLARES':
            ac = self.abonos().filter(moneda='CORDOBAS')
            if ac:
                monto += ac.aggregate(Sum('monto'))['monto__sum'] / self.tc
            ad = self.abonos().filter(moneda='DOLARES')
            if ad:
                monto += ad.aggregate(Sum('monto'))['monto__sum']
        return round(monto, 2)

    def disponible(self):
        return round(self.monto - self.monto_aplicado(), 2)

    def cuadrado(self):
        if abs(self.disponible()) > 1:
            return True
        else:
            return False

    def numero_doc(self):
        return 'ROC - ' + self.numero_impreso()

    class Meta:
        verbose_name = "Recibo Oficial de Caja"
        verbose_name_plural = "Recibos Oficiales de Caja"


class Abono(Base):
    roc = models.ForeignKey(Roc)
    tipo_doc = models.ForeignKey(ContentType)
    nodoc = models.IntegerField()
    moneda = models.CharField(max_length=10, choices=MONEDAS)
    monto = models.FloatField(default=0.0)
    saldo = models.FloatField(default=0.0)
    aplicado = models.BooleanField(default=False)

    def __unicode__(self):
        if self.documento():
            return '{0}   {1}'.format(self.documento().cliente.nombre, self.monto)
        else:
            return '{}'.format(self.monto)

    def documento(self):
        try:
            return self.tipo_doc.model_class().objects.get(id=self.nodoc)
        except:
            return None

    def aplicar(self):
        if not self.aplicado:
            doc = self.documento()
            doc.saldo = doc.saldo - self.monto
            doc.save()
            self.aplicado = True
            self.save()

    def numero_doc(self):
        pre = ''
        if str(self.tipo_doc) == 'factura':
            pre = 'F - '
        else:
            pre = 'ND - '
        if self.documento():
            return pre + self.documento().numero_impreso()
        else:
            return pre
    numero_doc.short_description = "Referencia"

    def fecha(self):
        return self.roc.fecha

    def cliente(self):
        return self.roc.cliente

    def delete(self, *args,**kwargs):
        if self.aplicado:
            self.documento().revertir_saldo(self.monto)
        super(Abono, self).delete(*args, **kwargs)