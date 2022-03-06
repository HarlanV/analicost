from capex.equipments.equipments import teste_print
from capex.models import CapexProject, EquipmentUnity
from .models import EquipmentsUtilitiesSetting, MaterialCosts, Opex, OpexAuxiliateFactor as AuxiliarFactor, OpexProjectSettings, ProjectUtilitiesConstant, DefaultConstants
from django.db.models import Sum


# TODO: Transferir essa classe para services
class ManufactoryCost():

    def __init__(self, project: CapexProject):
        self.project = project
        # configs = EconomicConfig(project)
        # self.factors = configs.getConfig()
        # capex = self.factor.capex_source

    # Cria um novo material e chama as atualizações necessárias
    def createMaterial(self, args: dict):
        args["annual_cost"] = CostCalculationTools.calculateAnualCost(args["flow"], args["price"], args["flow_unity"], "kg/h")
        material = MaterialCosts(**args)
        material.save()
        self.updateMaterialCosts(args['classification'])
        # return material
        return

    # Remove um material do projeto
    def deleteMaterial(self, idMaterial):
        # consultar material armazenar os campos necessários para atualização posterior
        material = MaterialCosts.objects.get(id=idMaterial)
        classOfMaterial = material.classification
        material.delete()
        self.updateMaterialCosts(classOfMaterial)

        # Atualizar os campos relevantes
        return True

    # Atualiza os valores
    def updateMaterialCosts(self, classification: str):
        """
        for updade all material relational field, classification = "all"
        """
        materials = MaterialCosts.objects.filter(project=self.project)
        opex = Opex.objects.filter(project=self.project).first()
        config = self.checkFieldsUpdate().values()

        if ("Waste" in classification or classification == 'all') and config.first()["cwt_calculated"] is True:
            materialList = materials.filter(classification__contains="Waste")
            opex.cwt = materialList.aggregate(Sum('annual_cost'))["annual_cost__sum"]
        if (classification == "Product" or classification == 'all') and config.first()["revenue_calculated"] is True:
            materialList = materials.filter(classification__contains="Product").all()
            opex.revenue = materialList.aggregate(Sum('annual_cost'))["annual_cost__sum"]
        if ("Raw" in classification or classification == 'all') and config.first()["crm_calculated"] is True:
            materialList = materials.filter(classification__contains="Raw").all()
            opex.crm = materialList.aggregate(Sum('annual_cost'))["annual_cost__sum"]
        opex.save()
        self.checkFieldsUpdate()

    # Esta função checa se os campos devem ser atualizados ou estão como input
    def checkFieldsUpdate(self, field="all"):
        configs = OpexProjectSettings.objects.filter(project=self.project)
        if field == "all":
            return configs
        else:
            return configs.values(field)

    # Armazenado para atualização de todos os custos de manufatura do projeto
    def updateAllCosts(self):
        pass
        self.updateMaterialCosts("all")


class UtilityCost():

    def __init__(self, project: CapexProject):
        self.project = project


    # TODO: MOVER PARA OPEX
    def updateUtilitesFromEquipemt(self, equipment, args):

        # significa que é a bomba com a eficiência
        if len(args) == 1:
            utilities = EquipmentsUtilitiesSetting.objects.filter(equipment=equipment.id)
            utilities.update(**args)
            return

        utilities = EquipmentsUtilitiesSetting.objects.filter(equipment=equipment.id)
        args["duty_unity"] = EquipmentUnity.objects.get(id=args["duty_unity"])

        if 'utype' in args:
            if args["utype"] == "User Defined":
                args["utility"] = args["utype"]
            args.pop('utype', None)

        if args["utility"] == "User Defined":
            cost = CostCalculationTools.calculateAnualCost(float(args["duty"]), args["utility_cost"], args["duty_unity"],"GJ")
            args["annual_cost"] = cost
            args["utility"] = ProjectUtilitiesConstant.objects.filter(aka="Defined").first()
            args["utility_cost"] = float(args["utility_cost"])
        else:
            args["utility"] = ProjectUtilitiesConstant.objects.get(id=args["utility"])
            cost = CostCalculationTools.calculateAnualCost(float(args["duty"]), args["utility"].value, args["duty_unity"], "GJ",)
            args["annual_cost"] = cost
            args["utility_cost"] = float(args["utility"].value)
            args.pop('utype', None)

        args["duty"] = float(args["duty"])
        args["cost_unity"] = EquipmentUnity.objects.filter(unity="GJ").first()
        args["equipment"] = equipment
        if not utilities:
            equipment = EquipmentsUtilitiesSetting(**args)
            equipment.save()
        else:
            utilities.update(**args)


    def updateCut(self):
        equipments = EquipmentsUtilitiesSetting.objects.filter(equipment__project=self.project).all()
        opex = Opex.objects.filter(project=self.project).first()
        opex.cut = equipments.aggregate(Sum('utility_cost'))["utility_cost__sum"]
        opex.save()
        pass

# Classe a ser chamada sempre que houver atualização dos custos
class EconomicConfig():
    def __init__(self, project: CapexProject):
        self.project = project
        self.setAuxiliarFactor(project)

    # Atualiza as configurações do projeto
    def updateConfig(self, data):
        config = AuxiliarFactor.objects.filter(project=self.project)
        config.update(**data)
        ManufactoryCost(self.project).updateAllCosts()
        return config

    # Config criada automaticamente na criação do projeto usa valores default
    def setAuxiliarFactorsDefault(self):
        factors = AuxiliarFactor()
        factors.project = self.project
        factors.save()
        return factors

    def setProjectSettingsDefautl(self):
        settings = OpexProjectSettings()
        settings.project = self.project
        settings.capex_source = 'total_langfactor'
        settings.save()

    def setOpexDefault(self):
        opex = Opex()
        opex.project = self.project
        opex.save()

    def setUtilitiesConstantsDefault(self):
        unity = EquipmentUnity.objects.filter(unity="$/GJ").first()

        for v in DefaultConstants().initialUtilitiesConstans:
            if v["unity"]:
                if v["unity"] == "$/GJ":
                    v["unity"] = unity
                else:
                    v["unity"] = EquipmentUnity.objects.filter(unity=v["unity"]).first()
            else:
                v.pop('unity')
            p = ProjectUtilitiesConstant(**v)
            p.project = self.project
            p.save()

    def updateAllOpexValues(self):
        ManufactoryCost(self.project).updateAllCosts()

    # Busca e Define as variáveis auxiliares dentro da instância da classe
    def setAuxiliarFactor(self, project):
        self.factors = AuxiliarFactor.objects.filter(project=project).first()

    # Retorna os valores de variáveis auxiliares
    def getConfig(self, project=None):
        if project is not None:
            self.setAuxiliarFactor(project)
            return self.factors
        elif self.factors:
            return self.factors
        else:
            return None


class CostCalculationTools():

    def __init__(self):
        pass

    # apenas juros compostos no momento
    def pmt(tax, n):
        return (tax * ((tax + 1) ** n)) / (((1 + tax) ** n) - 1)

    def costInYear(project, flow, price, flowConversor=1, priceConversor=1):
        """
        ATENTION: all unitys must be already converted and flow must be in HOUR unity
        if can't be done, optional conversor [flowConversor and price Conversor] can
        be set on arguments.
        """
        hourPrice = (flow * flowConversor) * (price * priceConversor)
        hourYear = ProjectUtilitiesConstant.objects.filter(aka="Hours in Year", project=project).first()
        return (hourPrice * hourYear)

    def convertToDefaultUnity(value: float, unity: EquipmentUnity):
        defaultUnity = EquipmentUnity.objects.filter(dimension=unity.dimension, is_default=True).first()
        return ((defaultUnity.convert_factor) / (unity.convert_factor))

    def convertToDesiredUnit(value: float, unity: EquipmentUnity, desired: str):
        # timeWorked = ProjectUtilitiesConstant.objects.filter(aka="Hours in Year").first()
        defaultPressureFactor = EquipmentUnity.objects.filter(unity=desired).first()
        conversor = (defaultPressureFactor.convert_factor) / (unity.convert_factor)
        converted = conversor * value
        return (converted)

    def convertEnergyUnity(self, unity: EquipmentUnity, reference: str, value: float):
        defaultPressureFactor = EquipmentUnity.objects.filter(unity=reference).first()

        return ((defaultPressureFactor.convert_factor) / (unity.convert_factor))

        pass

    def calculateCost(self, duty: float, utility_cost: float, duty_unity: EquipmentUnity):
        timeWorked = ProjectUtilitiesConstant.objects.filter(aka="Hours in Year").first()
        valueInGJ = CostCalculationTools.convertEnergyUnity(duty_unity, "GJ", duty)
        return (float(valueInGJ) * float(utility_cost) * (timeWorked.value))

    def calculateAnualCost(value: float, cost_unity: float, value_unity: EquipmentUnity, valueHourUnity='unecessary'):
        """
        value: unit module.
        cost_unity: cost in ($/und)
        value_unit: value unity. Must be a Equipmentunity instance
        hourUnity: default is the value is already converted. Otherwise, fill with the hour base unit(Ex.: 'GJ')
        """

        hourBaseValue = value

        if valueHourUnity != "unecessary":
            hourBaseValue = CostCalculationTools.convertToDesiredUnit(float(value), value_unity, valueHourUnity)

        timeWorked = ProjectUtilitiesConstant.objects.filter(aka="Hours in Year").first()

        cost = float(hourBaseValue) * float(cost_unity) * (timeWorked.value)
        return (cost)
