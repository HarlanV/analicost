# from capex.models import BareModule, Equipment, PurchasedFactor, EquipmentUnity
from capex.models import BareModule, EquipmentUnity, PurchasedFactor
from capex.equipments.equipments import BaseEquipment, teste_print


class HeatExchanger(BaseEquipment):

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
        if self.moc is not None:
            constants = PurchasedFactor.objects.filter(equipment_id=id, description=type, material=self.moc).first()
            refId = PurchasedFactor.objects.filter(equipment_id=id, description=type, is_reference=True).first().id
            self.reference = BareModule.objects.filter(equipment_id=refId).first().fbm
        else:
            self.reference = 1
            constants = PurchasedFactor.objects.filter(equipment_id=id, description=type).first()
        self.set_purchase_constants(type, constants)

    # Função para atribuição de variáveis
    def setIndividualConstants(self, equipment_id: int, args: dict):
        # Verificar possibilidade de personalizar
        self.defaultUnity = EquipmentUnity.objects.filter(dimension=self.equipment.dimension, is_default=True).first()
        self.type = args["type"]
        self.moc = None
        self.pressure = None
        if "cepci" in args:
            self.cepci = args["cepci"]

        if "equipment_attribute" in args:
            self.specification = float(args["equipment_attribute"])
        if ("spares" in args and args["spares"] != ""):
            self.spares = int(args["spares"])
        else:
            self.spares = 0
        if "attribute_dimension" in args:
            self.selectedUnity = EquipmentUnity.objects.filter(id=args["attribute_dimension"]).first()
            self.conversor = (self.defaultUnity.convert_factor) / (self.selectedUnity.convert_factor)

    def config_purchase_constants(self, id, type):
        self.reference = 1
        constants = PurchasedFactor.objects.filter(equipment_id=id, description=type).first()
        self.set_purchase_constants(type, constants)

    # Calculo dos custos totais, incluindo o Bare Module
    def setCosts(self):

        # pressureFactor = self.pressureFactorCalc(self.pressure)
        pressureFactor = 1
        self.baseCost = (self.baseCost * self.cepci) / self.reference_cepci

        # Fator BareMobule
        bareModuleCost = self.baseCost * self.bareModuleFactor() * pressureFactor

        # Arredonda valores
        # Blender
        self.purchasedEquipmentCost = self.upRound(self.baseCost * self.reference)     # 1 trocado
        self.bareModuleCost = self.upRound(bareModuleCost)                             # 2 ok
        self.baseEquipmentCost = self.upRound(self.baseCost)                           # 3 ok
        self.baseBaremoduleCost = self.upRound(bareModuleCost / self.reference)        # 4 trocado


class sketch(HeatExchanger):

    def __init__(self, equipment_id: int, args: dict):
        super().__init__(equipment_id, args)


class FobCost(HeatExchanger):
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
        return self.equipmentForm


class FormData():

    def __init__(self):
        self.data = {}

    def validate():
        pass
