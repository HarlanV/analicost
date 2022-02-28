from django.db import models
from datetime import datetime
# from capex.models import Equipment, PurchasedFactor, EquipmentUnity

# Create your models here.


class Cepci(models.Model):
    ''' Taxas de CEPCI  '''
    taxa = models.FloatField()
    ano = models.IntegerField()
    data = models.DateField(blank=True, null=True)

    def __str__(self):
        return str(self.ano)

    class Meta:
        db_table = "media_cepci_anual"


class CapexProject(models.Model):
    project_number = models.IntegerField(default=100)
    cepci = models.FloatField(default=601.8)
    year = models.IntegerField(default=2017)
    purchased_equip_cost = models.FloatField(default=0.00)
    baremodule_cost = models.FloatField(default=0.00)
    base_equipment_cost = models.FloatField(default=0.00)
    base_baremodule_cost = models.FloatField(default=0.00)
    total_module_cost = models.FloatField(default=0.00)
    total_grassroot_cost = models.FloatField(default=0.00)
    total_equipment_cost = models.FloatField(default=0.00)
    total_langfactor = models.FloatField(default=0.00)
    lang_factor = models.FloatField(default=4.74)

    class Meta:
        db_table = "capex_project"

    def __str__(self):
        return str(self.project_number)


class Dimension(models.Model):
    dimension = models.CharField(max_length=300, null=True)
    symbol = models.CharField(max_length=300, null=True)
    unity = models.CharField(max_length=300, null=True)

    def __str__(self):
        return self.dimension

    class Meta:
        db_table = "dimension"


class Equipment(models.Model):
    name = models.CharField(max_length=300)
    description = models.CharField(max_length=100, null=True, blank=True)
    dimension = models.ForeignKey(Dimension, on_delete=models.CASCADE)
    symbol = models.CharField(max_length=10, null=True, blank=True)

    def __str__(self):
        return self.name

    class Meta:
        db_table = "capex_equipment"


class PurchasedFactor(models.Model):
    material = models.CharField(max_length=100, null=True)
    description = models.CharField(max_length=100, null=True)
    k1 = models.FloatField(null=True)
    k2 = models.FloatField(null=True)
    k3 = models.FloatField(null=True)
    max_dimension = models.FloatField(null=True)
    min_dimension = models.FloatField(null=True)
    fixed_value = models.FloatField(null=True)
    equipment = models.ForeignKey(Equipment, on_delete=models.CASCADE)
    reference_year = models.IntegerField(blank=True, null=True)
    cepci = models.FloatField(null=True, blank=True)
    is_reference = models.BooleanField(default=0, blank=True)

    class Meta:
        db_table = "capex_purchase_factor"

    def __str__(self):
        return str(self.description + "(" + self.material + ")")


class PressureFactor(models.Model):
    c1 = models.FloatField(null=True)
    c2 = models.FloatField(null=True)
    c3 = models.FloatField(null=True)
    pressure_min = models.FloatField(null=True)
    pressure_max = models.FloatField(null=True)
    condition = models.CharField(max_length=300, null=True)
    equipment = models.ForeignKey(PurchasedFactor, on_delete=models.CASCADE)

    class Meta:
        db_table = "capex_pressure_factor"


class MaterialFactor(models.Model):
    b1 = models.FloatField(null=True)
    b2 = models.FloatField(null=True)
    fm = models.FloatField(null=True)
    material = models.CharField(max_length=200, null=True)
    condition = models.CharField(max_length=300, null=True, blank=True)
    equipment = models.ForeignKey(PurchasedFactor, on_delete=models.CASCADE)

    class Meta:
        db_table = "capex_material_factor"


class BareModule(models.Model):
    fbm = models.FloatField(null=True)
    calculated = models.BooleanField(null=True)
    equipment = models.ForeignKey(PurchasedFactor, on_delete=models.CASCADE)

    def __str__(self):
        return str(self.fbm)

    class Meta:
        db_table = "capex_baremodule"


class ComplementConstants(models.Model):
    constant = models.CharField(max_length=300, null=True)
    value = models.FloatField(null=True)
    description = models.CharField(max_length=300, null=True)
    equipment = models.ForeignKey(PurchasedFactor, on_delete=models.CASCADE)

    def __str__(self):
        return self.constant

    class Meta:
        db_table = "capex_complement_constants"


class EquipmentUnity(models.Model):
    dimension = models.ForeignKey(Dimension, on_delete=models.CASCADE)
    unity = models.CharField(max_length=300, null=True)
    unity_math = models.CharField(max_length=300, null=True)
    convert_factor = models.FloatField(null=True, blank=True)
    is_default = models.BooleanField(null=True, blank=True)

    def __str__(self):
        return self.unity

    class Meta:
        db_table = "equipment_unity"


class EquipmentProject(models.Model):
    purchased_factor = models.ForeignKey(PurchasedFactor, on_delete=models.CASCADE)
    project = models.ForeignKey(CapexProject, on_delete=models.CASCADE)
    equipment = models.ForeignKey(Equipment, on_delete=models.CASCADE)
    spares = models.IntegerField(default=0, blank=True)
    specification = models.FloatField(default=0, blank=True)
    pressure = models.FloatField(default=0, blank=True)
    pressureunity = models.ForeignKey(EquipmentUnity, on_delete=models.CASCADE, blank=True, null=True, related_name="related_equipment")
    preference_unity = models.ForeignKey(EquipmentUnity, on_delete=models.CASCADE, blank=True, null=True)
    equipment_code = models.CharField(max_length=30, null=True)
    purchased_equip_cost = models.FloatField(null=True)
    baremodule_cost = models.FloatField(null=True)
    base_equipment_cost = models.FloatField(null=True)
    base_baremodule_cost = models.FloatField(null=True)
    cepci = models.FloatField(default=4.74)
    year = models.FloatField(default=2007)

    def __str__(self):
        return self.equipment_code

    class Meta:
        db_table = "capex_equipment_project"


def get_cepci(year):
    cepci = Cepci.objects.filter(ano=year).first().taxa
    return cepci


def fluxoCaixa():
    return 0
