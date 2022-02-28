from queue import Empty
from capex.models import BareModule, Equipment, MaterialFactor, PressureFactor
from capex.models import EquipmentProject
import math


class BaseEquipment():

    def __init__(self):
        return

    # [ok] Retona as constante de custo do equipamento
    def configEquipmentConstants(self, id):
        self.equipment = Equipment.objects.get(id=id)
        return self.equipment

    # [ok] Seta as variáveis para calculo do custo de compra
    def set_purchase_constants(self, type, constants):
        self.k1 = constants.k1
        self.k2 = constants.k2
        self.k3 = constants.k3
        self.maxAttribute = constants.max_dimension
        self.minAttribute = constants.min_dimension
        self.type = type
        self.reference_cepci = constants.cepci
        self.purchase_id = constants.id
        self.purchase_obj = constants

    # [ok] Função para calculo do valor de compra pela função logarítimica {encapsular}
    def baseCostCalculate(self, E: float):
        """
        Função recebe um valor de especificação E (área, volume, etc) e calcula
        o custo de compra básico (sem B.M.)
        """
        aux1 = self.k2 * math.log10(E)
        aux2 = self.k3 * (math.log10(E)**2)
        price = (10 ** (self.k1 + aux1 + aux2)) * (self.spares + 1)
        self.baseCost = price
        return price

    # [ok] Rettornas os custos do Bare Module
    def get_equipment_price(self):
        """
        Função retorna um dicionário com os custos calculo Bare Module
        """
        prices = {
            'Base Coast': round(self.baseCost),
            'Bare Module Cost': round(self.bareModule)
        }
        return prices

    # [ok] Função retorna/calcula o Fbm
    def bareModuleFactor(self):
        fbm = BareModule.objects.filter(equipment_id=self.purchase_id).first().fbm
        return fbm

    def roughFbm(self, equip_id):
        materialFactors = MaterialFactor.objects.filter(equipment_id=equip_id).first()
        self.b1 = materialFactors.b1
        self.b2 = materialFactors.b2
        self.fM = materialFactors.fm
        fbm = (self.b1 + (self.b2 * self.fM * self.pressureFactor))
        return fbm

    def baseRoughFbm(self, equip_id):
        b1 = self.b1
        b2 = self.b2
        fM = 1
        fP = 1
        fbm = (b1 + (b2 * fM * fP))
        return fbm

    # [ok] Calculo do fator de pressão
    def pressureFactorCalc(self, pressure):
        const = PressureFactor.objects.filter(equipment=self.purchase_id).first()
        aux1 = const.c1
        aux2 = const.c2 * (math.log10(pressure))
        aux3 = const.c3 * (math.log10(pressure)**2)
        pressureFactor = 10 ** (aux1 + aux2 + aux3)

        return pressureFactor

    # [ok] Função auxiliar para arredondamento de valor significativo. Regra de capex no CAPCOST {encapsular}
    def upRound(self, value):
        """
        função auxiliar aproxima value para o mais proximo do multiplo de (10^digits)
        """
        rounded = round(value)
        if (rounded < 1):
            digits = -3
        else:
            digits = -(3 - len(str(round(value))))

        rounded = (round((value / (10**digits))) * (10**digits))
        return rounded

    # [ok] Insere os dados já calculados no projeto
    def insertIntoProject(self, project):
        args = {
            'purchased_factor': self.purchase_obj,
            'equipment_code': self.findsEquipmentCode(project.projectNum),
            'purchased_equip_cost': self.purchasedEquipmentCost,
            'baremodule_cost': self.bareModuleCost,
            'base_equipment_cost': self.baseEquipmentCost,
            'base_baremodule_cost': self.baseBaremoduleCost,
            'equipment': self.equipment,
            'spares': self.spares,
            'specification': self.specification,
            'preference_unity': self.selectedUnity
        }

        # Nem todos os equipamentos possuem pressão. Campo nulable

        try:
            if self.pressure is not None:
                args["pressure"] = self.pressure
                args["pressureunity"] = self.pressureUnity
        except AttributeError:
            pass

        equipment = project.insertEquipment(args)

        equipment = project.updateCosts()

        return equipment

    # [ok] Atualiza os dados já calculados no projeto
    def updateInProject(self, project, equipmentProject):

        # equipment code não é alterável (Regra de negócio até o momento)
        args = {
            'purchased_factor': self.purchase_obj,
            'equipment_code': equipmentProject.equipment_code,
            'purchased_equip_cost': self.purchasedEquipmentCost,
            'baremodule_cost': self.bareModuleCost,
            'base_equipment_cost': self.baseEquipmentCost,
            'base_baremodule_cost': self.baseBaremoduleCost,
            'equipment': self.equipment,
            'spares': self.spares,
            'specification': self.specification,
            'preference_unity': self.selectedUnity
        }

        try:
            if self.pressure is not None:
                args["pressure"] = self.pressure
                args["pressureunity"] = self.pressureUnity
        except AttributeError:
            pass

        equipment = project.updateEquipment(args, equipmentProject)
        equipment = project.updateCosts()
        return equipment

    # [ok] Função auxiliar para criar o código de Projeto do Equipamento {encapsular}
    def findsEquipmentCode(self, numProject):
        equipmentLetter = self.equipment.symbol
        initial = equipmentLetter + (str(numProject)[:1])
        query = EquipmentProject.objects.filter(equipment_code__contains=initial)
        code = equipmentLetter + str(numProject + query.count() + 1)
        return code


def teste_print(dados):
    print('--------------------------------------')
    print('--------------------------------------')
    print(dados)
    print('--------------------------------------')
    print('--------------------------------------')
