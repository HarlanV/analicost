from capex.equipments.equipments import teste_print
from capex.models import CapexProject, EquipmentUnity
from .models import Opex, OpexAuxiliateFactor as AuxiliarFactor, OpexProjectSettings, ProjectUtilitiesConstant, initialUtilitiesConstans


class ManufactoryCost():

    def __init__(self, project: CapexProject):
        self.project = project
        configs = EconomicConfig(project)
        self.factorss = configs.getConfig()
        # capex = self.factor.capex_source

    # apenas juros compostos no momento
    def pmt(tax, n):
        return (tax * ((tax + 1) ** n)) / (((1 + tax) ** n) - 1)

    def updateAllCosts(self):
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

        for v in initialUtilitiesConstans:
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


class CashFlow():
    def __init__(self):
        pass

    def getCashFlow():
        pass

    def setCashFlow():
        pass


# Custos de Utilidade (CUT)
class UtilityCosts(ManufactoryCost):

    def __init__(self):
        # esses valores devem ser calculados anteriormente em uma classe mãe
        # TODO: criar classe mãe. Herança para calcular os atributos definidos abaixo
        self.crm = 1
        self.cwt = 1
        self.cut = 1
        self.col = 1
        self.com = 1
        self.fci = 1
        individualFactors = {

        }

    def totalDirectCosts(self, individual=False):
        if not individual:
            cost = self.crm + self.cwt + self.cut
            cost = cost + (1.33 * self.col) + (0.03 * self.com) + (0.069 * self.fci)

    # lista de atributos que devem ser definidos individualmente
    def setIndividualFactors(self):
        pass

    def supervisionaryClericalWorker(self):
        pass


# Custos de Capital de Giro
class WorkingCapitalCost(ManufactoryCost):
    pass


# Custos de Mão de Obra (COL)
class OperatingLaborCost(ManufactoryCost):
    pass


# Custos de Resíduos (CWT)
class WasteTreatmentCost(ManufactoryCost):
    pass


# class Opex():
#     def __init__(self, project):
#         self.project = project
#         self.cwt = WasteTreatmentCost()
#         self.col = OperatingLaborCost()
#         self.cut = UtilityCosts()
#         self.fci = self.getCapex()
#         self.factors = AuxiliarFactor.objects.filter(project=project).first()
# 
#     def getCapex(self):
#         source = self.factors.capex_source
#         if source == 'input_source':
#             pass
#         else:
#             project = CapexProject.objects.filter(id=self.project).first()
#             capex = project[source]
#         return capex
