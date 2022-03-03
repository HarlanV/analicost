from django.db import models
from capex.models import CapexProject, EquipmentProject, EquipmentUnity


# Create your models here.
class CashFlow(models.Model):
    ''' Histórico e previsões de lançamentos no livro caixa da empresa  '''
    # para evitar o tratamento de datas no front, bem como buscar como funciona, será utilizado formato int para ano
    # TODO: mudar para datefield
    year = models.IntegerField(null=True, blank=True)
    descricao = models.CharField(max_length=100)
    valor = models.FloatField()
    data = models.DateField()

    def __str__(self):
        return self.descricao

    class Meta:
        db_table = "cash_flow"


# Create your models here.
class Opex(models.Model):
    ''' Histórico e previsões de lançamentos no livro caixa da empresa  '''
    # para evitar o tratamento de datas no front, bem como buscar como funciona, será utilizado formato int para ano
    # TODO: mudar para datefield

    fixed_costs = models.FloatField(default=0.00, null=True, blank=True)
    general_expenses = models.FloatField(default=0.00, null=True, blank=True)
    direct_costs = models.FloatField(default=0.00, null=True, blank=True)

    # Cost Raw Material
    crm = models.FloatField(default=0.00, null=True, blank=True)

    # Cosw Waste Treatment
    cwt = models.FloatField(default=0.00, null=True, blank=True)

    # Cost Utilities
    cut = models.FloatField(default=0.00, null=True, blank=True)

    # Cost Operational Labor
    col = models.FloatField(default=0.00, null=True, blank=True)

    # Operational Cost
    com = models.FloatField(default=0.00, null=True, blank=True)

    # fixed capital Investiment (capex)
    fcil = models.FloatField(default=0.00, null=True, blank=True)

    # Cash In
    revenue = models.FloatField(default=0.00, blank=True, null=True)

    # CashBack when the plant is sold
    salvage = models.FloatField(default=0.00, blank=True, null=True)

    # Initial investiment on opex (not capex!)
    working_capital = models.FloatField(default=0.00, blank=True, null=True)

    depreciation = models.FloatField(default=0.00, null=True, blank=True)
    project = models.ForeignKey(CapexProject, on_delete=models.CASCADE)

    def __str__(self):
        return "opex_project_" + str(self.project.project_number)

    class Meta:
        db_table = "opex_factors"


class OpexAuxiliateFactor(models.Model):
    project = models.ForeignKey(CapexProject, on_delete=models.CASCADE)
    crm = models.FloatField(default=1.23)
    cwt = models.FloatField(default=1.23)
    cut = models.FloatField(default=1.23)
    col = models.FloatField(default=2.76)
    fcil = models.FloatField(default=0.18)
    working_capital_a = models.FloatField(default=0.10)
    working_capital_b = models.FloatField(default=0.10)
    working_capital_c = models.FloatField(default=0.10)
    year1 = models.FloatField(default=1, blank=True, null=True)
    year2 = models.FloatField(default=0, blank=True, null=True)
    year3 = models.FloatField(default=0, blank=True, null=True)
    year4 = models.FloatField(default=0, blank=True, null=True)
    year5 = models.FloatField(default=0, blank=True, null=True)

    def __str__(self):
        return "from project " + str(self.project.project_number)

    class Meta:
        db_table = "opex_auxiliar_factor"


class OpexProjectSettings(models.Model):
    project = models.ForeignKey(CapexProject, on_delete=models.CASCADE)
    capex_source = models.CharField(max_length=25, null=True, blank=True)
    revenue_calculated = models.BooleanField(default=True, blank=True)
    crm_calculated = models.BooleanField(default=True, blank=True)
    salvage_calculated = models.BooleanField(default=True, blank=True)
    cut_calculated = models.BooleanField(default=True, blank=True)
    wc_calculated = models.BooleanField(default=True, blank=True)
    col_calculated = models.BooleanField(default=True, blank=True)
    cwt_calculated = models.BooleanField(default=True, blank=True)
    construction_period = models.IntegerField(default=2, blank=True, null=True)
    project_life = models.IntegerField(default=10, blank=True, null=True)

    def __str__(self):
        return "project_" + str(self.project.project_number)

    class Meta:
        db_table = "opex_project_settings"


class MaterialCosts(models.Model):
    project = models.ForeignKey(CapexProject, on_delete=models.CASCADE, null=True)
    name = models.CharField(max_length=300)
    classification = models.CharField(max_length=300, blank=True, null=True)
    price = models.FloatField(default=0, blank=True, null=True)
    unity = models.ForeignKey(EquipmentUnity, on_delete=models.CASCADE, blank=True, null=True, related_name="buyed_materials")
    flow = models.FloatField(default=0, blank=True, null=True)
    flow_unity = models.ForeignKey(EquipmentUnity, on_delete=models.CASCADE, blank=True, null=True)

    def __str__(self):
        return self.name

    class Meta:
        db_table = "opex_materials"


class EquipmentsUtilitiesSetting (models.Model):
    equipment = models.ForeignKey(EquipmentProject, on_delete=models.CASCADE)
    cost_unity = models.ForeignKey(EquipmentUnity, on_delete=models.SET_NULL, blank=True, null=True, related_name="cost_unity_utilities")
    duty_unity = models.ForeignKey(EquipmentUnity, on_delete=models.SET_NULL, blank=True, null=True)
    annual_cost = models.FloatField(default=0.00, blank=True, null=True)
    duty = models.FloatField(default=0.00, blank=True, null=True)
    efficiency = models.FloatField(default=0.00, blank=True, null=True)
    utility = models.ForeignKey('ProjectUtilitiesConstant', on_delete=models.CASCADE, blank=True, null=True)
    utility_cost = models.FloatField(default=0.00, blank=True, null=True)

    def __str__(self):
        return str(self.equipment) + "_utilities"

    class Meta:
        db_table = "utilities_settings"


class ProjectUtilitiesConstant (models.Model):
    project = models.ForeignKey(CapexProject, on_delete=models.CASCADE, null=True)
    name = models.CharField(max_length=300)
    aka = models.CharField(max_length=300, blank=True, null=True)
    classification = models.CharField(max_length=300, blank=True, null=True)
    value = models.FloatField(default=0, blank=True, null=True)
    unity = models.ForeignKey(EquipmentUnity, on_delete=models.CASCADE, blank=True, null=True, related_name="materials_costs")

    def __str__(self):
        return self.name

    class Meta:
        db_table = "utilities_constants"


fcilSourceList = {
    'Lang Factor': 'total_langfactor',
    'Total Module Cost': 'total_module_cost',
    'Grass Roots Cost': 'total_grassroot_cost',
    'Input Fcil': 'input_source'
}

# TODO: Criar um banco para variáveis default
initialUtilitiesConstans = [
    {
        'name': 'Electricity (110V - 440V)',
        'value': 18.72,
        'aka': 'Eletricity',
        'classification': 'Common Utilities',
        'unity': '$/GJ'
    },

    {
        'name': 'Cooling Water (30°C to 45°C)',
        'value': 0.378,
        'aka': 'Cooling Water',
        'classification': 'Water',
        'unity': '$/GJ'
    },

    {
        'name': 'Refrigerated Water (15°C to 25°C)',
        'value': 4.77,
        'aka': 'Refrigerated Water',
        'classification': 'Water',
        'unity': '$/GJ'
    },


    {
        'name': 'Low Pressure (5 barg, 160°C)',
        'value': 2.03,
        'aka': 'Low Pressure Steam',
        'classification': 'Steam from Boilers',
        'unity': '$/GJ'
    },

    {
        'name': 'Medium Pressure (10 barg, 184°C)',
        'value': 2.78,
        'aka': 'Medium Pressure Steam',
        'classification': 'Steam from Boilers',
        'unity': '$/GJ'
    },

    {
        'name': 'High Pressure (41 barg, 254°C)',
        'value': 5.66,
        'aka': 'High Pressure Steam',
        'classification': 'Steam from Boilers',
        'unity': '$/GJ'
    },

    {
        'name': 'Fuel Oil (no. 2)',
        'value': 10.3,
        'aka': 'Fuel Oil',
        'classification': 'Fuels',
        'unity': '$/GJ'
    },

    {
        'name': 'Natural Gas',
        'value': 3.16,
        'aka': 'Natural Gas',
        'classification': 'Fuels',
        'unity': '$/GJ'
    },

    {
        'name': 'Coal (FOB mine mouth)',
        'value': 2.04,
        'aka': 'COAL',
        'classification': 'Fuels',
        'unity': '$/GJ'
    },

    {
        'name': 'Moderately High (up to 330°C)',
        'value': 3.95,
        'aka': 'Moderately High',
        'classification': 'Thermal Systems',
        'unity': '$/GJ'
    },

    {
        'name': 'High (up to 400°C)',
        'value': 3.95,
        'aka': 'High',
        'classification': 'Thermal Systems',
        'unity': '$/GJ'
    },

    {
        'name': 'Very High (up to 600°C)',
        'value': 3.95,
        'aka': 'Very High',
        'classification': 'Thermal Systems',
        'unity': '$/GJ'
    },

    {
        'name': 'Moderately Low (5°C)',
        'value': 4.77,
        'aka': 'Moderately Low',
        'classification': 'Refrigeration',
        'unity': '$/GJ'
    },

    {
        'name': 'Low (-20°C)',
        'value': 8.49,
        'aka': 'Low',
        'classification': 'Refrigeration',
        'unity': '$/GJ'
    },

    {
        'name': 'Very low (-50°C)',
        'value': 14.12,
        'aka': 'Very low',
        'classification': 'Refrigeration',
        'unity': '$/GJ'
    },

    {
        'name': 'Non-Hazardous',
        'value': 36,
        'aka': 'Non-Hazardous',
        'classification': 'Waste Disposal (solid and liquid)',
        'unity': '$/GJ'
    },

    {
        'name': 'Hazardous',
        'value': 200,
        'aka': 'Hazardous',
        'classification': 'Waste Disposal (solid and liquid)',
        'unity': '$/Tonne'
    },

    {
        'name': 'Steam used for steam-powered drives',
        'value': 5.66,
        'aka': 'Steam for drives',
        'classification': 'Cost of Steam used in Steam Drives',
        'unity': '$/GJ'
    },

    {
        'name': 'Cost of Labor (per operator/year)',
        'value': 18.72,
        'aka': 'Cost of Labor',
        'classification': 'Process Equipment',
        'unity': None,
    },

    {
        'name': 'Hours per Operting Year',
        'value': 8322.0,
        'aka': 'Hours in Year',
        'classification': 'Process Equipment',
        'unity': None,
    },

    {
        'name': 'Solids Handling Coefficient',
        'value': 18.72,
        'aka': 'Solids Handling Coefficient',
        'classification': 'Miscellaneous Numebrs',
        'unity': None,
    },

    {
        'name': 'User Defined',
        'value': 1,
        'aka': 'Defined',
        'classification': 'Inputed',
        'unity': None,
    },


]
