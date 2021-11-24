from equipamentos.models import EquipmentUnity
from .models import BareModule, Equipment, PressureFactor, PurchasedFactor
from capitalcost.models import CapexProject, EquipmentProject
import math
from django.db.models import Q


class EquipmentCost():

    def __init__(self, equipment_id: int, args: dict, allCosts=False, noCost=False):
        """
        kwargs: (equipment_id, contants, allCosts)
        """

        self.equipment = Equipment.objects.filter(id=equipment_id).first()
        self.defaultUnity = EquipmentUnity.objects.filter(dimension=self.equipment.dimension, is_default=True).first()
        self.setIndividualConstants(equipment_id, args)
        self.set_purchase_constants(equipment_id, self.type)
        self.name = self.equipment.name
        
        # (TODO: CONFIRMAR SE É NECESSÁRIO AINDA ESSA VARIÁVEL ARGS)
        self.args = args

        # Caso queira apenas as informações das contantes, sem calcular custos
        if noCost is True:
            return


        # Calcula preço de compra (sem BareModule)
        self.baseCostCalculate(self.specification * self.conversor)

        # Caso queria ser calculado todos os custos [PENSAR SE DEVE SER EXTRAÍDO DEPOIS]
        if allCosts is True:
            self.setCosts()

    # Função para atribuição de variáveis
    def setIndividualConstants(self, equipment_id: int, args: dict):
        self.type = args["type"]

        if "moc" in args:
            args["pressure"] = 100
            self.moc = args["moc"]
        else:
            self.moc = None
        if "pressure" in args:
            self.pressure = (float(args["pressure"]))
        else:
            self.pressure = None
        if "cepci" in args:
            self.cepci = args["cepci"]
        if "equipment_attribute" in args:
            self.specification = float(args["equipment_attribute"])
        if "spares" in args:
            self.spares = int(args["spares"])
        else:
            self.spares = 0
        if "attribute_dimension" in args:
            self.selectedUnity = EquipmentUnity.objects.filter(id=args["attribute_dimension"]).first()
            self.conversor = (self.defaultUnity.convert_factor) / (self.selectedUnity.convert_factor)

    def set_purchase_constants(self, id, type):
        if self.moc is not None:
            constants = PurchasedFactor.objects.filter(equipment_id=id, description=type, material=self.moc).first()
            refId = PurchasedFactor.objects.filter(equipment_id=id, description=type, is_reference=True).first().id
            self.reference = BareModule.objects.filter(equipment_id=refId).first().fbm
        else:
            self.reference = 1
            constants = PurchasedFactor.objects.filter(equipment_id=id, description=type).first()
        self.k1 = constants.k1
        self.k2 = constants.k2
        self.k3 = constants.k3
        self.maxAttribute = constants.max_dimension
        self.minAttribute = constants.min_dimension
        self.type = type
        self.reference_cepci = constants.cepci
        self.purchase_id = constants.id
        self.purchase_obj = constants

    # Função para calculo do valor de compra pela função logarítimica {encapsular}
    def baseCostCalculate(self, E: float):
        """
        Função recebe um valor de especificação E (área, volume, etc) e calcula
        o custo de compra básico (sem B.M.)
        """

        aux1 = self.k2 * math.log10(E)
        aux2 = self.k3 * (math.log10(E)**2) 
        
        price = (10 ** (self.k1 + aux1 + aux2)) * (self.spares + 1)
        # self.teste_print(price)
        # teste = str(self.k1) + "//" + str(self.k2) + "//" + str(self.k3) + "//" + str(E)
        teste = str(aux1) + "//" + str(aux2) + "//" + str(self.k1) + "//" + str(price)
        self.teste_print(teste)
        self.baseCost = price
        return price

    def get_equipment_price(self):
        """
        Função retorna um dicionário com os custos calculo Bare Module
        """
        prices = {
            'Base Coast': round(self.baseCost),
            'Bare Module Cost': round(self.bareModule)
        }
        return prices

    # Função retorna ou calcula o Fbm
    def bareModuleFactor(self):
        fbm = BareModule.objects.filter(equipment_id=self.purchase_id).first().fbm
        return fbm

    def pressureFactorCalc(self, pressure):
        const = PressureFactor.objects.filter(equipment_id=self.purchase_id).first()
        aux1 = const.c1
        aux2 = const.c2 * (math.log10(pressure))
        aux3 = const.c3 * (math.log10(pressure)**2)

        pressureFactor = 10 ** (aux1 + aux2 + aux3)
        return pressureFactor

    def setCosts(self):

        if self.pressure is not None:
            pressureFactor = self.pressureFactorCalc(self.pressure)
            method = 2
        else:
            pressureFactor = 1
            method = 1
        self.original_cost = self.baseCost
        self.baseCost = (self.baseCost * self.cepci) / self.reference_cepci
        # teste = self.baseCost
        # self.teste_print(teste)
        # Fator BareMobule

        bareModuleCost = self.baseCost * self.bareModuleFactor() * pressureFactor
        cP = bareModuleCost / self.reference

        # Arredonda valores

        # Aqui nós temos uma diferença nos métodos comparados com o Blender e Evaporador.
        # Esse Method é temporário até entender melhor se há um erro no calculo
        if method == 2:
            # Evaporator
            self.purchasedEquipmentCost = self.upRound(bareModuleCost / self.reference)    # 1 trocado
            self.bareModuleCost = self.upRound(bareModuleCost)                             # 2 ok
            self.baseEquipmentCost = self.upRound(self.baseCost)                           # 3 ok
            self.baseBaremoduleCost = self.upRound(self.baseCost * self.reference)         # 4 trocado
        else:
            # Blender
            self.purchasedEquipmentCost = self.upRound(self.baseCost * self.reference)     # 1 trocado
            self.bareModuleCost = self.upRound(bareModuleCost)                             # 2 ok
            self.baseEquipmentCost = self.upRound(self.baseCost)                           # 3 ok
            self.baseBaremoduleCost = self.upRound(bareModuleCost / self.reference)        # 4 trocado

            # t1 = self.purchasedEquipmentCost
            # t2 = self.bareModuleCost
            # t3 = self.baseEquipmentCost
            # t4 = self.baseBaremoduleCost
            # teste = str(t1) + "//" + str(t2) + "//" + str(t3) + "//" + str(t4)
            # self.teste_print(teste)

    def teste_print(self, dados):
        print('--------------------------------------')
        print('--------------------------------------')
        print(dados)
        print('--------------------------------------')
        print('--------------------------------------')

    # Função auxiliar para arredondamento de valor significativo. Regra de Turton no CAPCOST {encapsular}
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

        if self.pressure is not None:
            args["pressure"] = self.pressure

        equipment = project.insertEquipment(args)

        equipment = project.updateCosts()

        return equipment

    # Função auxiliar para criar o código de Projeto do Equipamento {encapsular}
    def findsEquipmentCode(self, numProject):
        equipmentLetter = self.equipment.symbol
        initial = equipmentLetter + (str(numProject)[:1])
        query = EquipmentProject.objects.filter(equipment_code__contains=initial)
        code = equipmentLetter + str(numProject + query.count() + 1)
        return code


class ProjectCost():
    """
    Attributes: projectNum, project, equipments
    """

    def __init__(self, num, noCreate=False):

        hasProject = self.checkProject(num)
        if noCreate is False and hasProject is False:
            self.createProject(num)
        else:
            self.setProject(num)
            self.equipments = self.listEquipmentsProject()

    def setProject(self, num, project=None):
        if project:
            self.projectNum = num
            self.project = project
        else:
            self.projectNum = num
            self.project = self.getProject(num)

    def getProject(self, num):
        project = CapexProject.objects.filter(project_number=num).first()
        return project

    def project(self):
        return self.project

    def createProject(self, num):
        project = CapexProject(project_number=num)
        project.save()
        self.setProject(num, project)
        return project

    def insertEquipment(self, data):
        data['project'] = self.project
        equipment = EquipmentProject(**data)
        equipment.save()
        self.equipments = self.listEquipmentsProject()
        return equipment

    def updateCosts(self):

        project = self.project

        # listEquipments = self.listEquipmentsProject()
        listEquipments = self.equipments
        equipment_code = 0
        purchased_equip_cost = 0
        baremodule_cost = 0
        base_equipment_cost = 0
        base_baremodule_cost = 0

        for equipment in listEquipments:
            purchased_equip_cost += equipment.purchased_equip_cost
            baremodule_cost += equipment.baremodule_cost
            base_equipment_cost += equipment.base_equipment_cost
            base_baremodule_cost += equipment.base_baremodule_cost

        project.equipment_code = equipment_code
        project.purchased_equip_cost = purchased_equip_cost
        project.baremodule_cost = baremodule_cost
        project.base_equipment_cost = base_equipment_cost
        project.base_baremodule_cost = base_baremodule_cost

        total_module_cost = self.upRound(baremodule_cost * 1.18)
        project.total_module_cost = total_module_cost
        project.total_grassroot_cost = total_module_cost + self.upRound(0.5 * base_baremodule_cost)
        project.total_equipment_cost = purchased_equip_cost
        project.total_langfactor = project.lang_factor * purchased_equip_cost
        project.save()
        self.project = project

    def teste_print(self, dados):
        print('--------------------------------------')
        print('--------------------------------------')
        print(dados)
        print('--------------------------------------')
        print('--------------------------------------')

    def listEquipmentsProject(self):
        self.equipments = EquipmentProject.objects.filter(project=self.project)
        listDistinctEquipment = (EquipmentProject.objects.filter(project=self.project).values('equipment__name').distinct())
        self.listDistinctEquipment = list(map(lambda x: x["equipment__name"], listDistinctEquipment))
        # self.unique_equipments = EquipmentProject.objects.filter(project=self.project).values('description').distinct()
        return self.equipments

    def upRound(self, value):
        if (value < 1):
            digits = 3
        else:
            digits = 3 - len(str(round(value)))

        return (round((value / (10**digits))) * (10**digits))

    def checkProject(self, num):
        project = self.getProject(num)
        self.setProject(100, project)
        if project:
            return True
        else:
            return False

    def renumerar(self, symbol):
        num = self.projectNum
        equipmentLetter = symbol
        initial = equipmentLetter + (str(num)[:1])
        it = 0
        for e in EquipmentProject.objects.filter(equipment_code__contains=initial):
            code = equipmentLetter + str(num + it + 1)
            e.equipment_code = code
            e.save()
            it += 1

        return (equipmentLetter + str(num + it + 1))

    def removeEquipment(self, equipment_id):
        equipment = EquipmentProject.objects.filter(id=equipment_id)
        symbol = equipment.first().equipment.symbol
        delete = equipment.delete()
        self.updateCosts()
        self.renumerar(symbol)

        if delete[0] >= 1:
            return True
        else:
            return False

    def removeProject(self):
        delete = self.project.delete()

        if delete[0] >= 1:
            return True
        else:
            return False
