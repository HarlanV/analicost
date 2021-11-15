from django.contrib import admin
from .models import EquipmentUnity


class ListandoUnidades(admin.ModelAdmin):
    list_display = ('id', 'dimension', 'unity', 'is_default')
    list_display_links = ('id', 'dimension', 'unity')
    search_fields = ('dimension',)
    list_filter = ('dimension',)
    list_per_page = 10


admin.site.register(EquipmentUnity, ListandoUnidades)
