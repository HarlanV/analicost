from django.db import models
from turtonapp.models import Equipment, PurchasedFactor

# Create your models here.


class HistoricoFluxoCaixa(models.Model):
    ''' Histórico e previsões de lançamentos no livro caixa da empresa  '''
    descricao = models.CharField(max_length=100)
    valor = models.FloatField()
    data = models.DateField()
    entrada = models.BooleanField(null=True)
    saida = models.BooleanField(null=True)

    def __str__(self):
        return self.descricao

    class Meta:
        db_table = "fluxo_caixa_empresa"


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


class EquipmentProject(models.Model):
    purchased_factor = models.ForeignKey(PurchasedFactor, on_delete=models.CASCADE)
    project = models.ForeignKey(CapexProject, on_delete=models.CASCADE)
    equipment = models.ForeignKey(Equipment, on_delete=models.CASCADE)
    spares = models.IntegerField(default=0, blank=True)
    specification = models.FloatField(default=0, blank=True)
    pressure = models.FloatField(default=0, blank=True)
    # colocar aqui a dimensão

    # project = models.ManyToManyField(CapexProject)
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
