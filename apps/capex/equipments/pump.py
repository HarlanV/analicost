# from capex.models import BareModule, Equipment, PurchasedFactor, EquipmentUnity
import json
from opex.models import EquipmentsUtilitiesSetting, ProjectUtilitiesConstant
from capex.models import BareModule, Dimension, EquipmentUnity, MaterialFactor, PressureFactor, PurchasedFactor
from capex.equipments.equipments import BaseEquipment, teste_print


class Pump(BaseEquipment):

    def __init__(self, equipment_id: int, args: dict):
        # 1. Configuração das variáveis
        # 1.1 Busca as informações do equipamento
        self.configEquipmentConstants(id=equipment_id)

        # 1.2 Recebe os dados do formulário em constantes
        self.setIndividualConstants(equipment_id, args)

        # 1.3 Configura os valores para calculo do custo base
        self.config_purchase_constants(equipment_id, self.type)
        self.name = self.equipment.name

    # Busca e configura as contantes de custo do equipamento
    def config_purchase_constants(self, id, type):
        constants = PurchasedFactor.objects.filter(equipment_id=id, description=type, material=self.moc).first()
        self.referenceEquipmentId = PurchasedFactor.objects.filter(equipment_id=id, description=type, is_reference=True).first()

        self.set_purchase_constants(type, constants)

    # Função para atribuição de variáveis
    def setIndividualConstants(self, equipment_id: int, args: dict):
        self.defaultUnity = EquipmentUnity.objects.filter(dimension=self.equipment.dimension, is_default=True).first()
        self.type = args["type"]
        self.moc = args["moc"]
        self.pressure = 0
        self.spares = 0
        if "pressure" in args:
            self.pressure = (float(args["pressure"]))
        if "cepci" in args:
            self.cepci = args["cepci"]
        if "equipment_attribute" in args:
            self.specification = float(args["equipment_attribute"])
        if ("spares" in args and args["spares"] != ""):
            self.spares = int(args["spares"])
        if "attribute_dimension" in args:
            self.selectedUnity = EquipmentUnity.objects.filter(id=args["attribute_dimension"]).first()
            self.conversor = (self.defaultUnity.convert_factor) / (self.selectedUnity.convert_factor)
        if "pressure_unity" in args:
            self.pressureUnity = EquipmentUnity.objects.filter(id=args["pressure_unity"]).first()
            defaultPressureFactor = EquipmentUnity.objects.filter(unity="barg").first()
            self.pressureConversor = (defaultPressureFactor.convert_factor) / (self.pressureUnity.convert_factor)

    def bareModuleFactor(self, referenceId=False):
        if referenceId is False:
            fbm = self.roughFbm(self.purchase_id)
        else:
            fbm = self.roughFbm(self.referenceEquipmentId.id)
        return fbm

    # Calculo dos custos totais, incluindo o Bare Module
    def setCosts(self):

        self.pressureFactor = 1
        if self.pressure * self.pressureConversor > 10:
            self.pressureFactor = self.pressureFactorCalc(self.pressure * self.pressureConversor)

        self.baseCost = (self.baseCost * self.cepci) / self.reference_cepci

        # Para CS
        self.reference = self.bareModuleFactor(True)

        # Fator BareMobule
        # Arredonda valores
        # fbm nas condições básicas (Fp e Fm unitários)
        fbm0 = self.baseRoughFbm(self.purchase_id)

        # Arredonda valores
        self.purchasedEquipmentCost = self.upRound(self.baseCost * self.fM * self.pressureFactor)
        self.bareModuleCost = self.upRound(self.baseCost * self.bareModuleFactor())
        self.baseEquipmentCost = self.upRound(self.baseCost)
        self.baseBaremoduleCost = self.upRound(self.baseCost * fbm0)

    def setUtilitiesField(self, equipment):

        efficiency = 0.86
        costUtility = ProjectUtilitiesConstant.objects.filter(aka="Eletricity").first()
        duty = (self.specification * self.conversor) / efficiency
        utility = EquipmentsUtilitiesSetting()
        utility.equipment = equipment
        utility.utility = costUtility
        utility.efficiency = efficiency
        utility.duty = duty
        utility.duty_unity = self.selectedUnity
        # Considereando o default em kW
        utility.annual_cost = self.calculateAnnualCut(duty, costUtility)
        utility.save()

    def calculateAnnualCut(self, duty, costUtility, cost_unity="GJ"):
        timeWorked = ProjectUtilitiesConstant.objects.filter(aka="Hours in Year").first()
        GJConversor = EquipmentUnity.objects.filter(unity=cost_unity).first().convert_factor
        valueInGJ = duty * GJConversor
        annual_cost = ((valueInGJ) * float(costUtility.value) * float(timeWorked.value))
        return annual_cost


class sketch(Pump):

    def __init__(self, equipment_id: int, args: dict):
        super().__init__(equipment_id, args)


class FobCost(Pump):
    def __init__(self, equipment_id: int, args: dict):
        super().__init__(equipment_id, args)
        # 2. Calculos de Custo
        # 2.1 Calcula preço de compra base (fob)
        self.baseCostCalculate(self.specification * self.conversor)


class EquipmentCosts(FobCost):
    def __init__(self, equipment_id: int, args: dict):
        super().__init__(equipment_id, args)
        self.setCosts()


class EquipmentComplementData():
    def __init__(self, q, equipment):
        self.equipmentForm = {}
        self.equipment = equipment
        self.equipmentForm["equipment"] = equipment
        self.q = q
        pass

    def form(self):
        self.equipmentForm["types"] = self.q.values('description').distinct()
        self.equipmentForm["dimension"] = self.equipment.dimension
        self.equipmentForm["unitys"] = EquipmentUnity.objects.filter(dimension=self.equipment.dimension)
        self.equipmentForm["materials"] = self.q.values('material').distinct()
        pressureDimension = Dimension.objects.get(dimension="Pressure")
        self.equipmentForm["pressureUnity"] = EquipmentUnity.objects.filter(dimension=pressureDimension)
        typesList = list(self.equipmentForm["types"].values_list("id", flat=True))
        self.equipmentForm["pressureLimits"] = list(PressureFactor.objects.filter(equipment__in=typesList).values_list("equipment_id", "pressure_min", "pressure_max"))
        mf = MaterialFactor.objects.filter(equipment__in=typesList).values_list("equipment__description", "material")
        export = []
        aux = []
        for t in self.equipmentForm["types"]:
            aux.append(t["description"])
            for k, v in mf:
                if k == t["description"]:
                    aux.append(v)

            export.append(tuple(aux))
            aux = []

        self.equipmentForm["typesAndMaterials"] = json.dumps(export)

        self.equipmentForm["typesSubtitle"] = list(self.q.values_list('description', 'id', 'material'))
        material = list(self.equipmentForm["materials"].values_list("material", flat=True))
        types = list(self.equipmentForm["types"].values_list("description", flat=True))
        self.equipmentForm["auxiliarLists"] = [material, types]
        self.equipmentForm["conversores"] = dict(EquipmentUnity.objects.filter(dimension__dimension="Pressure").values_list("unity", "convert_factor"))

        return self.equipmentForm
