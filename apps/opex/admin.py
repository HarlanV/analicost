from django.contrib import admin
from .models import CashFlow, EquipmentsUtilitiesSetting, MaterialCosts, Opex, OpexAuxiliateFactor, OpexProjectSettings, ProjectUtilitiesConstant


# Register your models here.
class ListandoFluxoCaixa(admin.ModelAdmin):
    list_display = ('descricao', 'valor', 'data')
    list_display_links = ('descricao', 'valor')
    search_fields = ('descricao',)
    list_filter = ('data',)
    list_per_page = 10


class ListandoVariaveisAuxiliares(admin.ModelAdmin):
    list_display = ('project',)
    list_display_links = ('project',)
    search_fields = ('project',)
    list_per_page = 10


class ListandoUtilitiesConstants(admin.ModelAdmin):
    list_display = ('project', 'name', 'classification', 'unity')
    list_display_links = ('project', 'name', 'classification')
    search_fields = ('name',)
    list_per_page = 10


class ListandoUtilitiesSettings(admin.ModelAdmin):
    list_display = ('equipment', 'duty', 'utility', 'annual_cost')
    list_display_links = ('equipment', 'duty', 'utility', 'annual_cost')
    search_fields = ('equipment',)
    list_per_page = 10

class ListandoMaterialsInProject(admin.ModelAdmin):
    list_display = ('project', 'name', 'classification', 'price','unity','flow','flow_unity','annual_cost')
    list_display_links = ('project', 'name', 'classification', 'price','unity','flow','flow_unity','annual_cost')
    search_fields = ('name',)
    list_per_page = 10


class OpexValues(admin.ModelAdmin):
    list_display = ('project', )
    list_display_links = ('project',)
    search_fields = ('name',)
    list_per_page = 10

class ListandoOpexConfig(admin.ModelAdmin):
    list_display = ('project', )
    list_display_links = ('project',)
    search_fields = ('name',)
    list_per_page = 10





admin.site.register(CashFlow, ListandoFluxoCaixa)
admin.site.register(OpexAuxiliateFactor, ListandoVariaveisAuxiliares)
admin.site.register(ProjectUtilitiesConstant, ListandoUtilitiesConstants)
admin.site.register(EquipmentsUtilitiesSetting, ListandoUtilitiesSettings)
admin.site.register(MaterialCosts, ListandoMaterialsInProject)
admin.site.register(OpexProjectSettings, ListandoOpexConfig)
admin.site.register(Opex, OpexValues)
