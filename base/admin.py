from import_export.admin import ImportExportModelAdmin

class entidad_admin(ImportExportModelAdmin):
    list_display = ('code', 'name')
    search_fields = ('code', 'name')
    list_filter = ('activo', )
    fields = (('name', 'code'), 'activo')
