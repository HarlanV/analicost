# from capex.models import BareModule, Equipment, PurchasedFactor, EquipmentUnity
from capex.models import BareModule, Dimension, EquipmentUnity, PressureFactor, PurchasedFactor
from capex.equipments.equipments import BaseEquipment, teste_print


class Vaporizer(BaseEquipment):

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
        refId = PurchasedFactor.objects.filter(equipment_id=id, description=type, is_reference=True).first().id
        self.reference = BareModule.objects.filter(equipment_id=refId).first().fbm
        self.set_purchase_constants(type, constants)

    # Função para atribuição de variáveis
    def setIndividualConstants(self, equipment_id: int, args: dict):
        # Verificar possibilidade de personalizar
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
            self.defaultPressure = EquipmentUnity.objects.filter(unity="barg").first()
            self.pressureConversor = (self.defaultPressure.convert_factor) / (self.pressureUnity.convert_factor)

    # Calculo dos custos totais, incluindo o Bare Module
    def setCosts(self):
        # pressureFactor = self.pressureFactorCalc(self.pressure)
        # Para valores de pressão < 0, o valor do fator é aproximadamente 1 constante
        pressureFactor = 1

        if self.pressure * self.pressureConversor > 10:
            pressureFactor = self.pressureFactorCalc(self.pressure * self.pressureConversor)

        self.pressureFactor = pressureFactor
        self.baseCost = (self.baseCost * self.cepci) / self.reference_cepci

        # Fator BareMobule
        bareModuleCost = self.baseCost * self.bareModuleFactor() * pressureFactor

        # Arredonda valores
        self.purchasedEquipmentCost = self.upRound(bareModuleCost / self.reference)
        self.bareModuleCost = self.upRound(bareModuleCost)
        self.baseEquipmentCost = self.upRound(self.baseCost)
        self.baseBaremoduleCost = self.upRound(self.baseCost * self.reference)


class sketch(Vaporizer):

    def __init__(self, equipment_id: int, args: dict):
        super().__init__(equipment_id, args)


class FobCost(Vaporizer):
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
        pressureDimension = Dimension.objects.get(dimension="Pressão")
        self.equipmentForm["pressureUnity"] = EquipmentUnity.objects.filter(dimension=pressureDimension)
        typesList = list(self.equipmentForm["types"].values_list("id", flat=True))
        self.equipmentForm["pressureLimits"] = list(PressureFactor.objects.filter(equipment__in=typesList).values_list("equipment_id", "pressure_min", "pressure_max"))
        self.equipmentForm["typesSubtitle"] = list(self.q.values_list('description', 'id', 'material'))
        material = list(self.equipmentForm["materials"].values_list("material", flat=True))
        types = list(self.equipmentForm["types"].values_list("description", flat=True))
        self.equipmentForm["auxiliarLists"] = [material, types]
        self.equipmentForm["conversores"] = dict(EquipmentUnity.objects.filter(dimension__dimension="Pressão").values_list("unity", "convert_factor"))
        return self.equipmentForm


class FormData():

    def __init__(self):
        self.data = {}

    def validate():
        pass
