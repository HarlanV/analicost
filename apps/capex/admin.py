from django.contrib import admin
from .models import Cepci, CapexProject, EquipmentProject
from django.contrib import admin
from .models import BareModule, ComplementConstants, Dimension, Equipment, EquipmentUnity, MaterialFactor, PressureFactor, PurchasedFactor


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


class ListandoEquipamentos(admin.ModelAdmin):
    list_display = ('id', 'name', 'description', 'dimension')
    list_display_links = ('id', 'name', 'description')
    search_fields = ('name',)
    list_filter = ('name',)
    list_per_page = 10


class ListandoKs(admin.ModelAdmin):
    list_display = ('id', 'equipment', 'description', 'material', 'k1', 'k2', 'k3', )
    list_display_links = ('id', 'equipment', 'description', 'material', 'k1', 'k2', 'k3', )
    search_fields = ('equipment__name', 'description', 'material')
    list_filter = ('equipment__name',)
    list_per_page = 10


class ListandoBare(admin.ModelAdmin):
    list_display = ('fbm', 'calculated', 'equipment')
    list_display_links = ('fbm', 'calculated', 'equipment')
    search_fields = ('equipment__description', 'equipment__equipment__name', '')
    list_filter = ('equipment__equipment',)
    list_per_page = 10


class ListandoComplement(admin.ModelAdmin):
    list_display = ('constant', 'value', 'description', 'equipment')
    list_display_links = ('constant', 'value', 'description', 'equipment')
    search_fields = ('equipment__description', 'equipment__equipment__name', '')
    list_filter = ('equipment__equipment',)
    list_per_page = 10


class ListandoPressure(admin.ModelAdmin):
    list_display = ('equipment', 'c1', 'c2', 'c3', 'pressure_min', 'pressure_max', 'condition')
    list_display_links = ('equipment', 'c1', 'c2', 'c3', 'pressure_min', 'pressure_max')
    search_fields = ('equipment__description', 'equipment__equipment__name', '')
    list_filter = ('equipment__equipment',)
    list_per_page = 10


class ListandoMaterial(admin.ModelAdmin):
    list_display = ('equipment', 'b1', 'b2', 'material', 'condition', 'fm')
    list_display_links = ('equipment', 'b1', 'b2', 'material', 'condition', 'fm')
    search_fields = ('equipment__description', 'equipment__equipment__name', '')
    list_filter = ('equipment__equipment',)
    list_per_page = 10


class ListandoUnidades(admin.ModelAdmin):
    list_display = ('id', 'dimension', 'unity', 'is_default')
    list_display_links = ('id', 'dimension', 'unity')
    search_fields = ('dimension',)
    list_filter = ('dimension',)
    list_per_page = 10


class ListandoDimension(admin.ModelAdmin):
    list_display = ('id', 'dimension', 'unity', 'symbol')
    list_display_links = ('id', 'dimension', 'unity')
    search_fields = ('dimension',)
    list_filter = ('dimension',)
    list_per_page = 10


admin.site.register(EquipmentUnity, ListandoUnidades)
admin.site.register(Equipment, ListandoEquipamentos)
admin.site.register(PurchasedFactor, ListandoKs)
admin.site.register(BareModule, ListandoBare)
admin.site.register(ComplementConstants, ListandoComplement)
admin.site.register(PressureFactor, ListandoPressure)
admin.site.register(MaterialFactor, ListandoMaterial)
admin.site.register(Dimension, ListandoDimension)
admin.site.register(Cepci, ListagemCepci)
admin.site.register(CapexProject, ListCapex)
admin.site.register(EquipmentProject, ListEquipmentCapex)
