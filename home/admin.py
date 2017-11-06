from django.contrib import admin

# Register your models here.
from import_export.admin import ImportExportModelAdmin

from home.models import nicaragua_import


class Import_Export_admin(ImportExportModelAdmin):
    pass


#admin.site.register(nicaragua_import, ImportExportModelAdmin)