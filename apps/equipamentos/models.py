from django.db import models
from datetime import datetime
from turtonapp.models import Dimension, Equipment
# from app.models import App
# equipamento = models.ForeignKey(Equipamento, on_delete=models.CASCADE)
# para importar e/ou relacionar com outras apps


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
