from django.db import models
from datetime import datetime
# from app.models import App
# equipamento = models.ForeignKey(Equipamento, on_delete=models.CASCADE)
# para importar e/ou relacionar com outras apps


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
        db_table = "turton_equipment"


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
        db_table = "turton_purchase_factor"

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
        db_table = "turton_pressure_factor"


class MaterialFactor(models.Model):
    b1 = models.FloatField(null=True)
    b2 = models.FloatField(null=True)
    fm = models.FloatField(null=True)
    material = models.CharField(max_length=200, null=True)
    condition = models.CharField(max_length=300, null=True)
    equipment = models.ForeignKey(PurchasedFactor, on_delete=models.CASCADE)

    class Meta:
        db_table = "turton_material_factor"


class BareModule(models.Model):
    fbm = models.FloatField(null=True)
    calculated = models.BooleanField(null=True)
    equipment = models.ForeignKey(PurchasedFactor, on_delete=models.CASCADE)

    def __str__(self):
        return str(self.fbm)

    class Meta:
        db_table = "turton_baremodule"


class ComplementConstants(models.Model):
    constant = models.CharField(max_length=300, null=True)
    value = models.FloatField(null=True)
    description = models.CharField(max_length=300, null=True)
    equipment = models.ForeignKey(PurchasedFactor, on_delete=models.CASCADE)

    def __str__(self):
        return self.constant

    class Meta:
        db_table = "turton_complement_constants"


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
