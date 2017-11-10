from django.core.management.base import BaseCommand
from dtracking.models import Gestion


class Command(BaseCommand):
    help = "Prueba"

    def handle(self, *args, **options):
        Gestion.notificar_reporte_diario()
