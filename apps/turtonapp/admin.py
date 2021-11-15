from django.contrib import admin
from .models import BareModule, ComplementConstants, Equipment, MaterialFactor, PressureFactor, PurchasedFactor


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
    list_display = ('equipment', 'b1', 'b2', 'material', 'condition')
    list_display_links = ('equipment', 'b1', 'b2', 'material', 'condition')
    search_fields = ('equipment__description', 'equipment__equipment__name', '')
    list_filter = ('equipment__equipment',)
    list_per_page = 10


admin.site.register(Equipment, ListandoEquipamentos)
admin.site.register(PurchasedFactor, ListandoKs)
admin.site.register(BareModule, ListandoBare)
admin.site.register(ComplementConstants, ListandoComplement)
admin.site.register(PressureFactor, ListandoPressure)
admin.site.register(MaterialFactor, ListandoMaterial)
