from django.core.management.base import BaseCommand



class Command(BaseCommand):
    help = "Prueba"

    def handle(self, *args, **options):
        print "funka!"





