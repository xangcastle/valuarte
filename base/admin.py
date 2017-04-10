from import_export.admin import ImportExportModelAdmin

class entidad_admin(ImportExportModelAdmin):
    list_display = ('code', 'name')
