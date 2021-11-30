from django.contrib import admin
from .models import HistoricoFluxoCaixa, Cepci, CapexProject, EquipmentProject


class ListandoFluxoCaixa(admin.ModelAdmin):
    list_display = ('descricao', 'valor', 'data')
    list_display_links = ('descricao', 'valor')
    search_fields = ('descricao',)
    list_filter = ('data',)
    list_per_page = 4


class ListagemCepci(admin.ModelAdmin):
    list_display = ('ano', 'taxa')
    list_display_links = ('ano', 'taxa')
    search_fields = ('taxa', 'ano')
    list_filter = ('ano',)
    list_per_page = 5


class ListCapex(admin.ModelAdmin):
    list_display = ('id', 'project_number', 'cepci')
    list_display_links = ('id', 'project_number', 'cepci')
    list_per_page = 5


class ListEquipmentCapex(admin.ModelAdmin):
    list_display = ('id', 'equipment_code', 'equipment', 'purchased_factor', 'baremodule_cost')
    list_display_links = ('id', 'equipment_code', 'equipment', 'purchased_factor', 'baremodule_cost')
    list_per_page = 5


admin.site.register(Cepci, ListagemCepci)
admin.site.register(CapexProject, ListCapex)
admin.site.register(EquipmentProject, ListEquipmentCapex)
admin.site.register(HistoricoFluxoCaixa, ListandoFluxoCaixa)
