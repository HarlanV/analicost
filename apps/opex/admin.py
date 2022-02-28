from django.contrib import admin
from .models import HistoricoFluxoCaixa


# Register your models here.
class ListandoFluxoCaixa(admin.ModelAdmin):
    list_display = ('descricao', 'valor', 'data')
    list_display_links = ('descricao', 'valor')
    search_fields = ('descricao',)
    list_filter = ('data',)
    list_per_page = 4


admin.site.register(HistoricoFluxoCaixa, ListandoFluxoCaixa)
